from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dofi.extra.types import Repository
    from dofi.utils.network import ClientSessionProxy, HttpResponse


class API(ABC):
    @abstractmethod
    async def download(
        self,
        client: "ClientSessionProxy",
        repository: "Repository",
        *,
        dest: Path | None = None,
    ) -> "HttpResponse":
        """
        Download a file from git remote repository.
        """
