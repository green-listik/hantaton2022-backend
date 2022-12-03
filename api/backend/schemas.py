from pydantic import BaseModel


class ValueBase(BaseModel):
    id: str
    value: int


class ValueCreate(ValueBase):
    pass


class Value(ValueBase):
    class Config:
        orm_mode = True


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


class OperationBase(BaseModel):
    id: int
    name: str
    parameters: dict
    is_completed: bool


class Operation(OperationBase):
    class Config:
        orm_mode = True


class ExampleOperationBase(BaseModel):
    id: int
    name: str
    parameters: dict


class ExampleOperation(ExampleOperationBase):
    class Config:
        orm_mode = True
