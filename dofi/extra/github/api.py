import re
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

from dofi.extra.abc import API
from dofi.extra.types import Repository, RepositoryReleaseInfo

from . import schemas

if TYPE_CHECKING:
    from dofi.utils.network import ClientSessionProxy, HttpResponse


def select_download_url(info: schemas.GithubReleaseInfo, pattern: str) -> str:
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

    async def fetch_release_info(
        self, client: "ClientSessionProxy", repository: "Repository", pattern: str
    ) -> RepositoryReleaseInfo:
        response = await client.get(
            url=f"https://api.github.com/repos/{repository.username}/{repository.project}/releases/latest",
            headers=self.headers,
        )
        info = response.parse_contents_as(schemas.GithubReleaseInfo)
        download_link = select_download_url(info, pattern=pattern)

        return RepositoryReleaseInfo(
            username=repository.username,
            project=repository.project,
            version=info.tag_name,
            download_link=download_link,
        )

    async def download(
        self,
        client: "ClientSessionProxy",
        repository: "Repository",
        pattern: str,
        *,
        dest: Path | None = None,
    ) -> "HttpResponse":
        info = await self.fetch_release_info(client, repository, pattern)
        dest = dest if dest is not None else Path.home() / "Downloads"

        return await client.get(url=info.download_link, headers=self.headers, download=dest)
        # TODO: actually download method is not mandatory?
        # TODO: compare local version with remote version
        # TODO: extract zip files
