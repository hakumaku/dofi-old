from pydantic import BaseModel


class Repository(BaseModel):
    username: str
    project: str


class RepositoryReleaseInfo(Repository):
    version: str
    download_link: str


class Package(Repository):
    pattern: str
