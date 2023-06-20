import typer

app = typer.Typer(name="github")


@app.command("update")
def install_or_update():
    pass
