"""
Display packages status.
"""
import typer

app = typer.Typer(name="check")


@app.command()
def foo():
    print("foo")


@app.callback(invoke_without_command=True)
def check_packages(ctx: typer.Context):
    if ctx.invoked_subcommand:
        return

    print("hello, world!")
