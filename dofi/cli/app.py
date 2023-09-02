from functools import lru_cache

import typer

from . import subcommand


def init_typer_app() -> typer.Typer:
    app = typer.Typer()

    app.add_typer(subcommand.update.app)
    app.add_typer(subcommand.sync.app)
    app.add_typer(subcommand.check.app)

    return app


@lru_cache(maxsize=1)
def get_typer_app() -> typer.Typer:
    return init_typer_app()
