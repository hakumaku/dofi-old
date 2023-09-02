def test_cli_check(cli, cli_app):
    result = cli.invoke(cli_app, ["check"])
    print(result.output)
