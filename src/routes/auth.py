from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from src.database import db
from src.config import ACCESS_TOKEN_DURATION_MINUTES
from src.auth import (
    get_user,
    hash_password,
    verify_password,
    authenticate_user,
    create_access_token,
    current_active_user,
    User,
    Token,
)


authentication_routes = APIRouter()


@authentication_routes.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
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
            status_code=401,  # Unauthorized
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@authentication_routes.post("/admin/", tags=["Authentication"])
async def create_admin(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    full_name: str = Form(None),
):
    """Allows to create an initial user.

    Parameters
    ----------
    username: str

    password: str

    email: Optional(str)

    full_name: Optional(str)

    """

    users = list(db.users.find())
    if users:
        raise HTTPException(status_code=403, detail="Cannot create")

    new_user = {
        "username": username,
        "hashed_password": hash_password(password),
        "email": email,
        "full_name": full_name,
        "disabled": False,
    }

    db.users.insert_one(new_user)

    raise HTTPException(status_code=201, detail="User created")


@authentication_routes.post("/user/", tags=["Authentication"])
async def create_user(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    full_name: str = Form(None),
    current_user: User = Depends(current_active_user),
):
    """Allows to an authenticated user to create an user.

    Parameters
    ----------
    username: str

    password: str

    email: Optional(str)

    full_name: Optional(str)

    """

    user = get_user(db, username)
    if user:
        raise HTTPException(status_code=403, detail="User not created")

    new_user = {
        "username": username,
        "hashed_password": hash_password(password),
        "email": email,
        "full_name": full_name,
        "disabled": False,
    }

    db.users.insert_one(new_user)

    raise HTTPException(status_code=201, detail="User crated")


@authentication_routes.get(
    "/user/{username}/", response_model=User, tags=["Authentication"]
)
async def get_user_by_username(
    username: str, current_user: User = Depends(current_active_user)
):
    """Returns basic info of the given user.

    Parameters
    ----------
    username: str

    """

    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    return user


@authentication_routes.put("/user/name/", tags=["Authentication"])
async def update_user_name(
    old_username: str = Form(...),
    new_username: str = Form(...),
    current_user: User = Depends(current_active_user),
):
    """Update the current user's usersname. Cannot be repeated.

    Parameters
    ----------
    old_username: str

    new_username: str

    """

    if current_user.username != old_username:
        raise HTTPException(status_code=403, detail="Not allowed")

    if current_user.username == new_username:
        raise HTTPException(status_code=400, detail="Error on form")

    users = list(db.users.find({"username": new_username}))
    if users:
        raise HTTPException(status_code=400, detail="User exist")

    db.users.update_one(
        {"username": old_username}, {"$set": {"username": new_username}}
    )

    raise HTTPException(status_code=201, detail="User updated")


@authentication_routes.put("/user/pass/", tags=["Authentication"])
async def update_user_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    retry_password: str = Form(...),
    current_user: User = Depends(current_active_user),
):
    """Update the current user's password. Cannot be equals to the current password.

    Parameters
    ----------
    old_password: str

        original password of the user

    new_password: str

        new password

    retry_password: str

        check of new password

    """

    user = get_user(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    if (
        not verify_password(old_password, user.hashed_password)
        or new_password != retry_password
        or old_password == new_password
    ):
        raise HTTPException(status_code=400, detail="Error on form")

    db.users.update_one(
        {"username": current_user.username},
        {"$set": {"hashed_password": hash_password(new_password)}},
    )

    raise HTTPException(status_code=201, detail="User updated")


@authentication_routes.put("/user/info/", tags=["Authentication"])
async def update_user_information(
    email: str = Form(None),
    full_name: str = Form(None),
    current_user: User = Depends(current_active_user),
):
    """Update the current user's email or full_name. Both cannot be blank.

    Parameters
    ----------
    email: Optional(str)

        new email

    full_name: Optional(str)

        new full name

    """

    if not email and not full_name:
        raise HTTPException(status_code=400, detail="Error on form")

    new_data = dict()
    if email:
        new_data["email"] = email

    if full_name:
        new_data["full_name"] = full_name

    db.users.update_one(
        {"username": current_user.username},
        {"$set": new_data},
    )

    raise HTTPException(status_code=201, detail="User updated")


@authentication_routes.delete("/user/{username}/", tags=["Authentication"])
async def delete_user(
    username: str,
    current_user: User = Depends(current_active_user),
):
    """Delete the given user if exists.

    Parameters
    ----------
    username: str

        target username to delete

    """

    result = db.users.delete_one({"username": username})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

    raise HTTPException(status_code=201, detail="User remove")


@authentication_routes.get("/user/", response_model=list[User], tags=["Authentication"])
async def get_all_users(current_user: User = Depends(current_active_user)):
    """Lists all existing users.

    Returns
    -------
    list[User]

        list of all users's info. Passwords not included.

    """

    users = list(db.users.find({}, {"_id": 0, "hashed_password": 0}))
    if not users:
        raise HTTPException(status_code=404, detail="Not found")

    return [User(**user) for user in users]
