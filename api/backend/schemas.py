from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    middle_name: str
    is_admin: bool


class User(UserBase):
    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True


class FieldBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class BushBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Operation(BaseModel):
    id: int
    name: str
    parameters: dict
    is_complete: bool

    class Config:
        orm_mode = True


class Event(EventBase):
    description: str
    operations: list[Operation]


class Well(BaseModel):
    id: int
    name: str
    parameters: dict
    events: list[Event]

    class Config:
        orm_mode = True


class Bush(BushBase):
    wells: list[Well]


class Field(FieldBase):
    bushes: list[Bush]

    class Config:
        orm_mode = True


class ExampleOperationBase(BaseModel):
    id: int
    name: str
    parameters: dict

    class Config:
        orm_mode = True


class ExampleOperation(ExampleOperationBase):
    pass
