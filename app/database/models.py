
import uuid

from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Dataset(Base):

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    row_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    column_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    schema_info: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    profile: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
