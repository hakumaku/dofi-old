import typer

from dofi.cli import subcommand


def init_typer_app() -> typer.Typer:
    app = typer.Typer()
    app.add_typer(subcommand.github.app)

    return app


typer_app = init_typer_app()
