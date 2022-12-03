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
    user = await crud.get_user_by_username(session, data['user_id'])
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


async def get_session() -> AsyncSession:
    async with models.async_session() as session:
        async with session.begin():
            return session


async def admin_required(token: str, session: AsyncSession = Depends(get_session)):
    user = await get_user_from_jwt(session, token)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")


async def login_required(token: str, session: AsyncSession = Depends(get_session)):
    user = await get_user_from_jwt(session, token)
    if user is None:
        raise HTTPException(status_code=403, detail="Login required")


app = FastAPI()


@app.on_event("startup")
async def startup():
    await models.init_engine()
    session = await get_session()
    await crud.create_user(session, models.User(username='admin', password='admin', is_admin=True))


@app.get("/get_fields", response_model=list[schemas.Field], dependencies=[Depends(login_required)])
async def get_fields(session: AsyncSession = Depends(get_session)):
    return await crud.get_fields(session)


@app.get("/get_dots/{event_id}", response_model=list[schemas.Dot], dependencies=[Depends(login_required)])
async def get_dots(session: AsyncSession = Depends(get_session)):
    pass

@app.post("/create_field", response_model=schemas.FieldBase, dependencies=[Depends(admin_required)])
async def create_field(field: schemas.FieldBase, session: AsyncSession = Depends(get_session)):
    res = await crud.create_field(session, field)
    return res


@app.post("/create_bush", response_model=schemas.Bush, dependencies=[Depends(admin_required)])
async def create_bush(bush: schemas.BushCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_bush(session, bush)


@app.post("/create_well", response_model=schemas.Well, dependencies=[Depends(admin_required)])
async def create_well(well: schemas.WellCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_well(session, well)


@app.post("/create_event", response_model=schemas.Event)
async def create_event(event: schemas.EventCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_event(session, event)


@app.post("/create_operation", response_model=schemas.Operation)
async def create_operation(operation: schemas.OperationCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_operation(session, operation)


@app.post("/add_user", response_model=schemas.User, dependencies=[Depends(JWTBearer), Depends(admin_required)])
async def register(user: schemas.User, db=Depends(get_session)):
    db_user = await crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)


@app.post("/login")
async def login(user: schemas.UserLoginSchema, session=Depends(get_session)):
    res = await crud.get_user_by_username(session, user.login)
    if res:
        if verify_password(user.password, res.password):
            return sign_jwt(res.username)
    return {
        "error": "Wrong login details!"
    }
