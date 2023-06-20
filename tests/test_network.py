import json

import pytest
from starlette import status

from dofi.utils.network import HttpClient


@pytest.mark.asyncio
async def test_http_client_get(helper):
    helper.mock_http_request("get", status_code=status.HTTP_200_OK, data={"foo": 1, "bar": "Hello, world!"})

    async with HttpClient() as client:
        response = await client.get("https://example.com/test")

    assert response.status == status.HTTP_200_OK
    data = json.loads(response.contents)
    assert data["foo"] == 1
    assert data["bar"] == "Hello, world!"


@pytest.mark.asyncio
async def test_http_client_get_download(helper, tmp_path):
    helper.mock_http_request("get", status_code=status.HTTP_200_OK, filename="test.zip", data={"foo": 1})

    async with HttpClient() as client:
        response = await client.get("https://example.com/test", download=tmp_path)

    assert response.status == status.HTTP_200_OK
    file = tmp_path / "test.zip"
    assert file.exists()

    with open(file, "rb") as fp:
        contents = fp.read()

    data = json.loads(contents)
    assert data["foo"] == 1


@pytest.mark.asyncio
async def test_http_client_post(helper):
    helper.mock_http_request("post", status_code=status.HTTP_201_CREATED, data={"foo": 1, "bar": "Hello, world!"})

    async with HttpClient() as client:
        response = await client.post("https://example.com/test")

    assert response.status == status.HTTP_201_CREATED
    data = json.loads(response.contents)
    assert data["foo"] == 1
    assert data["bar"] == "Hello, world!"
