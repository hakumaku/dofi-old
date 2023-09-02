import asyncio
from pathlib import Path
from typing import Awaitable, cast

from dofi.extra.api import Github
from dofi.extra.types import Repository, RepositoryReleaseInfo
from dofi.parser.spec import Spec
from dofi.service.package import PackageService
from dofi.utils.network import HttpClient


async def fetch_release_info_from_spec(spec: Spec) -> list[RepositoryReleaseInfo]:
    api = Github()

    tasks: list[Awaitable[RepositoryReleaseInfo]] = []

    async with HttpClient() as client:
        for pkg in spec.packages:
            repository = Repository(username=pkg.username, project=pkg.project)
            task = api.fetch_release_info(client, repository=repository, pattern=pkg.pattern)
            tasks.append(task)

        result = await asyncio.gather(*tasks)

    return cast(list[RepositoryReleaseInfo], result)


def sync_package(path: Path):
    spec = Spec.from_yaml(path)
    release_info_list = asyncio.run(fetch_release_info_from_spec(spec))

    service = PackageService()
    for info in release_info_list:
        service.upsert(package_name=f"{info.username}/{info.project}", remote_version=info.version)
