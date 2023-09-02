from pathlib import Path
from typing import Any, Literal, cast, overload
from unittest.mock import Mock

from pytest_mock import MockerFixture

from aiohttp import ClientSession

from dofi.utils.network import ClientSessionProxy, HttpResponse

from .network import MockRequest


class Helper:
    def __init__(self, mocker: MockerFixture):
        self.resource_dir: Path = Path(__file__).parents[1] / "resources"
        self.mocker: MockerFixture = mocker

    @overload
    def read_file(self, filename: str, *, mode: Literal["r"]) -> str:
        ...

    @overload
    def read_file(self, filename: str, *, mode: Literal["rb"]) -> bytes:
        ...

    def read_file(self, filename: str, *, mode: Literal["r", "rb"] = "r") -> str | bytes:
        with open(f"{self.resource_dir}/{filename}", mode=mode) as fp:
            return cast(str | bytes, fp.read())

    def get_path(self, filename: str) -> Path:
        return self.resource_dir / filename

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

    def mock_parse_contents_as(
        self,
        method: Literal["get", "post"],
        value: Any,
    ):
        def fn(*args, **kwargs):
            return value

        response = Mock(spec=HttpResponse)
        response.parse_contents_as = fn
        self.mocker.patch.object(ClientSessionProxy, method, return_value=response)
