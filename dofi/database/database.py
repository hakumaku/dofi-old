import re
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import ContextManager, Iterator, Mapping, cast

from fastapi.encoders import jsonable_encoder
from orjson import orjson  # type: ignore

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, declared_attr, sessionmaker

from dofi.settings.env import get_env_settings


def json_serializer(*args, **kwargs) -> str:
    # orjson.dumps returns 'bytes', not 'str'.
    return cast(str, orjson.dumps(*args, default=jsonable_encoder, **kwargs).decode())


class ModelBase(DeclarativeBase):
    """
    sqlalchemy base model.

    All models should inherit from this model to declare a table.
    """

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        table_name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return f"dofi_{table_name}"


class Database(ABC):
    """
    Database base class
    """

    @property
    @abstractmethod
    def engine(self) -> Engine:
        """
        Return sqlalchemy.Engine object.
        """


class SQLite3Database(Database):
    def __init__(self, *, path: str):
        url = URL.create(
            drivername="sqlite",
            database=path,
        )
        self._engine = create_engine(
            url,
            connect_args={},
            json_serializer=json_serializer,
        )

    @property
    def engine(self) -> Engine:
        return self._engine


class PostgresDatabase(Database):
    def __init__(self, *, username: str, password: str, host: str, db_name: str):
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=username,
            password=password,
            host=host,
            database=db_name,
        )
        self._engine = create_engine(
            url,
            connect_args={
                # Specify timezone explicitly to get consistent values of datetime fields.
                "options": "-c timezone=utc"
            },
            json_serializer=json_serializer,
        )

    @property
    def engine(self) -> Engine:
        return self._engine


class DatabaseManager(Mapping[str, sessionmaker]):
    def __init__(self, *, databases: dict[str, Database]):
        self._mapping: dict[str, sessionmaker] = {
            key: sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=database.engine)
            for key, database in databases.items()
        }

    def __getitem__(self, key: str) -> sessionmaker:
        return self._mapping[key]

    def __len__(self) -> int:
        return len(self._mapping)

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping)


@lru_cache(maxsize=1)
def get_database_manager() -> DatabaseManager:
    """
    Return database map holding all databases of the application.
    Use lru_cache() trick to defer the initialization of database,
    and avoid using global variable.
    """
    env = get_env_settings()
    databases: dict[str, Database] = {"default": SQLite3Database(path=str(env.SQLITE_DB_PATH))}
    return DatabaseManager(databases=databases)


def begin_session(*, name: str | None = None) -> ContextManager[Session]:
    """
    Return database map holding all databases of the application.
    Use lru_cache() trick to defer the initialization of database,
    and avoid using global variable.
    """
    name = name or "default"
    manager = get_database_manager()
    session = manager[name]

    return session.begin()
