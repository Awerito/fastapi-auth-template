from typing import Annotated
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from src.database import MongoDBConnectionManager
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_DURATION_MINUTES


# Scopes
SCOPES = {
    "admin": "Complete access to the API.",
    # User
    "user.me": "The current user.",
    "user.all": "All users.",
    "user.create": "Create a new user.",
    "user.update": "Update a user.",
    "user.delete": "Delete a user.",
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = False
    scopes: list[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user",
                "full_name": "username fullname",
                "email": "example@mail.com",
                "disabled": False,
            }
        }


class UserCreate(User):
    password: str


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=SCOPES)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(db: AsyncIOMotorDatabase, username: str):
    user = await db.users.find_one({"username": username})
    if not user:
        return None

    return UserInDB(**user)


async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_DURATION_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        if username == "":
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    async with MongoDBConnectionManager() as db:
        usernamestring = token_data.username if token_data.username else ""
        user = await get_user(db, username=usernamestring)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes or scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_admin_user():
    async with MongoDBConnectionManager() as db:
        user = await db.users.find_one()
        if user:
            return None

        admin_user = UserInDB(
            username="admin",
            hashed_password=get_password_hash("admin"),
            scopes=list(SCOPES.keys()),
            disabled=False,
        )
        await db.users.insert_one(admin_user.model_dump())
        return User(**admin_user.model_dump())
