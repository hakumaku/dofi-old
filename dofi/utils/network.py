import functools
import logging
from dataclasses import dataclass
from http.cookies import SimpleCookie
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncContextManager, Literal, Mapping, Protocol, Type, TypeAlias

from pydantic import ValidationError

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from yarl import URL

if TYPE_CHECKING:
    from dofi.utils.typehint import SchemaType

Method: TypeAlias = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]

logger = logging.Logger(__name__)


class _RequestPartial(Protocol):
    def __call__(self) -> AsyncContextManager[ClientResponse]:
        """
        Typehint "functools.partial" of aiohttp request methods.
        """


@dataclass(slots=True, frozen=True)
class HttpResponse:
    url: URL
    status: int
    reason: object
    contents: bytes
    cookies: SimpleCookie[str]

    def __str__(self) -> str:
        return f"<Response [{self.status}]>"

    def parse_contents_as(self, schemas: Type["SchemaType"]) -> "SchemaType":
        try:
            return schemas.model_validate_json(self.contents)
        except ValidationError as e:
            msg = f"{self.url}[{self.status}]: {self.reason} (body: {self.contents!s}, schemas: {schemas.__name__})"
            logger.error(msg)
            raise e


async def _request(fn: _RequestPartial, *, download: Path | None = None) -> HttpResponse:
    if download is None:
        async with fn() as response:
            contents = await response.read()

        return HttpResponse(
            url=response.url,
            status=response.status,
            reason=response.reason,
            cookies=response.cookies,
            contents=contents,
        )

    async with fn() as response:
        assert response.content_disposition
        assert response.content_disposition.filename

        output = download / response.content_disposition.filename
        with open(output, "wb") as f:
            async for chunk in response.content.iter_chunked(2**20):
                f.write(chunk)

    return HttpResponse(
        url=response.url,
        status=response.status,
        reason=response.reason,
        cookies=response.cookies,
        contents=b"",
    )


class ClientSessionProxy:
    def __init__(self, session: ClientSession):
        self._session = session

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        download: Path | None = None,
    ) -> HttpResponse:
        fn = functools.partial(
            self._session.get,
            url,
            params=params,
            cookies=cookies,
            headers=headers,
        )
        return await _request(fn, download=download)

    async def post(
        self,
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        cookies: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        fn = functools.partial(
            self._session.post,
            url,
            data=data,
            json=json,
            cookies=cookies,
            headers=headers,
        )
        return await _request(fn)


class HttpClient:
    def __init__(
        self, *, base_url: str | None = None, headers: Mapping[str, str] | None = None, timeout: int | None = None
    ):
        self.base_url = base_url
        self.timeout = ClientTimeout(total=timeout)
        self.headers = headers
        self.client_session: ClientSession | None = None

    async def __aenter__(self) -> "ClientSessionProxy":
        self.client_session = ClientSession(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        )
        return ClientSessionProxy(self.client_session)

    async def __aexit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.client_session:
            await self.client_session.close()
            self.client_session = None
