from pydantic import BaseModel, ConfigDict

## Base models ##


class APIModel(BaseModel):
    pass


class ORMModel(APIModel):
    model_config = ConfigDict(from_attributes=True)


## User ##


class UserBase(APIModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase, ORMModel):
    id: int


## Auth ##


class Token(APIModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


## Server ##


class ServerBase(APIModel):
    name: str


class ServerCreate(ServerBase):
    pass


class ServerRead(ServerBase, ORMModel):
    id: int
    owner_id: int
