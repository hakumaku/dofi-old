from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from pytest_mock import MockerFixture

from sqlalchemy import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database

from dofi.database.database import DatabaseManager, SQLite3Database
from dofi.models import models


@contextmanager
def create_test_database(path: Path, mocker: MockerFixture) -> Generator[URL, None, None]:
    # Change test configuration here
    path = path / "pytest_db.sqlite"
    test_database = SQLite3Database(path=str(path))

    # Setup
    create_database(test_database.url)
    models.ModelBase.metadata.create_all(bind=test_database.engine)

    session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=test_database.engine)

    mocker.patch.object(DatabaseManager, "__getitem__", return_value=session)

    yield test_database.url

    # Teardown
    drop_database(test_database.url)
