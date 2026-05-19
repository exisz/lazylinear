from lazylinear.cli import build_parser


def test_parser_create():
    args = build_parser().parse_args(["create", "Hello", "--team", "EDU", "--label", "phase-1"])
    assert args.title == "Hello"
    assert args.team == "EDU"
    assert args.label == ["phase-1"]


def test_parser_move():
    args = build_parser().parse_args(["move", "EDU-1", "In Progress"])
    assert args.issue == "EDU-1"
    assert args.state == "In Progress"
