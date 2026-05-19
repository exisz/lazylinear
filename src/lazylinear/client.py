from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.linear.app/graphql"


class LinearError(RuntimeError):
    pass


def _read_token_file() -> str | None:
    path = Path(os.environ.get("LAZYLINEAR_TOKEN_FILE", "~/.config/lazylinear/token")).expanduser()
    if path.exists():
        token = path.read_text().strip()
        return token or None
    return None


def _read_roblocks_token() -> str | None:
    store = os.environ.get("LAZYLINEAR_ROBLOCKS_STORE", "edux")
    key = os.environ.get("LAZYLINEAR_ROBLOCKS_KEY", "linear_app_token")
    try:
        result = subprocess.run(
            ["roblocks", "get", store, key],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    token = result.stdout.strip()
    return token or None


def get_token() -> str:
    token = os.environ.get("LINEAR_API_KEY") or os.environ.get("LINEAR_TOKEN") or _read_token_file() or _read_roblocks_token()
    if not token:
        raise LinearError(
            "Linear token not found. Set LINEAR_API_KEY, write ~/.config/lazylinear/token, "
            "or configure roblocks edux/linear_app_token."
        )
    return token


def graphql(query: str, variables: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": token or get_token(),
            "Content-Type": "application/json",
            "User-Agent": "lazylinear/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise LinearError(f"Linear HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise LinearError(f"Linear request failed: {e}") from e

    if data.get("errors"):
        raise LinearError(json.dumps(data["errors"], ensure_ascii=False, indent=2))
    return data.get("data", {})
