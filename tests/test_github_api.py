import pytest

from starlette import status

from dofi.extra import api
from dofi.extra.types import Repository
from dofi.utils.network import HttpClient


class TestGithubAPI:
    @pytest.fixture(autouse=True)
    def _fake_get_release_info(self, helper):
        contents = helper.read_file("github_api_release_info_contents.json", mode="rb")
        helper.mock_http_request(
            "get",
            status_code=status.HTTP_200_OK,
            data=contents,
        )

    @pytest.mark.asyncio()
    async def test_github_api_fetch_release_info_should_return_when_only_one_is_matched(self):
        github = api.Github()

        async with HttpClient() as client:
            release_info = await github.fetch_release_info(
                client, Repository(username="jesseduffield", project="lazygit"), pattern="Linux_x86_64"
            )

        assert release_info.version == "v0.40.2"
        assert (
            release_info.download_link
            == "https://github.com/jesseduffield/lazygit/releases/download/v0.40.2/lazygit_0.40.2_Linux_x86_64.tar.gz"
        )

    @pytest.mark.asyncio()
    async def test_github_api_fetch_release_info_should_raise_when_nothing_is_matched(self):
        github = api.Github()

        with pytest.raises(RuntimeError) as e:
            async with HttpClient() as client:
                await github.fetch_release_info(
                    client, Repository(username="jesseduffield", project="lazygit"), pattern=r"test"
                )

        assert "matching url is not found" in str(e)

    @pytest.mark.asyncio()
    async def test_github_api_fetch_release_info_should_raise_when_more_than_one_is_matched(self):
        github = api.Github()

        with pytest.raises(RuntimeError) as e:
            async with HttpClient() as client:
                await github.fetch_release_info(
                    client, Repository(username="jesseduffield", project="lazygit"), pattern=r"\w*"
                )

        assert "multiple matching" in str(e)
