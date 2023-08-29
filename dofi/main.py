from dofi.cli.app import get_typer_app


def main():
    app = get_typer_app()
    app()


if __name__ == "__main__":
    main()
