import pytest
from pytest_mock import MockerFixture
from starlette import status

from dofi.extra import api
from dofi.extra.github import schemas
from dofi.extra.types import Repository
from dofi.utils.network import HttpClient


@pytest.mark.asyncio
async def test_github_api_get_release_info(helper):
    contents = helper.read_file("github_api_release_info_contents.json", mode="rb")
    helper.mock_http_request(
        "get",
        status_code=status.HTTP_200_OK,
        data=contents,
    )

    github = api.Github()

    async with HttpClient() as client:
        release_info = await github.get_release_info(
            client,
            Repository("jesseduffield", "lazygit", "my-link"),
        )

    assert release_info.author.login == "jesseduffield"
    assert release_info.url == "https://api.github.com/repos/jesseduffield/lazygit/releases/115470098"


class TestGithubAPI:
    @pytest.fixture(autouse=True)
    def fake_get_release_info(self, helper, mocker: MockerFixture):
        def fake_get_release_info(*args, **kwargs):
            fake_release_info = mocker.create_autospec(schemas.GithubReleaseInfo)
            asset1 = mocker.create_autospec(schemas.GithubAsset)
            asset1.browser_download_url = "foo"
            asset2 = mocker.create_autospec(schemas.GithubAsset)
            asset2.browser_download_url = "bar"

            fake_release_info.assets = [asset1, asset2]
            return fake_release_info

        mocker.patch.object(api.Github, "get_release_info", side_effect=fake_get_release_info)
        helper.mock_http_request("get", status_code=status.HTTP_200_OK, filename="source.zip", data=b"my file")

    @pytest.mark.asyncio
    async def test_github_api_download_should_raise_when_nothing_is_matched(self):
        github = api.Github()

        with pytest.raises(RuntimeError) as e:
            async with HttpClient() as client:
                await github.download(
                    client,
                    Repository("example", "lazygit", download_link=r"test"),
                )

        assert "matching url is not found" in str(e)

    @pytest.mark.asyncio
    async def test_github_api_download_should_raise_when_more_than_one_is_matched(self):
        github = api.Github()

        with pytest.raises(RuntimeError) as e:
            async with HttpClient() as client:
                await github.download(
                    client,
                    Repository("example", "lazygit", download_link=r"\w*"),
                )

        assert "multiple matching" in str(e)

    @pytest.mark.asyncio
    async def test_github_api_download_should_work_successfully_when_only_one_is_matched(self, tmp_path):
        github = api.Github()

        async with HttpClient() as client:
            response = await github.download(
                client, Repository("example", "lazygit", download_link=r"foo"), dest=tmp_path
            )

        assert response.status == status.HTTP_200_OK
        downloaded_file = tmp_path / "source.zip"
        assert downloaded_file.exists()
