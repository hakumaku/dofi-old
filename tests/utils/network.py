import itertools
import json
from contextlib import asynccontextmanager
from http.cookies import SimpleCookie
from unittest.mock import Mock

from starlette import status

from aiohttp.client_reqrep import ContentDisposition


class StreamReaderMock(Mock):
    def __init__(self, data: bytes):
        super().__init__()
        self.data = data

    async def read(self, *args, **kwargs):
        return self.data

    def iter_chunked(self, *args, **kwargs):
        class Reader:
            def __init__(self, data: bytes):
                self.done: bool = False
                self.data = data

            def __aiter__(self):
                return self

            async def __anext__(self) -> bytes:
                if self.done:
                    raise StopAsyncIteration

                self.done = True
                return self.data

        return Reader(self.data)


class ResponseMock(Mock):
    def __init__(
        self, data: dict | bytes, status_code: int | None = None, *args, filename: str | None = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.data: bytes = json.dumps(data).encode() if isinstance(data, dict) else data
        self.status_code = status_code if status_code is not None else status.HTTP_200_OK

    @property
    def content(self):
        return StreamReaderMock(self.data)

    @property
    def content_disposition(self):
        return Mock(spec=ContentDisposition, filename=self.filename)

    @property
    def url(self):
        return "fake_url"

    @property
    def status(self):
        return self.status_code

    @property
    def reason(self):
        return ""

    @property
    def cookies(self):
        return SimpleCookie()

    async def read(self, *args, **kwargs):
        return self.data


class MockRequest:
    def __init__(
        self,
        status_code: int | None = None,
        filename: str | None = None,
        data: dict | bytes | list[dict] | None = None,
    ):
        self.counter = itertools.count(0)
        self.status_code = status_code or status.HTTP_200_OK
        self.filename = filename
        self.fake_data: dict | bytes | list[dict] | None = data

    @asynccontextmanager
    async def __call__(self, *args, **kwargs):
        if isinstance(self.fake_data, bytes | dict):
            yield ResponseMock(self.fake_data, self.status_code, filename=self.filename)
        elif isinstance(self.fake_data, list):
            index = next(self.counter)
            yield ResponseMock(self.fake_data[index], self.status_code)
