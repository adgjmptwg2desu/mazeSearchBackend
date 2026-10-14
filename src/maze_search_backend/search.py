import networkx as nx
from collections import deque

from .schemas import (
    MazeRequest,
    Position,
    SearchResponse,
    SearchStep,
    SearchTreeNode,
    SearchTreeState,
)


def _node_id(position: tuple[int, int]) -> str:
    row, column = position
    return f"{column},{row}"


def _build_search(maze: MazeRequest, depth_first: bool) -> SearchResponse:
    height = len(maze.cells)
    width = len(maze.cells[0])
    graph = nx.grid_2d_graph(height, width)
    walls = [
        (row, column)
        for row, cells in enumerate(maze.cells)
        for column, cell in enumerate(cells)
        if cell == "wall"
    ]
    graph.remove_nodes_from(walls)

    start = (maze.startPosition.y, maze.startPosition.x)
    goal = (maze.goalPosition.y, maze.goalPosition.x)
    traversal_order = [start]
    visited = {start}
    parent_by_node: dict[
        tuple[int, int], tuple[int, int] | None
    ] = {start: None}
    depth_by_node = {start: 0}
    steps: list[SearchStep] = []
    expanded_node_count = 0
    found = False

    if depth_first:
        if start == goal:
            found = True
            steps.append(SearchStep(action="goal", nodeId=_node_id(start)))
        else:
            expanded_node_count += 1
            steps.append(SearchStep(action="expand", nodeId=_node_id(start)))
            stack = [(start, iter(graph.neighbors(start)))]

            while stack:
                node, neighbors = stack[-1]
                child = next((neighbor for neighbor in neighbors if neighbor not in visited), None)

                if child is None:
                    stack.pop()
                    if stack:
                        steps.append(
                            SearchStep(action="backtrack", nodeId=_node_id(stack[-1][0]))
                        )
                    continue

                visited.add(child)
                traversal_order.append(child)
                parent_by_node[child] = node
                depth_by_node[child] = depth_by_node[node] + 1

                if child == goal:
                    found = True
                    steps.append(SearchStep(action="goal", nodeId=_node_id(child)))
                    break

                expanded_node_count += 1
                steps.append(SearchStep(action="expand", nodeId=_node_id(child)))
                stack.append((child, iter(graph.neighbors(child))))
    else:
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node == goal:
                found = True
                steps.append(SearchStep(action="goal", nodeId=_node_id(node)))
                break

            expanded_node_count += 1
            steps.append(SearchStep(action="expand", nodeId=_node_id(node)))
            for child in graph.neighbors(node):
                if child in visited:
                    continue
                visited.add(child)
                traversal_order.append(child)
                parent_by_node[child] = node
                depth_by_node[child] = depth_by_node[node] + 1
                queue.append(child)

    nodes = []
    for node in traversal_order:
        row, column = node
        parent = parent_by_node[node]
        parent_id = _node_id(parent) if parent is not None else None
        depth = depth_by_node[node]
        node_id = _node_id(node)
        is_start = node == start
        is_goal = node == goal

        nodes.append(
            SearchTreeNode(
                id=node_id,
                label="S" if is_start else "G" if is_goal else node_id,
                position=Position(x=column, y=row),
                parentId=parent_id,
                depth=depth,
                visited=True,
                onPath=False,
            )
        )

    path_positions = []
    if found:
        current = goal
        while current is not None:
            path_positions.append(current)
            current = parent_by_node[current]
        path_positions.reverse()
    path_ids = [_node_id(position) for position in path_positions]
    path_id_set = set(path_ids)

    for node in nodes:
        node.onPath = node.id in path_id_set

    return SearchResponse(
        found=found,
        expandedNodeCount=expanded_node_count,
        steps=steps,
        state=SearchTreeState(
            nodes=nodes,
            activeNodeIds=[_node_id(position) for position in traversal_order],
            pathNodeIds=path_ids,
        ),
    )


def build_bfs_search(maze: MazeRequest) -> SearchResponse:
    """Build a breadth-first search tree and shortest path for a maze."""
    return _build_search(maze, depth_first=False)


def build_dfs_search(maze: MazeRequest) -> SearchResponse:
    """Build a depth-first search tree and the path found by DFS."""
    return _build_search(maze, depth_first=True)
