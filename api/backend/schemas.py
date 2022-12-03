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
    name: str

    class Config:
        orm_mode = True


class BushCreate(BushBase):
    field_name: str


class Bush(BushBase):
    id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class EventCreate(EventBase):
    well_id: int
    description: str


class OperationBase(BaseModel):
    name: str
    parameters: dict
    is_complete: bool

    class Config:
        orm_mode = True

class OperationCreate(OperationBase):
    event_id: int


class Operation(OperationBase):
    id: int


class Event(EventBase):
    id: int
    description: str
    operations: list[Operation]


class WellBase(BaseModel):
    name: str
    parameters: dict

    class Config:
        orm_mode = True


class WellCreate(WellBase):
    bush_id: int


class Well(WellBase):
    id: int
    events: list[Event]


class BushExtended(Bush):
    wells: list[Well]


class Field(FieldBase):
    bushes: list[BushExtended]

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


class Dots(BaseModel):
    planned: list[tuple[float, float]]
    actual: list[tuple[float, float]]
