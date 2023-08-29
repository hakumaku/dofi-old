def test_cli_sync(cli, cli_app):
    result = cli.invoke(cli_app, ["sync"])
    print(result.output)
