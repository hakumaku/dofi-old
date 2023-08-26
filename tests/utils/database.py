from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from pytest_mock import MockerFixture

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database

from dofi.database.database import DatabaseManager
from dofi.models import models


@contextmanager
def create_test_database(path: Path, mocker: MockerFixture) -> Generator[URL, None, None]:
    path = path / "pytest_db.sqlite"
    url = URL.create(
        drivername="sqlite",
        database=str(path),
    )

    create_database(url)
    engine = create_engine(url, connect_args={})
    models.ModelBase.metadata.create_all(bind=engine)

    session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    mocker.patch.object(DatabaseManager, "__getitem__", return_value=session)

    yield url

    drop_database(url)
