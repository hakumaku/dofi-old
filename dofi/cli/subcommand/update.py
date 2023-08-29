"""
Check for newer versions on remote server.
"""
import typer

app = typer.Typer(name="update")


@app.command()
def foo():
    print("foo")


@app.callback(invoke_without_command=True)
def update_packages(ctx: typer.Context):
    if ctx.invoked_subcommand:
        return

    print("hello, world!")
