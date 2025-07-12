from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, Security, status

from app.database import MongoDBConnectionManager
from app.config import ACCESS_TOKEN_DURATION_MINUTES
from app.auth import (
    User,
    Token,
    UserInDB,
    UserCreate,
    get_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
    current_active_user,
)


routes = APIRouter()


@routes.post("/token", response_model=Token, tags=["Users and Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    """Validate user logins and returns a JWT.

    Parameters
    ----------
    username: str

    password: str

    email: Optional(str)

    full_name: Optional(str)

    Returns
    -------
    str
        JSON Web Token with expiration on 30 minutes.

    """

    async with MongoDBConnectionManager() as db:
        user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    for scope in form_data.scopes:
        if scope not in user.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes or user.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@routes.post("/user/", tags=["Users and Authentication"])
async def create_user(
    user: UserCreate,
    _: User = Security(current_active_user, scopes=["user.create"]),
) -> None:
    """Allows to an authenticated user to create an user.

    Parameters
    ----------
    username: str

    password: str

    email: Optional(str)

    full_name: Optional(str)

    disabled: Optional(bool) = False

    password: str

    """

    async with MongoDBConnectionManager() as db:
        user_exists = await get_user(db, user.username)
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not created"
            )

        if user.roles:
            roles = await db.roles.find({"name": {"$in": user.roles}}).to_list(None)
            if len(roles) != len(user.roles):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid roles")

        hashed_password = get_password_hash(user.password)
        await db.users.insert_one(
            UserInDB(**user.model_dump(), hashed_password=hashed_password).model_dump()
        )

    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="User created")


@routes.get("/user/{name}/", response_model=User, tags=["Users and Authentication"])
async def get_user_by_username(
    name: str,
    current_user: User = Security(current_active_user, scopes=["user.me"]),
) -> User:
    """Returns basic info of the given user.

    Parameters
    ----------
    name: str

    """

    if "admin" in current_user.scopes or (
        "user.me" in current_user.scopes and current_user.username == name
    ):
        async with MongoDBConnectionManager() as db:
            user = await get_user(db, name)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
            )

        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@routes.put("/user/{name}/", tags=["Users and Authentication"])
async def update_user(
    name: str,
    user: UserCreate,
    current_user: User = Security(current_active_user, scopes=["user.update"]),
) -> None:
    """Update the current user's usersname. Cannot be repeated.

    Parameters
    ----------
    user: str

    user_form: Depends(User)

    """

    if "admin" in current_user.scopes or current_user.username == name:
        hashed_password = get_password_hash(user.password)
        async with MongoDBConnectionManager() as db:
            if user.roles:
                roles = await db.roles.find({"name": {"$in": user.roles}}).to_list(None)
                if len(roles) != len(user.roles):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid roles")
            await db.users.update_one(
                {"username": name},
                {
                    "$set": UserInDB(
                        **user.model_dump(), hashed_password=hashed_password
                    ).model_dump()
                },
            )
        raise HTTPException(status_code=status.HTTP_200_OK, detail="User updated")

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@routes.delete("/user/{name}/", tags=["Users and Authentication"])
async def delete_user(
    name: str,
    current_user: User = Security(current_active_user, scopes=["user.delete"]),
) -> None:
    """Delete the given user if exists.

    Parameters
    ----------
    name: str

        target username to delete

    """

    async with MongoDBConnectionManager() as db:
        if "admin" in current_user.scopes:
            result = await db.users.delete_one({"username": name})

            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
                )

            raise HTTPException(status_code=status.HTTP_200_OK, detail="User deleted")

        if "user.me" in current_user.scopes and current_user.username != name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
            )

        if "user.me" in current_user.scopes and current_user.username == name:
            await db.users.update_one({"username": name}, {"$set": {"disabled": True}})
            raise HTTPException(status_code=status.HTTP_200_OK, detail="User deleted")

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@routes.get("/user/", response_model=list[User], tags=["Users and Authentication"])
async def get_all_users(_: User = Security(current_active_user, scopes=["user.all"])) -> list[User]:
    """Lists all existing users.

    Returns
    -------
    list[User]

        list of all users's info. Passwords not included.

    """

    async with MongoDBConnectionManager() as db:
        users = await db.users.find({}, {"_id": 0, "hashed_password": 0}).to_list(None)
        role_map = {
            r["name"]: r["scopes"]
            for r in await db.roles.find({}, {"_id": 0}).to_list(None)
        }
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    result = []
    for user in users:
        scopes = set(user.get("scopes", []))
        for role_name in user.get("roles", []):
            scopes.update(role_map.get(role_name, []))
        user["scopes"] = list(scopes)
        result.append(User(**user))

    return result
