from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dofi.extra.types import Repository, RepositoryReleaseInfo
    from dofi.utils.network import ClientSessionProxy, HttpResponse


class API(ABC):
    @abstractmethod
    async def fetch_release_info(
        self, client: "ClientSessionProxy", repository: "Repository", pattern: str
    ) -> "RepositoryReleaseInfo":
        """
        Fetch latest release info from git remote repository.
        """

    @abstractmethod
    async def download(
        self,
        client: "ClientSessionProxy",
        repository: "Repository",
        pattern: str,
        *,
        dest: Path | None = None,
    ) -> "HttpResponse":
        """
        Download a file from git remote repository.
        """
