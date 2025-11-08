from bson import ObjectId
from pymongo import UpdateOne
from collections import defaultdict
from datetime import datetime, timezone
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import MongoDBConnectionManager


async def restore_expired_reservations_stock():
    now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    async with MongoDBConnectionManager() as db:
        expired = await db.reservations.find(
            {"status": "PENDING", "expires_at": {"$lt": now_utc_naive}}
        ).to_list(length=None)
        if not expired:
            return {"reservations": 0, "events_updated": 0}

        bulk_ops = [
            UpdateOne(
                {"_id": r["_id"], "status": "PENDING"}, {"$set": {"status": "EXPIRED"}}
            )
            for r in expired
        ]
        await db.reservations.bulk_write(bulk_ops)

        restore_map = defaultdict(lambda: defaultdict(int))
        for r in expired:
            eid = r.get("event_id")
            if not eid:
                continue
            for it in r.get("items", []):
                ttype = it.get("type")
                qty = int(it.get("quantity", 0))
                if ttype and qty > 0:
                    restore_map[eid][ttype] += qty

        events_updated = 0
        for eid, per_type in restore_map.items():
            try:
                event_oid = ObjectId(eid)
            except Exception:
                continue
            event = await db.events.find_one({"_id": event_oid})
            if not event:
                continue

            tickets = event.get("tickets", [])
            type_index = {t["type"]: i for i, t in enumerate(tickets)}
            changed = False
            for ttype, qty in per_type.items():
                if ttype in type_index:
                    idx = type_index[ttype]
                    tickets[idx]["available"] = (
                        int(tickets[idx].get("available", 0)) + qty
                    )
                    changed = True
            if changed:
                await db.events.update_one(
                    {"_id": event["_id"]}, {"$set": {"tickets": tickets}}
                )
                events_updated += 1

        return {"reservations": len(expired), "events_updated": events_updated}


def register_jobs(scheduler: AsyncIOScheduler) -> None:
    scheduler.add_job(
        restore_expired_reservations_stock,
        CronTrigger(minute="*/5"),
        id="restore_expired_reservations_stock",
        replace_existing=True,
    )  # Every 5 minutes
    pass
