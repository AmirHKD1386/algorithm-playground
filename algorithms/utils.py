"""Shared helpers: random data generation, timing, formatting.

Every helper here is intentionally tiny so the Streamlit app and the
Rich CLI can share the exact same benchmarking logic.
"""

from __future__ import annotations

import random
import string
import timeit
from typing import Callable, Dict, List


def generate_random_array(n: int, low: int = 0, high: int = 100, seed: int | None = None) -> List[int]:
    """Return a list of ``n`` random ints in ``[low, high]``."""
    rng = random.Random(seed)
    return [rng.randint(low, high) for _ in range(n)]


def generate_random_text(length: int = 500, seed: int | None = None) -> str:
    """Random lowercase text (with spaces) for string-algorithm demos."""
    rng = random.Random(seed)
    letters = string.ascii_lowercase + "     "
    return "".join(rng.choice(letters) for _ in range(length))


def generate_random_graph(n: int = 8, p: float = 0.35, weighted: bool = True,
                          seed: int | None = None) -> Dict[int, List[tuple]]:
    """Erdos-Renyi style undirected graph as adjacency list.

    Returns ``{node: [(neighbor, weight), ...]}``. Guaranteed connected
    by first building a random spanning tree, then adding extra edges.
    """
    rng = random.Random(seed)
    adj: Dict[int, List[tuple]] = {i: [] for i in range(n)}

    def add_edge(u: int, v: int):
        w = rng.randint(1, 9) if weighted else 1
        if all(nb != v for nb, _ in adj[u]):
            adj[u].append((v, w))
            adj[v].append((u, w))

    # spanning tree -> connectivity
    nodes = list(range(n))
    rng.shuffle(nodes)
    for i in range(1, n):
        add_edge(nodes[i], rng.choice(nodes[:i]))
    # extra random edges
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                add_edge(u, v)
    return adj


def generate_maze(rows: int = 15, cols: int = 21, wall_prob: float = 0.28,
                  seed: int | None = None) -> List[List[int]]:
    """Random maze grid: 0 = free, 1 = wall.

    Start ``(0, 0)`` and goal ``(rows-1, cols-1)`` are always free, and a
    path between them is guaranteed: if random walls seal the goal off,
    a corridor is carved through them.
    """
    rng = random.Random(seed)
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    start, goal = (0, 0), (rows - 1, cols - 1)
    for r in range(rows):
        for c in range(cols):
            if (r, c) == start or (r, c) == goal:
                continue
            if rng.random() < wall_prob:
                grid[r][c] = 1
    if not _has_open_path(grid, start, goal):
        _carve_path(grid, start, goal, rng)
    return grid


def _has_open_path(grid: List[List[int]], start: tuple, goal: tuple) -> bool:
    """True if ``goal`` is reachable from ``start`` through free cells."""
    rows, cols = len(grid), len(grid[0])
    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        if (r, c) == goal:
            return True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in seen and grid[nr][nc] == 0):
                seen.add((nr, nc))
                stack.append((nr, nc))
    return False


def _carve_path(grid: List[List[int]], start: tuple, goal: tuple,
                rng: random.Random) -> None:
    """Clear walls along a randomized path from start to goal (always exists
    when movement ignores walls)."""
    rows, cols = len(grid), len(grid[0])
    stack = [start]
    prev: Dict[tuple, tuple | None] = {start: None}
    while stack:
        u = stack.pop()
        if u == goal:
            break
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rng.shuffle(dirs)
        for dr, dc in dirs:
            v = (u[0] + dr, u[1] + dc)
            if 0 <= v[0] < rows and 0 <= v[1] < cols and v not in prev:
                prev[v] = u
                stack.append(v)
    node: tuple | None = goal
    while node is not None:
        grid[node[0]][node[1]] = 0
        node = prev.get(node)


def benchmark(func: Callable, *args, repeats: int = 5, number: int = 1, **kwargs) -> Dict[str, float]:
    """Time ``func(*args)`` with :mod:`timeit` and return stats in milliseconds."""
    timer = timeit.Timer(lambda: func(*args, **kwargs))
    raw = timer.repeat(repeat=repeats, number=number)
    per_run_ms = [t / number * 1000.0 for t in raw]
    return {
        "best_ms": min(per_run_ms),
        "avg_ms": sum(per_run_ms) / len(per_run_ms),
        "worst_ms": max(per_run_ms),
    }


def format_ms(ms: float) -> str:
    if ms < 1:
        return f"{ms * 1000:.1f} µs"
    if ms < 1000:
        return f"{ms:.2f} ms"
    return f"{ms / 1000:.2f} s"


def parse_int_list(text: str) -> List[int]:
    """Parse '3, 1, 4, 1, 5' -> [3, 1, 4, 1, 5]. Raises ValueError on bad tokens."""
    tokens = [t.strip() for t in text.replace(";", ",").split(",") if t.strip()]
    if not tokens:
        raise ValueError("Empty input.")
    return [int(t) for t in tokens]
