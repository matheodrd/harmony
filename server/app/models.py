import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChannelType(enum.Enum):
    TEXT = "text"
    VOICE = "voice"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    owned_servers: Mapped[list[Server]] = relationship(
        back_populates="owner",
        lazy="selectin",  # FIXME: change to "raise" and implement pagination
    )


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped[User] = relationship(back_populates="owned_servers", lazy="joined")
    channels: Mapped[list[Channel]] = relationship(
        back_populates="server",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[ChannelType] = mapped_column(
        Enum(ChannelType),
        default=ChannelType.TEXT,
    )
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))

    server: Mapped[Server] = relationship(back_populates="channels")
