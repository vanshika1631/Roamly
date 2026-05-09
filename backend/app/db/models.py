import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    oauth_provider: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TEBProfile(Base):
    __tablename__ = "teb_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String,index=True)
    teb_json: Mapped[dict] = mapped_column(JSONB)
    confidence_score: Mapped[float] = mapped_column(Float)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True)
    teb_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    constraints_json: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ItineraryRecord(Base):
    __tablename__ = "itineraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[str] = mapped_column(String, index=True)
    itinerary_json: Mapped[dict] = mapped_column(JSONB)
    audit_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String,index=True)
    trip_id: Mapped[str | None] = mapped_column(String, nullable=True)
    messages_json: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True)
    country: Mapped[str] = mapped_column(String)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
