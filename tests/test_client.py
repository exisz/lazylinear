from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from lazylinear import client
from lazylinear.client import LinearError


def test_get_token_prefers_environment(monkeypatch, tmp_path):
    token_file = tmp_path / "token"
    token_file.write_text("file-token\n")
    monkeypatch.setenv("LINEAR_API_KEY", "env-token")
    monkeypatch.setenv("LAZYLINEAR_TOKEN_FILE", str(token_file))

    assert client.get_token() == "env-token"


def test_get_token_reads_token_file(monkeypatch, tmp_path):
    token_file = tmp_path / "token"
    token_file.write_text("file-token\n")
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.delenv("LINEAR_TOKEN", raising=False)
    monkeypatch.setenv("LAZYLINEAR_TOKEN_FILE", str(token_file))
    monkeypatch.setattr(client, "_read_roblocks_token", lambda: None)

    assert client.get_token() == "file-token"


def test_get_token_falls_back_to_roblocks(monkeypatch, tmp_path):
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.delenv("LINEAR_TOKEN", raising=False)
    monkeypatch.setenv("LAZYLINEAR_TOKEN_FILE", str(tmp_path / "missing"))
    monkeypatch.setattr(client, "_read_roblocks_token", lambda: "vault-token")

    assert client.get_token() == "vault-token"


def test_get_token_raises_when_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.delenv("LINEAR_TOKEN", raising=False)
    monkeypatch.setenv("LAZYLINEAR_TOKEN_FILE", str(tmp_path / "missing"))
    monkeypatch.setattr(client, "_read_roblocks_token", lambda: None)

    with pytest.raises(LinearError, match="Linear token not found"):
        client.get_token()


def test_read_roblocks_token_uses_configured_store_and_key(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0, stdout="secret\n", stderr="")

    monkeypatch.setenv("LAZYLINEAR_ROBLOCKS_STORE", "custom-store")
    monkeypatch.setenv("LAZYLINEAR_ROBLOCKS_KEY", "custom-key")
    monkeypatch.setattr(subprocess, "run", fake_run)

    assert client._read_roblocks_token() == "secret"
    assert calls[0][0] == ["roblocks", "get", "custom-store", "custom-key"]
    assert calls[0][1]["timeout"] == 10


def test_graphql_returns_data(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"data": {"viewer": {"name": "Exis"}}}).encode()

    def fake_urlopen(req, timeout):
        assert timeout == 30
        assert req.headers["Authorization"] == "token"
        return FakeResponse()

    monkeypatch.setattr(client.urllib.request, "urlopen", fake_urlopen)

    assert client.graphql("{ viewer { name } }", token="token") == {"viewer": {"name": "Exis"}}


def test_graphql_raises_on_graphql_errors(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"errors": [{"message": "bad"}]}).encode()

    monkeypatch.setattr(client.urllib.request, "urlopen", lambda *_args, **_kwargs: FakeResponse())

    with pytest.raises(LinearError, match="bad"):
        client.graphql("query", token="token")
