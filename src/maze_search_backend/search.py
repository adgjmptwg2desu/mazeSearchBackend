import networkx as nx

from .schemas import MazeRequest, Position, SearchResponse, SearchTreeNode, SearchTreeState


def _node_id(position: tuple[int, int]) -> str:
    row, column = position
    return f"{column},{row}"


def build_bfs_search(maze: MazeRequest) -> SearchResponse:
    """Build a BFS search tree and shortest path for a maze."""
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
    tree = nx.bfs_tree(graph, source=start)
    traversal_order = list(tree.nodes)
    found = goal in tree

    if found:
        traversal_order = traversal_order[: traversal_order.index(goal) + 1]

    included_nodes = set(traversal_order)
    parent_by_node = {
        node: next(tree.predecessors(node), None)
        for node in traversal_order
    }
    depth_by_node: dict[tuple[int, int], int] = {start: 0}
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

        for child in tree.successors(node):
            if child in included_nodes and child not in depth_by_node:
                depth_by_node[child] = depth + 1

    path_positions = (
        nx.shortest_path(tree, source=start, target=goal) if found else []
    )
    path_ids = [_node_id(position) for position in path_positions]
    path_id_set = set(path_ids)

    for node in nodes:
        node.onPath = node.id in path_id_set

    return SearchResponse(
        found=found,
        state=SearchTreeState(
            nodes=nodes,
            activeNodeIds=[_node_id(position) for position in traversal_order],
            pathNodeIds=path_ids,
        ),
    )
