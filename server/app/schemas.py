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
