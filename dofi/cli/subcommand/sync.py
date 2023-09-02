"""
Start syncing all packages.
"""
from pathlib import Path

import typer

from dofi import toolkit

app = typer.Typer(name="sync")


@app.command()
def foo():
    print("foo")


@app.callback(invoke_without_command=True)
def sync_packages(ctx: typer.Context, spec_path: Path):
    if ctx.invoked_subcommand:
        return

    toolkit.sync_package(spec_path)
