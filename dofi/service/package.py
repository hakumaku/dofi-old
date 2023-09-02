from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from dofi.database import begin_session
from dofi.models import models


class PackageService:
    def upsert(self, package_name: str, remote_version: str) -> models.Package:
        """
        Insert a new row, or update an existing one if conflicts.
        """
        stmt = (
            insert(models.Package)
            .values(
                name=package_name,
                local_version="",
                remote_version=remote_version,
            )
            .on_conflict_do_update(index_elements=["name"], set_=dict(remote_version=remote_version))
            .returning(models.Package)
        )

        with begin_session() as db:
            return db.execute(stmt).scalar_one()

    def get(self, package_name: str) -> models.Package | None:
        stmt = select(models.Package).where(models.Package.name == package_name)

        with begin_session() as db:
            return db.execute(stmt).scalar_one_or_none()

    def get_all(self, package_name: str) -> list[models.Package]:
        stmt = select(models.Package).where(models.Package.name == package_name).order_by(models.Package.name)

        with begin_session() as db:
            return list(db.execute(stmt).scalars())

    def update_local_version(self, package_name: str, local_version: str) -> models.Package:
        stmt = (
            update(models.Package)
            .where(models.Package.name == package_name)
            .values(local_version=local_version)
            .returning(models.Package)
        )

        with begin_session() as db:
            return db.execute(stmt).scalar_one()

    def update_remote_version(self, package_name: str, remote_version: str) -> models.Package:
        now = datetime.now()
        stmt = (
            update(models.Package)
            .where(models.Package.name == package_name)
            .values(remote_version=remote_version, last_checked_at=now)
            .returning(models.Package)
        )

        with begin_session() as db:
            return db.execute(stmt).scalar_one()
