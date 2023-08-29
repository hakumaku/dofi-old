def test_cli_update(cli, cli_app):
    result = cli.invoke(cli_app, ["update"])
    print(result.output)
