import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, DateTime, Text, String, ForeignKey
from sqlalchemy.orm import relationship

from db import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Text(length=100), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    password_hash = Column(String(128))
    refresh_token = relationship("RefreshTokens", uselist=False, backref="user")

    
    def set_password(self, password):   
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.login}>' 


class RefreshTokens(db.Model):
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


