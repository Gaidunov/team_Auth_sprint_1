from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from ..config import DB_CONNECTION_STRING

engine = create_engine(DB_CONNECTION_STRING)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property


def create_db() -> None:
    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    for table in Base.metadata.sorted_tables:
        table.drop(engine)
