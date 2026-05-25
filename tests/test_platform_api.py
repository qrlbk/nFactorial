"""Tests for platform API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_discover_tweets_mock():
    resp = client.get("/discover", params={"source": "tweets", "q": "RAG"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "tweets"
    assert len(data["items"]) >= 1


def test_launch_queue_empty():
    resp = client.get("/launch/queue")
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_voices_list():
    resp = client.get("/voices")
    assert resp.status_code == 200
    assert "voices" in resp.json()


def test_generate_hooks_validation():
    resp = client.post("/generate/hooks", json={"draft": "Short"})
    assert resp.status_code == 422
