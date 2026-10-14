from fastapi.testclient import TestClient

from maze_search_backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_endpoint_returns_frontend_search_tree_shape():
    response = client.post(
        "/api/search",
        json={
            "cells": [["start", "goal"]],
            "startPosition": {"x": 0, "y": 0},
            "goalPosition": {"x": 1, "y": 0},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["state"]["pathNodeIds"] == ["0,0", "1,0"]
    assert body["state"]["nodes"][1]["parentId"] == "0,0"
    assert body["expandedNodeCount"] == 1
    assert body["expandedNodeCount"] == sum(
        step["action"] == "expand" for step in body["steps"]
    )


def test_search_endpoint_rejects_wall_start():
    response = client.post(
        "/api/search",
        json={
            "cells": [["wall", "goal"]],
            "startPosition": {"x": 0, "y": 0},
            "goalPosition": {"x": 1, "y": 0},
        },
    )

    assert response.status_code == 422


def test_search_endpoint_accepts_depth_first_algorithm():
    response = client.post(
        "/api/search?algorithm=dfs",
        json={
            "cells": [
                ["start", "path", "goal"],
                ["path", "path", "path"],
                ["path", "path", "path"],
            ],
            "startPosition": {"x": 0, "y": 0},
            "goalPosition": {"x": 2, "y": 0},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert len(body["state"]["pathNodeIds"]) > 3
    assert body["expandedNodeCount"] == sum(
        step["action"] == "expand" for step in body["steps"]
    )
