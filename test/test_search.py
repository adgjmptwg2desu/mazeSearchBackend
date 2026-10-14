from maze_search_backend.schemas import MazeRequest
from maze_search_backend.search import build_bfs_search, build_dfs_search


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
    assert any(node.label == "G" for node in result.state.nodes)
    assert all(node.visited for node in result.state.nodes)
    assert all(node.onPath for node in result.state.nodes if node.id in result.state.pathNodeIds)
    assert result.expandedNodeCount == sum(
        step.action == "expand" for step in result.steps
    )


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
    assert result.expandedNodeCount == 2


def test_dfs_returns_depth_first_path_and_search_tree():
    maze = MazeRequest(
        cells=[
            ["start", "path", "goal"],
            ["path", "path", "path"],
            ["path", "path", "path"],
        ],
        startPosition={"x": 0, "y": 0},
        goalPosition={"x": 2, "y": 0},
    )

    breadth_first = build_bfs_search(maze)
    depth_first = build_dfs_search(maze)

    assert depth_first.found is True
    assert depth_first.state.pathNodeIds[0] == "0,0"
    assert depth_first.state.pathNodeIds[-1] == "2,0"
    assert len(depth_first.state.pathNodeIds) > len(breadth_first.state.pathNodeIds)
    assert depth_first.state.activeNodeIds[1] == "0,1"
    assert depth_first.steps[-1].nodeId == "2,0"
    assert depth_first.expandedNodeCount == sum(
        step.action == "expand" for step in depth_first.steps
    )


def test_dfs_backtracks_from_dead_end_before_continuing_to_goal():
    maze = MazeRequest(
        cells=[
            ["start", "path", "goal"],
            ["path", "wall", "wall"],
            ["wall", "wall", "wall"],
        ],
        startPosition={"x": 0, "y": 0},
        goalPosition={"x": 2, "y": 0},
    )

    result = build_dfs_search(maze)

    assert [(step.action, step.nodeId) for step in result.steps] == [
        ("expand", "0,0"),
        ("expand", "0,1"),
        ("backtrack", "0,0"),
        ("expand", "1,0"),
        ("goal", "2,0"),
    ]


def test_dfs_backtracks_to_start_after_exhausting_unreachable_maze():
    maze = MazeRequest(
        cells=[
            ["start", "wall", "goal"],
            ["path", "wall", "path"],
        ],
        startPosition={"x": 0, "y": 0},
        goalPosition={"x": 2, "y": 0},
    )

    result = build_dfs_search(maze)

    assert result.found is False
    assert [step.action for step in result.steps] == [
        "expand",
        "expand",
        "backtrack",
    ]
    assert result.steps[-1].nodeId == "0,0"
    assert result.expandedNodeCount == 2
