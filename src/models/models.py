import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, DateTime, Text,
    String, ForeignKey,
    Enum, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event

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
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
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
    user_device_type = Column(
        Text,
        primary_key=True
    )


@event.listens_for(SessionHistory.__table__, 'after_create')
def receive_after_create(target, connection, **kw):
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_pc" 
        PARTITION OF "session_history" FOR VALUES IN ('pc')"""
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS "session_history_mobile" 
        PARTITION OF "session_history" FOR VALUES IN ('mobile')
        """
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_tablet" 
        PARTITION OF "session_history" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_bot" 
        PARTITION OF "session_history" FOR VALUES IN ('bot')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_history_unknown" 
        PARTITION OF "session_history" FOR VALUES IN ('unknown')"""
    )


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


class RegService(Base):
    __tablename__ = 'registration_servises'

    id = Column(
        Text(),
        primary_key=True,
        default=str(uuid.uuid1()),
        unique=True, nullable=False
    )
    name_service = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)


# class VkAccount(Base):
#     __tablename__ = 'vk_account'

#     id = db.Column(str(uuid.uuid1()), primary_key=True)
#     user_id = Column(
#         Text(),
#         ForeignKey("users.id")
#     )
#     user = db.relationship(User, backref=db.backref('vk_account', lazy=True))
#     vk_login = Column(String, unique=True, nullable=False)


#     # social_id = db.Column(db.Text, nullable=False)
#     # social_name = db.Column(db.Text, nullable=False)

#     __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'), )
    
#     def __repr__(self):
#         return f'<SocialAccount {self.social_name}:{self.user_id}>' 
