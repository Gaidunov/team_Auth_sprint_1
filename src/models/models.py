import uuid
import enum
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Column, Integer, DateTime, Text, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from src.db.db import Base

db = SQLAlchemy()


class User(Base):
    __tablename__ = 'users'

    id = Column(Text(length=100), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    refresh_token = relationship("RefreshTokens", uselist=False, backref="user")
    session = relationship('SessionHistory')
    roles = relationship("Role", back_populates="user")

    def set_password(self, password):   
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.login}>' 

class UserActoins(enum.Enum):
    login = 'login'
    log_out = 'log_out'
    

class SessionHistory(Base):
    __tablename__ = 'history'

    id = Column(Text(length=100), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    action = Column(Enum(UserActoins))


class UserRoles(enum.Enum):
    admin = 'admin'
    registered = 'registred'
    unregistered = 'unregistred'


class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Text(length=100), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
    name = Column(Enum(UserRoles)) 
    user = relationship("User")
    user_id = Column(Integer, ForeignKey("users.id"))
   
    def __repr__(self):
        return f'<Role {self.login}>' 


class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Text(length=100), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    token_expiration_date = Column(DateTime(timezone=True))
    token = Column(Text(length=100), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'token'),
      )

    def __repr__(self):
        return f'token {self.refresh_token} for user {self.user_id}'
