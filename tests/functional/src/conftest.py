import contextlib

import pytest

from src.app import create_app
from src.db.db import engine, Base


@pytest.fixture()
def f_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def f_client(f_app):
    return f_app.test_client()


@pytest.fixture()
def f_prepare_db_for_tests() -> None:
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()
