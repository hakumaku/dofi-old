from dofi.service.package import PackageService


class TestPackageService:
    def test_package_service_create_and_read(self, database):
        service = PackageService()

        package = service.create("my_package", remote_version="0.1.0")
        assert package.name == "my_package"
        assert package.last_checked_at is not None

        package_in_db = service.get("my_package")
        assert package_in_db
        assert package_in_db.name == package.name
        assert package_in_db.last_checked_at == package.last_checked_at

    def test_package_service_update_local_version(self, database):
        service = PackageService()

        package = service.create("my_package", remote_version="0.1.0")
        assert package.local_version == ""

        updated_package = service.update_local_version("my_package", local_version="0.2.0")
        assert updated_package.local_version == "0.2.0"

    def test_package_service_update_remote_version(self, database):
        service = PackageService()

        package = service.create("my_package", remote_version="0.1.0")

        updated_package = service.update_remote_version("my_package", remote_version="0.2.0")
        assert updated_package.remote_version == "0.2.0"
        assert updated_package.last_checked_at != package.last_checked_at
