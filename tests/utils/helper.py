from pathlib import Path
from typing import Literal, cast, overload

from pytest_mock import MockerFixture

from aiohttp import ClientSession

from .network import MockRequest


class Helper:
    def __init__(self, mocker: MockerFixture):
        self.mocker: MockerFixture = mocker

    @staticmethod
    @overload
    def read_file(filename: str, *, mode: Literal["r"]) -> str:
        ...

    @staticmethod
    @overload
    def read_file(filename: str, *, mode: Literal["rb"]) -> bytes:
        ...

    @staticmethod
    def read_file(filename: str, *, mode: Literal["r", "rb"] = "r") -> str | bytes:
        directory = Path(__file__).parents[1]
        with open(f"{directory}/resources/{filename}", mode=mode) as fp:
            return cast(str | bytes, fp.read())

    def mock_http_request(
        self,
        method: Literal["get", "post"],
        *,
        status_code: int | None = None,
        filename: str | None = None,
        data: dict | bytes | list[dict] | None = None,
    ):
        fake_request = MockRequest(status_code, filename=filename, data=data)
        self.mocker.patch.object(ClientSession, method, fake_request)
