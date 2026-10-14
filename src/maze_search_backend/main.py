from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import MazeRequest, SearchResponse
from .search import build_bfs_search, build_dfs_search

app = FastAPI(title="Maze Search API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
def search_maze(
    maze: MazeRequest,
    algorithm: Literal["bfs", "dfs"] = "bfs",
) -> SearchResponse:
    search = build_dfs_search if algorithm == "dfs" else build_bfs_search
    return search(maze)
