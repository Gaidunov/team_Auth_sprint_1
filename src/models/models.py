import uuid
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Column, DateTime, Text, String, ForeignKey, Enum, Table
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
        Text(length=100),
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


class SessionHistory(Base):
    __tablename__ = 'session_history'

    id = Column(
        Text(length=100),
        primary_key=True,
        default=str(uuid.uuid1()),
        unique=True,
        nullable=False
    )
    user_id = Column(
        Text(length=100),
        ForeignKey("users.id")
    )
    date = Column(DateTime)
    action = Column(Enum(*USER_ACTIONS))
    user_agent = Column(Text(length=100))


class Role(Base):
    __tablename__ = 'roles'

    id = Column(
        Text(length=100),
        primary_key=True,
        default=str(uuid.uuid1()),
        unique=True, nullable=False
    )
    name = Column(Text(length=100), unique=True, nullable=False)
    users = relationship(
        "User",
        secondary=users_n_roles,
        back_populates="roles"
    )

    def __repr__(self):
        return f'<Role {self.name}>'
