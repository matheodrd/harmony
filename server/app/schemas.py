from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict

from app.models import ChannelType  # noqa: TC001

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


## Channel ##


class ChannelBase(APIModel):
    name: str
    type: ChannelType


class ChannelCreate(ChannelBase):
    pass


class ChannelRead(ChannelBase, ORMModel):
    id: int
    server_id: int


## Message ##


class MessageBase(APIModel):
    content: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase, ORMModel):
    id: int
    created_at: datetime
    author_id: int
    channel_id: int
