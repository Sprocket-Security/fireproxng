from click.testing import CliRunner

from fireproxng.__main__ import main


def test_cli():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "fireprox-ng" in result.output

    commands = ["create", "list", "delete", "update"]
    for c in commands:
        result = runner.invoke(main, [c])
        assert result.exit_code == 0
        assert c in result.output
