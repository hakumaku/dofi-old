import re
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

from dofi.extra.abc import API
from dofi.extra.github import schemas

if TYPE_CHECKING:
    from dofi.extra.types import Repository
    from dofi.utils.network import ClientSessionProxy, HttpResponse


def _select_download_url(info: schemas.GithubReleaseInfo, pattern: str) -> str:
    download_url: list[str] = [asset.browser_download_url for asset in info.assets]
    matched_urls: list[str] = list(filter(lambda url: re.search(pattern, url) is not None, download_url))

    if len(matched_urls) == 1:
        return matched_urls[0]

    if len(matched_urls) == 0:
        messages: list[str] = [
            "matching url is not found",
            f"pattern: '{pattern}'",
            f"browser_download_urls: {download_url}",
        ]
    else:
        messages = [
            "multiple matching urls are found",
            f"pattern: '{pattern}'",
            f"browser_download_urls: {download_url}",
        ]

    raise RuntimeError("\n".join(messages))


class GithubAPI(API):
    def __init__(self, *, access_token: str | None = None):
        self.headers: Mapping[str, str] | None = None
        if access_token:
            self.headers = {
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }

    async def get_release_info(
        self, client: "ClientSessionProxy", repository: "Repository"
    ) -> schemas.GithubReleaseInfo:
        response = await client.get(
            url=f"https://api.github.com/repos/{repository.username}/{repository.repo_name}/releases/latest",
            headers=self.headers,
        )
        return response.parse_contents_as(schemas.GithubReleaseInfo)

    async def download(
        self,
        client: "ClientSessionProxy",
        repository: "Repository",
        *,
        dest: Path | None = None,
    ) -> "HttpResponse":
        release_info = await self.get_release_info(client, repository)
        download_url = _select_download_url(release_info, repository.download_link)

        dest = dest if dest is not None else Path.home() / "Downloads"

        return await client.get(url=download_url, headers=self.headers, download=dest)
        # TODO: compare local version with remote version
        # TODO: extract zip files
