import uuid
from datetime import datetime

from pydantic import UUID4
from sqlalchemy import TIMESTAMP, DateTime, event, func
from sqlalchemy.engine import Connection
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, Mapper, declarative_mixin, mapped_column


class Base(DeclarativeBase):
    __name__: str

    # Generate __tablename__ automatically

    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


def default_uuid():
    return str(uuid.uuid4())


def model_before_create_listener(mapper: Mapper, connection: Connection, target):  # noqa
    if target.created_at is None:
        target.created_at = datetime.now()
    if target.updated_at is None:
        target.updated_at = datetime.now()


def model_before_update_listener(mapper: Mapper, connection: Connection, target):  # noqa
    target.updated_at = datetime.now()


@declarative_mixin
class SoftBase:
    id: Mapped[UUID4] = mapped_column(primary_key=True, server_default=func.gen_random_uuid(), default=default_uuid)
    # id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, index=True, server_default=func.now())
    created_by: Mapped[UUID4 | None]
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, index=True, server_default=func.now(), onupdate=datetime.now()
    )
    updated_by: Mapped[UUID4 | None]
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    deleted_by: Mapped[UUID4 | None]


event.listen(SoftBase, 'before_insert', model_before_create_listener, propagate=True)
event.listen(SoftBase, 'before_update', model_before_update_listener, propagate=True)


@declarative_mixin
class HardBase:
    id: Mapped[UUID4] = mapped_column(primary_key=True, server_default=func.gen_random_uuid(), default=default_uuid)
    # id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, index=True, server_default=func.now())
    created_by: Mapped[UUID4 | None]
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, index=True, server_default=func.now(), onupdate=datetime.now()
    )
    updated_by: Mapped[UUID4 | None]


event.listen(HardBase, 'before_insert', model_before_create_listener, propagate=True)
event.listen(HardBase, 'before_update', model_before_update_listener, propagate=True)
