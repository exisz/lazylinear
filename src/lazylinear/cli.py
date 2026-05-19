from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .client import LinearError, graphql

ISSUE_FIELDS = "id identifier title url state { name type } team { key name } assignee { name email } labels { nodes { name } }"


def dump(data: Any, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif isinstance(data, list):
        for row in data:
            print(row)
    else:
        print(data)


def team_selector(key: str) -> tuple[str, dict[str, Any]]:
    return "query($key:String!){ teams(filter:{key:{eq:$key}}, first:1){ nodes { id key name } } }", {"key": key}


def get_team_id(key: str) -> str:
    data = graphql(*team_selector(key))
    teams = data.get("teams", {}).get("nodes", [])
    if not teams:
        raise LinearError(f"Team not found: {key}")
    return teams[0]["id"]


def get_issue_id(identifier: str) -> str:
    data = graphql("query($id:String!){ issue(id:$id){ id identifier title } }", {"id": identifier})
    issue = data.get("issue")
    if not issue:
        raise LinearError(f"Issue not found: {identifier}")
    return issue["id"]


def cmd_viewer(args):
    data = graphql("{ viewer { id name email } organization { id name urlKey } }")
    dump(data, args.json)


def cmd_teams(args):
    data = graphql("query($first:Int!){ teams(first:$first){ nodes { id key name } } }", {"first": args.limit})
    rows = data["teams"]["nodes"]
    if args.json:
        dump(rows, True)
    else:
        for t in rows:
            print(f"{t['key']}\t{t['name']}\t{t['id']}")


def cmd_states(args):
    team_id = get_team_id(args.team)
    data = graphql(
        "query($team:ID!){ workflowStates(filter:{team:{id:{eq:$team}}}){ nodes { id name type position } } }",
        {"team": team_id},
    )
    rows = sorted(data["workflowStates"]["nodes"], key=lambda r: r.get("position") or 0)
    if args.json:
        dump(rows, True)
    else:
        for s in rows:
            print(f"{s['name']}\t{s['type']}\t{s['id']}")


def cmd_issues(args):
    query = f"""
    query($first:Int!, $teamKey:String) {{
      issues(first:$first, filter:{{ team: {{ key: {{ eq: $teamKey }} }} }}) {{
        nodes {{ {ISSUE_FIELDS} }}
      }}
    }}
    """
    data = graphql(query, {"first": args.limit, "teamKey": args.team})
    rows = data["issues"]["nodes"]
    if args.json:
        dump(rows, True)
    else:
        for i in rows:
            print(f"{i['identifier']}\t{i['state']['name']}\t{i['title']}")


def cmd_read(args):
    data = graphql(f"query($id:String!){{ issue(id:$id){{ {ISSUE_FIELDS} description }} }}", {"id": args.issue})
    dump(data.get("issue"), args.json)


def cmd_create(args):
    team_id = get_team_id(args.team)
    input_data: dict[str, Any] = {"teamId": team_id, "title": args.title}
    if args.description:
        input_data["description"] = args.description
    if args.state:
        states = graphql(
            "query($team:ID!,$name:String!){ workflowStates(filter:{team:{id:{eq:$team}}, name:{eq:$name}}){ nodes { id name } } }",
            {"team": team_id, "name": args.state},
        )["workflowStates"]["nodes"]
        if not states:
            raise LinearError(f"State not found for {args.team}: {args.state}")
        input_data["stateId"] = states[0]["id"]
    if args.label:
        labels = []
        for name in args.label:
            found = graphql("query($name:String!){ issueLabels(filter:{name:{eq:$name}}){ nodes { id name } } }", {"name": name})["issueLabels"]["nodes"]
            if found:
                labels.append(found[0]["id"])
        if labels:
            input_data["labelIds"] = labels
    data = graphql(
        f"mutation($input:IssueCreateInput!){{ issueCreate(input:$input){{ success issue {{ {ISSUE_FIELDS} }} }} }}",
        {"input": input_data},
    )
    issue = data["issueCreate"]["issue"]
    dump(issue if args.json else f"{issue['identifier']} {issue['url']}", args.json)


def cmd_move(args):
    issue_id = get_issue_id(args.issue)
    issue = graphql("query($id:String!){ issue(id:$id){ team { id key } } }", {"id": args.issue})["issue"]
    team_id = issue["team"]["id"]
    states = graphql(
        "query($team:ID!,$name:String!){ workflowStates(filter:{team:{id:{eq:$team}}, name:{eq:$name}}){ nodes { id name } } }",
        {"team": team_id, "name": args.state},
    )["workflowStates"]["nodes"]
    if not states:
        raise LinearError(f"State not found: {args.state}")
    data = graphql(
        f"mutation($id:String!,$input:IssueUpdateInput!){{ issueUpdate(id:$id,input:$input){{ success issue {{ {ISSUE_FIELDS} }} }} }}",
        {"id": issue_id, "input": {"stateId": states[0]["id"]}},
    )
    issue = data["issueUpdate"]["issue"]
    dump(issue if args.json else f"{issue['identifier']} → {issue['state']['name']}", args.json)


def cmd_comment(args):
    issue_id = get_issue_id(args.issue)
    data = graphql(
        "mutation($input:CommentCreateInput!){ commentCreate(input:$input){ success comment { id url body } } }",
        {"input": {"issueId": issue_id, "body": args.body}},
    )
    comment = data["commentCreate"]["comment"]
    dump(comment if args.json else comment.get("url", comment["id"]), args.json)


def cmd_query(args):
    variables = json.loads(args.variables) if args.variables else {}
    dump(graphql(args.graphql, variables), True)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="linear", description="Small Linear CLI shim (lazylinear)")
    p.add_argument("--json", action="store_true", help="output JSON")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("viewer", help="show authenticated user/org")
    sp.set_defaults(func=cmd_viewer)

    sp = sub.add_parser("teams", help="list teams")
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_teams)

    sp = sub.add_parser("states", help="list workflow states for a team")
    sp.add_argument("team")
    sp.set_defaults(func=cmd_states)

    sp = sub.add_parser("issues", help="list issues")
    sp.add_argument("--team", default=None, help="team key, e.g. EDU")
    sp.add_argument("--limit", type=int, default=25)
    sp.set_defaults(func=cmd_issues)

    sp = sub.add_parser("read", help="read issue by identifier")
    sp.add_argument("issue")
    sp.set_defaults(func=cmd_read)

    sp = sub.add_parser("create", help="create issue")
    sp.add_argument("title")
    sp.add_argument("--team", required=True)
    sp.add_argument("--description", default=None)
    sp.add_argument("--state", default=None)
    sp.add_argument("--label", action="append", default=[])
    sp.set_defaults(func=cmd_create)

    sp = sub.add_parser("move", help="move issue to state by name")
    sp.add_argument("issue")
    sp.add_argument("state")
    sp.set_defaults(func=cmd_move)

    sp = sub.add_parser("comment", help="add comment to issue")
    sp.add_argument("issue")
    sp.add_argument("body")
    sp.set_defaults(func=cmd_comment)

    sp = sub.add_parser("query", help="run raw GraphQL")
    sp.add_argument("graphql")
    sp.add_argument("--variables", default=None, help="JSON variables")
    sp.set_defaults(func=cmd_query)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except LinearError as e:
        print(f"linear: error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
