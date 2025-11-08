from pymongo import UpdateOne
from datetime import datetime, timezone


def default_key_func_factory(key_fields: list[str]):
    def key_func(doc: dict) -> dict:
        filt = {}
        for k in key_fields:
            if k not in doc:
                raise ValueError(f"Missing key field '{k}' in document")
            v = doc[k]
            if v is None:
                raise ValueError(f"Null key field '{k}' in document")
            filt[k] = v
        return filt

    return key_func


async def bulk_upsert(
    db,
    *,
    collection: str,
    rows: list[dict],
    key_fields: list[str] | None = None,
    key_func=None,
    set_on_insert: dict | None = None,
) -> dict:
    if key_func is None:
        if not key_fields:
            raise ValueError("Either key_fields or key_func must be provided.")
        key_func = default_key_func_factory(key_fields)
    now = datetime.now(timezone.utc)
    ops: list[UpdateOne] = []
    for r in rows:
        filt = key_func(r)
        body_set = {**r, "updated_at": now}
        body_set.pop("_id", None)
        body = {"$set": body_set}
        if set_on_insert:
            body["$setOnInsert"] = set_on_insert
        ops.append(UpdateOne(filt, body, upsert=True))
    if not ops:
        return {"matched": 0, "modified": 0, "upserted": 0}
    res = await db[collection].bulk_write(ops, ordered=False)
    return {
        "matched": res.matched_count,
        "modified": res.modified_count,
        "upserted": len(res.upserted_ids) if res.upserted_ids else 0,
    }
