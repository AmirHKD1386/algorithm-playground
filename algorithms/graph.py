"""Graph algorithms: BFS, DFS, Dijkstra, A*, Kruskal, Prim.

Graph format: adjacency list ``{node: [(neighbor, weight), ...]}``.
Node ids are ints 0..n-1 in the playground, but code works for any hashable.

BFS/DFS/Dijkstra/A* are implemented once here as shared *search cores*
(``search_*``) returning ``(visit_order, prev, ...)``. The public wrappers
(``bfs``, ``dijkstra``, …) keep the classic signatures, and the grid
front-end in :mod:`algorithms.pathfinding` reuses the same cores through a
grid→adjacency adapter — one implementation, two views.
"""

from __future__ import annotations

import heapq
from collections import deque
from typing import Dict, Hashable, List, Tuple

Adj = Dict[Hashable, List[Tuple[Hashable, float]]]


# ------------------------------------------------- shared search cores ------
def search_bfs(adj: Adj, start, goal=None) -> Tuple[List, Dict]:
    """BFS core — returns ``(visit_order, prev)``. Stops early once ``goal`` pops."""
    seen = {start}
    prev: Dict = {}
    order: List = []
    q = deque([start])
    while q:
        u = q.popleft()
        order.append(u)
        if u == goal:
            break
        for v, _ in adj.get(u, []):
            if v not in seen:
                seen.add(v)
                prev[v] = u
                q.append(v)
    return order, prev


def search_dfs(adj: Adj, start, goal=None) -> Tuple[List, Dict]:
    """DFS core — returns ``(visit_order, prev)``. Marks nodes discovered on push."""
    seen = {start}
    prev: Dict = {}
    order: List = []
    stack = [start]
    while stack:
        u = stack.pop()
        order.append(u)
        if u == goal:
            break
        for v, _ in adj.get(u, []):
            if v not in seen:
                seen.add(v)
                prev[v] = u
                stack.append(v)
    return order, prev


def search_dijkstra(adj: Adj, start, goal=None) -> Tuple[List, Dict, Dict]:
    """Dijkstra core — returns ``(visit_order, prev, dist)``. Early stop at ``goal``."""
    dist: Dict = {u: float("inf") for u in adj}
    dist[start] = 0
    prev: Dict = {}
    pq: List[Tuple[float, Hashable]] = [(0, start)]
    seen: set = set()
    order: List = []
    while pq:
        d, u = heapq.heappop(pq)
        if u in seen:
            continue
        seen.add(u)
        order.append(u)
        if u == goal:
            break
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return order, prev, dist


def _zero_heuristic(a, b) -> float:
    """Admissible zero heuristic — A* with this degrades to Dijkstra."""
    return 0.0


def search_astar(adj: Adj, start, goal, heuristic=None) -> Tuple[List, Dict, Dict]:
    """A* core — returns ``(visit_order, prev, g)``.

    Optimal when ``heuristic`` is admissible (never overestimates).
    """
    if heuristic is None:
        heuristic = _zero_heuristic
    open_pq: List[Tuple[float, float, Hashable]] = [(heuristic(start, goal), 0, start)]
    g: Dict = {start: 0}
    prev: Dict = {}
    closed: set = set()
    order: List = []
    while open_pq:
        _, g_u, u = heapq.heappop(open_pq)
        if u in closed:
            continue
        closed.add(u)
        order.append(u)
        if u == goal:
            break
        for v, w in adj.get(u, []):
            ng = g_u + w
            if ng < g.get(v, float("inf")):
                g[v] = ng
                prev[v] = u
                heapq.heappush(open_pq, (ng + heuristic(v, goal), ng, v))
    return order, prev, g


def reconstruct_path(prev: Dict, start, goal) -> List:
    """Rebuild path goal←…←start from a ``prev`` map. Empty if unreachable."""
    if goal == start:
        return [start]
    if goal not in prev:
        return []
    path = [goal]
    while path[-1] != start:
        p = prev.get(path[-1])
        if p is None:
            return []
        path.append(p)
    return path[::-1]


# ------------------------------------------------- public API (classic) -----
def bfs(adj: Adj, start) -> List:
    """Breadth-First Search — level by level with a queue. O(V+E)."""
    return search_bfs(adj, start)[0]


def dfs(adj: Adj, start) -> List:
    """Depth-First Search — go deep before wide (iterative). O(V+E)."""
    return search_dfs(adj, start)[0]


def dijkstra(adj: Adj, start) -> Tuple[Dict, Dict]:
    """Dijkstra — shortest paths from ``start`` (non-negative weights). O(E log V)."""
    _, prev, dist = search_dijkstra(adj, start)
    return dist, prev


def astar(adj: Adj, start, goal, heuristic=None) -> Tuple[List, float]:
    """A* — Dijkstra + heuristic guiding toward goal. Optimal if h is admissible."""
    _, prev, g = search_astar(adj, start, goal, heuristic)
    return reconstruct_path(prev, start, goal), g.get(goal, float("inf"))


# ------------------------------------------------------- Kruskal / Prim ----
def _all_edges(adj: Adj) -> List[Tuple[float, Hashable, Hashable]]:
    edges = []
    seen = set()
    for u, nbs in adj.items():
        for v, w in nbs:
            if (v, u) not in seen:
                edges.append((w, u, v))
                seen.add((u, v))
    return edges


class _DSU:
    def __init__(self, nodes):
        self.p = {n: n for n in nodes}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.p[rb] = ra
        return True


def kruskal(adj: Adj) -> Tuple[List[Tuple], float]:
    """Kruskal — sort edges, greedily add if no cycle (Union-Find). O(E log E)."""
    dsu = _DSU(list(adj.keys()))
    mst: List[Tuple] = []
    total = 0.0
    for w, u, v in sorted(_all_edges(adj)):
        if dsu.union(u, v):
            mst.append((u, v, w))
            total += w
    return mst, total


def prim(adj: Adj, start=None) -> Tuple[List[Tuple], float]:
    """Prim — grow MST outward from start, always cheapest frontier edge. O(E log V)."""
    nodes = list(adj.keys())
    if not nodes:
        return [], 0.0
    start = start if start in adj else nodes[0]
    in_mst = {start}
    mst: List[Tuple] = []
    total = 0.0
    pq: List[Tuple[float, Hashable, Hashable]] = []
    for v, w in adj[start]:
        heapq.heappush(pq, (w, start, v))
    while pq and len(in_mst) < len(nodes):
        w, u, v = heapq.heappop(pq)
        if v in in_mst:
            continue
        in_mst.add(v)
        mst.append((u, v, w))
        total += w
        for to, w2 in adj.get(v, []):
            if to not in in_mst:
                heapq.heappush(pq, (w2, v, to))
    return mst, total
