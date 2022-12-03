import os

from fastapi import FastAPI, Depends, HTTPException
import crud
import models
import schemas
import utils
from security import decode_jwt, JWTBearer, verify_password, sign_jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import TypeVar, Generic, Dict


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


async def admin_required(token: str = Depends(JWTBearer()), session: AsyncSession = Depends(get_session)):
    user = await get_user_from_jwt(session, token)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(JWTBearer())):
    return await get_user_from_jwt(session, token)


T = TypeVar('T')
class ErrorModel(Generic[T], BaseModel):
    ok: bool
    obj: T | str


if os.getenv('LOCAL_INSTANCE') is None:
    app = FastAPI(root_path='/api')
else:
    app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await models.init_engine()
    session = await get_session()
    await crud.create_user(session, models.User(username='admin', password='admin', is_admin=True))


@app.get("/get_fields", response_model=list[schemas.Field], dependencies=[Depends(JWTBearer())])
async def get_fields(session: AsyncSession = Depends(get_session)):
    return await crud.get_fields(session)


@app.get("/get_dots/{event_id}", response_model=schemas.Dots, dependencies=[Depends(JWTBearer())])
async def get_dots(event_id, session: AsyncSession = Depends(get_session)):
    return await utils.get_dots(session, event_id)


@app.post("/create_field", response_model=schemas.FieldBase, dependencies=[Depends(admin_required)])
async def create_field(field: schemas.FieldBase, session: AsyncSession = Depends(get_session)):
    res = await crud.create_field(session, field)
    return res


@app.post("/create_bush", response_model=schemas.Bush, dependencies=[Depends(admin_required)])
async def create_bush(bush: schemas.BushCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_bush(session, bush)


@app.post("/create_well", response_model=schemas.Well, dependencies=[Depends(JWTBearer())])
async def create_well(well: schemas.WellCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_well(session, well)


@app.post("/create_event", response_model=schemas.Event, dependencies=[Depends(JWTBearer())])
async def create_event(event: schemas.EventCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_event(session, event)


@app.post("/create_operation", response_model=schemas.Operation, dependencies=[Depends(JWTBearer())])
async def create_operation(operation: schemas.OperationCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_operation(session, operation)


@app.post("create_example_operation", response_model=schemas.ExampleOperation, dependencies=[Depends(JWTBearer())])
async def create_example_operation(operation: schemas.ExampleOperationCreate,
                                   session: AsyncSession = Depends(get_session)):
    return await crud.create_example_operation(session, operation)


@app.post("/delete_operation/{operation_id}", dependencies=[Depends(JWTBearer())], response_model=bool)
async def delete_operation(operation_id: int, session=Depends(get_session)):
    return (await crud.delete_operation(session, operation_id)) is not None


@app.post("/update_operation_order", response_model=ErrorModel[schemas.Event], dependencies=[Depends(JWTBearer())])
async def update_operation_order(event_id: int, new_order: list[int], session=Depends(get_session)):
    res = await crud.update_operation_order_for_event(session, event_id, new_order)
    if isinstance(res, str):
        return {
            "ok": False,
            "obj": res
        }
    return {
        "ok": True,
        "obj": res
    }


@app.post("/add_user", response_model=schemas.User, dependencies=[Depends(JWTBearer()), Depends(admin_required)])
async def register(user: schemas.User, db=Depends(get_session)):
    db_user = await crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)


@app.post("/login", response_model=ErrorModel[str])
async def login(user: schemas.UserLoginSchema, session=Depends(get_session)):
    res = await crud.get_user_by_username(session, user.login)
    if res:
        if verify_password(user.password, res.password):
            return {
                "ok": True,
                "res": sign_jwt(res.username)['access_token']
            }
    return {
        "ok": False,
        "obj": "Неверные данные входа"
    }
