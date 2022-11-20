import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, DateTime, Text,
    String, ForeignKey,
    Enum, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from src.db.db import Base

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
        Text(),
        primary_key=True,
        default=str(uuid.uuid1()),
        unique=True,
        nullable=False
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


def create_partition(target, connection, **kw) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_smart" PARTITION OF "session_history" FOR VALUES IN ('pc')"""
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS "session_history_mobile" 
        PARTITION OF "session_history" FOR VALUES IN ('mobile')
        """
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_web" PARTITION OF "session_history" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_web" PARTITION OF "session_history" FOR VALUES IN ('bot')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_web" PARTITION OF "session_history" FOR VALUES IN ('unknown')"""
    )


class SessionHistory(Base):
    __tablename__ = 'session_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = Column(
        Text(),
        primary_key=True,
        default=str(uuid.uuid1()),
        unique=True,
        nullable=False
    )
    user_id = Column(
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
    user_device_type = Column(Text, primary_key=True)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(
        Text(),
        primary_key=True,
        default=str(uuid.uuid1()),
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
