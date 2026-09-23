"""Grid pathfinding / maze solving: BFS, DFS, Dijkstra, A* on 2-D grids.

Grid convention: ``0`` = free cell, ``1`` = wall.

No search logic lives here: a thin grid→adjacency adapter feeds the shared
search cores in :mod:`algorithms.graph`, and paths are rebuilt with the one
shared ``reconstruct_path`` — one implementation, two views.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

from .graph import (
    Adj,
    reconstruct_path,
    search_astar,
    search_bfs,
    search_dfs,
    search_dijkstra,
)

Coord = Tuple[int, int]
Grid = List[List[int]]

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# Back-compat alias — the single shared reconstruction lives in graph.py.
reconstruct = reconstruct_path


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def grid_to_adjacency(grid: Grid, cost: Callable[[Coord], float] | None = None,
                      ensure: Tuple[Coord, ...] = ()) -> Adj:
    """Adapter: free cells of ``grid`` become an adjacency list of coord nodes.

    - ``cost(v)`` sets the weight of *entering* cell ``v`` (default 1).
    - ``ensure`` lists cells to include even if walled (the start cell), with
      edges to free neighbours — matching classic grid-search semantics.
    """
    rows, cols = len(grid), len(grid[0])
    ensure_set = set(ensure)

    def weight(v: Coord) -> float:
        return 1.0 if cost is None else cost(v)

    nodes = {(r, c) for r in range(rows) for c in range(cols)
             if grid[r][c] == 0} | ensure_set
    adj: Adj = {n: [] for n in nodes}
    for cell in nodes:
        r, c = cell
        for dr, dc in DIRS:
            v = (r + dr, c + dc)
            if v in nodes:
                adj[cell].append((v, weight(v)))
    return adj


def bfs_grid(grid: Grid, start: Coord, goal: Coord) -> Tuple[List[Coord], List[Coord]]:
    """BFS on grid — guarantees shortest path (unweighted). Returns (path, visit_order)."""
    adj = grid_to_adjacency(grid, ensure=(start,))
    order, prev = search_bfs(adj, start, goal)
    return reconstruct_path(prev, start, goal), order


def dfs_grid(grid: Grid, start: Coord, goal: Coord) -> Tuple[List[Coord], List[Coord]]:
    """DFS on grid — fast but path is NOT shortest. Returns (path, visit_order)."""
    adj = grid_to_adjacency(grid, ensure=(start,))
    order, prev = search_dfs(adj, start, goal)
    return reconstruct_path(prev, start, goal), order


def dijkstra_grid(grid: Grid, start: Coord, goal: Coord,
                  cost: Callable[[Coord], float] | None = None
                  ) -> Tuple[List[Coord], List[Coord], float]:
    """Dijkstra on grid with optional per-cell cost. Returns (path, order, cost)."""
    adj = grid_to_adjacency(grid, cost=cost, ensure=(start,))
    order, prev, dist = search_dijkstra(adj, start, goal)
    return reconstruct_path(prev, start, goal), order, dist.get(goal, float("inf"))


def astar_grid(grid: Grid, start: Coord, goal: Coord) -> Tuple[List[Coord], List[Coord]]:
    """A* on grid with Manhattan heuristic — fast + optimal (uniform cost)."""
    adj = grid_to_adjacency(grid, ensure=(start,))
    order, prev, _ = search_astar(adj, start, goal, manhattan)
    return reconstruct_path(prev, start, goal), order


PATH_FUNCS = {"bfs": bfs_grid, "dfs": dfs_grid, "dijkstra": dijkstra_grid, "astar": astar_grid}
