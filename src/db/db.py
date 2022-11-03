import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URI = os.environ['DATABASE_URI']


engine = create_engine(DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property


def create_db():
    Base.metadata.create_all(bind=engine)


def reset_db():
    for table in Base.metadata.sorted_tables:
        table.drop(engine)
