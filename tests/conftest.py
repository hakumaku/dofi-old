import os
from typing import Generator

import pytest
from pytest_mock import MockerFixture

from typer import Typer
from typer.testing import CliRunner

from sqlalchemy import URL

from dofi.cli.app import get_typer_app
from dofi.settings.env import ROOT_DIR
from utils.database import create_test_database
from utils.helper import Helper


def pytest_sessionstart(session):
    # Override env variables for running pytest without hassles.
    os.environ["SQLITE_DB_PATH"] = str(ROOT_DIR)


@pytest.fixture()
def helper(mocker: MockerFixture) -> Helper:
    return Helper(mocker=mocker)


@pytest.fixture()
def cli() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def cli_app() -> Typer:
    return get_typer_app()


@pytest.fixture()
def database(tmp_path, mocker: MockerFixture) -> Generator[URL, None, None]:
    with create_test_database(tmp_path, mocker) as url:
        yield url
