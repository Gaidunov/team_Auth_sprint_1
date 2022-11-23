import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column, DateTime, Text,
    String, ForeignKey,
    Enum, Table, UniqueConstraint
)
from sqlalchemy import event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from src.db.db import Base
from .session_history import (
    DeviceType,
    create_table_login_history_partition_ddl,
)

db = SQLAlchemy()

users_n_roles = Table(
    "users_n_roles",
    Base.metadata,
    Column("users_id", ForeignKey("users.id"), primary_key=True),
    Column("roles_id", ForeignKey("roles.id"), primary_key=True),
)

        
class User(Base):
    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid1
    )
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    roles = relationship(
        "Role",
        secondary=users_n_roles,
        back_populates="users"
    )
    sessions = relationship('SessionHistory')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.login}>'


USER_ACTIONS = ['login', 'logout']


class SessionHistoryMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid1,
        unique=True,
        nullable=False
    )

    @declared_attr
    def user_id(self):
        return Column(
            Text(),
            ForeignKey("users.id")
        )

    date = Column(DateTime)
    action = Column(
        Enum(
            *USER_ACTIONS,
            name='actions'
        ),
    )
    user_agent = Column(Text())
    user_device_type = Column(
        Enum(DeviceType),
        primary_key=True
    )


class SessionHistoryPC(SessionHistoryMixin, db.Model):
    """User session history model for partition table for PC."""

    __tablename__ = "session_history_pc"


class SessionHistoryMobile(SessionHistoryMixin, db.Model):
    """User session history model for partition table for mobile devices."""

    __tablename__ = "session_history_mobile"


class SessionHistoryTablet(SessionHistoryMixin, db.Model):
    """User session history model for partition table for tablet devices."""
    __tablename__ = "session_history_tablet"


class SessionHistoryBot(SessionHistoryMixin, db.Model):
    """User session history model for partition table for bots."""

    __tablename__ = "session_history_bot"


class SessionHistoryUnknown(SessionHistoryMixin, db.Model):
    """User session history model for partition table for other unknown types."""

    __tablename__ = "session_history_unknown"


PARTITION_TABLES_REGISTRY = (
    (SessionHistoryPC, DeviceType.PC),
    (SessionHistoryMobile, DeviceType.MOBILE),
    (SessionHistoryTablet, DeviceType.TABLET),
    (SessionHistoryBot, DeviceType.BOT),
    (SessionHistoryUnknown, DeviceType.UNKNOWN),
)


class SessionHistory(SessionHistoryMixin, Base):
    __tablename__ = 'session_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
        }
    )


def attach_event_listeners() -> None:
    for class_, device_type in PARTITION_TABLES_REGISTRY:
        class_.__table__.add_is_dependent_on(SessionHistory.__table__)
        event.listen(
            class_.__table__,
            'after_create',
            create_table_login_history_partition_ddl(
                class_.__table__,
                device_type,
            ),
        )


attach_event_listeners()


class Role(Base):
    __tablename__ = 'roles'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid1,
        unique=True, nullable=False
    )
    name = Column(Text(), unique=True, nullable=False)
    users = relationship(
        "User",
        secondary=users_n_roles,
        back_populates="roles"
    )

    def __repr__(self):
        return f'<Role {self.name}>'


class RegService(Base):
    __tablename__ = 'registration_servises'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid1,
        unique=True, nullable=False
    )
    name_service = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)

