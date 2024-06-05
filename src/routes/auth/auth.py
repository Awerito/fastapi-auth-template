from datetime import timedelta
from pymongo.database import Database
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, Security, status

from src.database import get_db_instance
from src.config import ACCESS_TOKEN_DURATION_MINUTES
from src.auth import (
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


authentication_routes = APIRouter()


@authentication_routes.post(
    "/token", response_model=Token, tags=["Users and Authentication"]
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db_instance),
):
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

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@authentication_routes.post("/user/", tags=["Users and Authentication"])
async def create_user(
    user: UserCreate = Depends(UserCreate),
    current_user: User = Security(current_active_user, scopes=["user.create"]),
    db: Database = Depends(get_db_instance),
):
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

    user_exists = get_user(db, user.username)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not created"
        )

    hashed_password = get_password_hash(user.password)
    db.users.insert_one(
        UserInDB(**user.model_dump(), hashed_password=hashed_password).model_dump()
    )

    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="User created")


@authentication_routes.get(
    "/user/{name}/", response_model=User, tags=["Users and Authentication"]
)
async def get_user_by_username(
    name: str,
    current_user: User = Security(current_active_user, scopes=["user.me"]),
    db: Database = Depends(get_db_instance),
):
    """Returns basic info of the given user.

    Parameters
    ----------
    name: str

    """

    if "admin" in current_user.scopes or (
        "user.me" in current_user.scopes and current_user.username == name
    ):
        user = get_user(db, name)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
            )

        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@authentication_routes.put("/user/{name}/", tags=["Users and Authentication"])
async def update_user(
    name: str,
    user: UserCreate = Depends(UserCreate),
    current_user: User = Security(current_active_user, scopes=["user.update"]),
    db: Database = Depends(get_db_instance),
):
    """Update the current user's usersname. Cannot be repeated.

    Parameters
    ----------
    user: str

    user_form: Depends(User)

    """

    if "admin" in current_user.scopes or current_user.username == name:
        hasshed_password = get_password_hash(user.password)
        db.users.update_one(
            {"username": name},
            {
                "$set": UserInDB(
                    **user.model_dump(), hashed_password=hasshed_password
                ).model_dump()
            },
        )
        raise HTTPException(status_code=status.HTTP_200_OK, detail="User updated")

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@authentication_routes.delete("/user/{name}/", tags=["Users and Authentication"])
async def delete_user(
    name: str,
    current_user: User = Security(current_active_user, scopes=["user.delete"]),
    db: Database = Depends(get_db_instance),
):
    """Delete the given user if exists.

    Parameters
    ----------
    name: str

        target username to delete

    """

    if "admin" in current_user.scopes:
        result = db.users.delete_one({"username": name})

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
        user = get_user(db, name)
        db.users.update_one({"username": name}, {"$set": {"disabled": True}})
        raise HTTPException(status_code=status.HTTP_200_OK, detail="User deleted")

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@authentication_routes.get(
    "/user/", response_model=list[User], tags=["Users and Authentication"]
)
async def get_all_users(
    current_user: User = Security(current_active_user, scopes=["user.all"]),
    db: Database = Depends(get_db_instance),
):
    """Lists all existing users.

    Returns
    -------
    list[User]

        list of all users's info. Passwords not included.

    """

    users = list(db.users.find({}, {"_id": 0, "hashed_password": 0}))
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return [User(**user) for user in users]
