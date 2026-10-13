from maze_search_backend.schemas import MazeRequest
from maze_search_backend.search import build_bfs_search


def test_bfs_returns_search_tree_and_shortest_path():
    maze = MazeRequest(
        cells=[
            ["start", "path", "goal"],
            ["path", "path", "path"],
        ],
        startPosition={"x": 0, "y": 0},
        goalPosition={"x": 2, "y": 0},
    )

    result = build_bfs_search(maze)

    assert result.found is True
    assert result.state.pathNodeIds == ["0,0", "1,0", "2,0"]
    assert result.state.nodes[0].label == "S"
    assert result.state.nodes[-1].label == "G"
    assert all(node.visited for node in result.state.nodes)
    assert all(node.onPath for node in result.state.nodes if node.id in result.state.pathNodeIds)


def test_bfs_returns_reachable_tree_when_goal_is_blocked_off():
    maze = MazeRequest(
        cells=[
            ["start", "wall", "goal"],
            ["path", "wall", "path"],
        ],
        startPosition={"x": 0, "y": 0},
        goalPosition={"x": 2, "y": 0},
    )

    result = build_bfs_search(maze)

    assert result.found is False
    assert result.state.pathNodeIds == []
    assert result.state.activeNodeIds == ["0,0", "0,1"]
