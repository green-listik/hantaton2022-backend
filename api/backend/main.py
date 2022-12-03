import os

from fastapi import FastAPI, Depends, HTTPException
import crud
import models
import schemas
from security import decode_jwt, JWTBearer, verify_password, sign_jwt
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_from_jwt(session, token: str) -> models.User:
    data = decode_jwt(token)
    if data is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.get_user_by_username(session, data['username'])
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


async def get_session() -> AsyncSession:
    async with models.async_session() as session:
        async with session.begin():
            return session


app = FastAPI()


@app.on_event("startup")
async def startup():
    await models.init_engine()


@app.post("/add_user", response_model=schemas.User, dependencies=[Depends(JWTBearer())])
async def register(user: schemas.User, db=Depends(get_session)):
    db_user = await crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)

@app.post("/login")
async def login(user: schemas.UserLoginSchema, session = Depends(get_session)):
    res = await crud.get_user_by_username(session, user.login)
    if res:
        if verify_password(user.password, res.password):
            return sign_jwt(res.username)
    return {
        "error": "Wrong login details!"
    }

@app.get("/fields", response_model=list[schemas.Field])
async def fields(db=Depends(get_session)):
    return await crud.get_fields(db=db)
