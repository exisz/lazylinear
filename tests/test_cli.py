from __future__ import annotations

import pytest

from lazylinear.cli import build_parser, main


def test_parser_create():
    args = build_parser().parse_args(["create", "Hello", "--team", "EDU", "--label", "phase-1"])
    assert args.title == "Hello"
    assert args.team == "EDU"
    assert args.label == ["phase-1"]


def test_parser_move():
    args = build_parser().parse_args(["move", "EDU-1", "In Progress"])
    assert args.issue == "EDU-1"
    assert args.state == "In Progress"


def test_parser_comments():
    args = build_parser().parse_args(["comments", "EDU-1", "--limit", "5"])
    assert args.issue == "EDU-1"
    assert args.limit == 5


def test_version_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["--version"])
    assert exc.value.code == 0
    assert "lazylinear" in capsys.readouterr().out


def test_main_reports_linear_error(monkeypatch, capsys):
    from lazylinear import cli
    from lazylinear.client import LinearError

    def boom(*_args, **_kwargs):
        raise LinearError("missing token")

    monkeypatch.setattr(cli, "graphql", boom)

    assert main(["viewer"]) == 1
    assert "linear: error: missing token" in capsys.readouterr().err
