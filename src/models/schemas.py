from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from src.models.models import Role, SessionHistory

PydanticRole = sqlalchemy_to_pydantic(Role)
PydanticSessions = sqlalchemy_to_pydantic(SessionHistory, exclude=['id','user_id'])

