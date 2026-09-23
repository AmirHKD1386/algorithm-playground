"""Central registry: every algorithm's display metadata AND its callable.

The Streamlit app and Rich CLI both read from ALGORITHMS so names,
complexities and explanations stay consistent everywhere — and resolve
implementations through :func:`get_function` / :func:`get_steps`, so this
module is the single source of truth for all 30 algorithms.
"""

from __future__ import annotations

ALGORITHMS = {
    # ---------------- Sorting ----------------
    "bubble": {
        "name": "Bubble Sort", "category": "Sorting",
        "time": "O(n²) avg/worst, O(n) best", "space": "O(1)",
        "difficulty": "Beginner",
        "explanation": "Repeatedly steps through the list, compares neighbours and swaps "
                       "them if out of order. Big values 'bubble' to the end each pass.",
        "best_for": "Teaching; tiny or nearly-sorted lists (early-exit).",
    },
    "selection": {
        "name": "Selection Sort", "category": "Sorting",
        "time": "O(n²) always", "space": "O(1)",
        "difficulty": "Beginner",
        "explanation": "Divides the array into sorted/unsorted parts; each pass selects the "
                       "minimum of the unsorted part and swaps it to the boundary.",
        "best_for": "Minimizing writes (at most n swaps).",
    },
    "insertion": {
        "name": "Insertion Sort", "category": "Sorting",
        "time": "O(n²) avg/worst, O(n) best", "space": "O(1)",
        "difficulty": "Beginner",
        "explanation": "Builds a sorted hand like playing cards: take each new element and "
                       "insert it into the correct spot of the sorted prefix.",
        "best_for": "Small / nearly-sorted data; the inner loop of Timsort.",
    },
    "merge": {
        "name": "Merge Sort", "category": "Sorting",
        "time": "O(n log n) always", "space": "O(n)",
        "difficulty": "Intermediate",
        "explanation": "Divide & conquer: split in half, recursively sort each half, then "
                       "merge the two sorted halves. Stable and predictable.",
        "best_for": "Linked lists, stable sorting, guaranteed n log n.",
    },
    "quick": {
        "name": "Quick Sort", "category": "Sorting",
        "time": "O(n log n) avg, O(n²) worst", "space": "O(log n)",
        "difficulty": "Intermediate",
        "explanation": "Pick a pivot, partition so smaller values go left and larger go right, "
                       "then recurse. Blazing fast in practice with good pivots.",
        "best_for": "General-purpose in-memory sorting.",
    },
    "heap": {
        "name": "Heap Sort", "category": "Sorting",
        "time": "O(n log n) always", "space": "O(1)",
        "difficulty": "Intermediate",
        "explanation": "Turn the array into a max-heap, then repeatedly extract the maximum "
                       "to the end. In-place with guaranteed n log n.",
        "best_for": "Memory-tight guaranteed n log n; priority queues.",
    },
    "timsort": {
        "name": "Timsort (Python sorted)", "category": "Sorting",
        "time": "O(n log n) avg/worst, O(n) best", "space": "O(n)",
        "difficulty": "Advanced",
        "explanation": "Python's real sorted(): finds natural runs, insertion-sorts short runs, "
                       "then merges. Adaptive — flies on partially-ordered data.",
        "best_for": "Real-world data (this is what sorted() uses).",
    },
    # ---------------- Searching ----------------
    "linear": {
        "name": "Linear Search", "category": "Searching",
        "time": "O(n)", "space": "O(1)",
        "difficulty": "Beginner",
        "explanation": "Check each element left→right until you find the target. Works on "
                       "anything, sorted or not.",
        "best_for": "Unsorted / tiny lists.",
    },
    "binary": {
        "name": "Binary Search", "category": "Searching",
        "time": "O(log n)", "space": "O(1)",
        "difficulty": "Beginner",
        "explanation": "On a sorted list, look at the middle: if the target is smaller go left, "
                       "else go right. Halves the search space every step.",
        "best_for": "Sorted arrays; the classic log-n lookup.",
    },
    "jump": {
        "name": "Jump Search", "category": "Searching",
        "time": "O(√n)", "space": "O(1)",
        "difficulty": "Intermediate",
        "explanation": "Jump ahead in √n-sized blocks until the block containing the target is "
                       "found, then linear-scan inside the block.",
        "best_for": "Sorted data where binary jumps are expensive (e.g. linked structures).",
    },
    "interpolation": {
        "name": "Interpolation Search", "category": "Searching",
        "time": "O(log log n) avg (uniform), O(n) worst", "space": "O(1)",
        "difficulty": "Intermediate",
        "explanation": "Like guessing a word in a dictionary: estimate the target's position "
                       "proportionally instead of always picking the middle.",
        "best_for": "Uniformly distributed sorted numeric data.",
    },
    # ---------------- Graph ----------------
    "bfs": {
        "name": "BFS (graphs)", "category": "Graph",
        "time": "O(V + E)", "space": "O(V)",
        "difficulty": "Beginner",
        "explanation": "Breadth-First Search explores level by level with a queue — finds the "
                       "shortest path in unweighted graphs.",
        "best_for": "Shortest path (unweighted), level-order traversal.",
    },
    "dfs": {
        "name": "DFS (graphs)", "category": "Graph",
        "time": "O(V + E)", "space": "O(V)",
        "difficulty": "Beginner",
        "explanation": "Depth-First Search dives down one path with a stack before backtracking. "
                       "Great for connectivity, cycles, topological sort.",
        "best_for": "Connectivity, cycle detection, maze carving.",
    },
    "dijkstra": {
        "name": "Dijkstra", "category": "Graph",
        "time": "O(E log V)", "space": "O(V)",
        "difficulty": "Intermediate",
        "explanation": "Always finalizes the closest unvisited node (priority queue) and relaxes "
                       "its edges. Optimal for non-negative weights.",
        "best_for": "Shortest paths with non-negative weights (maps, networks).",
    },
    "astar": {
        "name": "A*", "category": "Graph",
        "time": "O(E log V) typical (heuristic-dependent)", "space": "O(V)",
        "difficulty": "Advanced",
        "explanation": "Dijkstra guided by a heuristic (e.g. straight-line distance). With an "
                       "admissible heuristic it is optimal and explores far less.",
        "best_for": "Game pathfinding, robotics, maps with a goal.",
    },
    "kruskal": {
        "name": "Kruskal (MST)", "category": "Graph",
        "time": "O(E log E)", "space": "O(V)",
        "difficulty": "Intermediate",
        "explanation": "Sorts all edges and greedily adds the cheapest one that doesn't form a "
                       "cycle (Union-Find). Builds a Minimum Spanning Tree.",
        "best_for": "MST on sparse graphs; clustering.",
    },
    "prim": {
        "name": "Prim (MST)", "category": "Graph",
        "time": "O(E log V)", "space": "O(V)",
        "difficulty": "Intermediate",
        "explanation": "Grows the MST from a start node, always attaching the cheapest edge to "
                       "the outside. Same result as Kruskal, different strategy.",
        "best_for": "MST on dense graphs.",
    },
    # ---------------- Dynamic Programming ----------------
    "fib": {
        "name": "Fibonacci (DP)", "category": "Dynamic Programming",
        "time": "O(n) memoized/tabulated (O(2ⁿ) naive!)", "space": "O(n) memo, O(1) tab",
        "difficulty": "Beginner",
        "explanation": "F(n) = F(n-1) + F(n-2). Naive recursion re-computes everything; "
                       "memoization caches results and tabulation builds bottom-up.",
        "best_for": "The 'hello world' of DP: overlapping subproblems.",
    },
    "knapsack": {
        "name": "0/1 Knapsack", "category": "Dynamic Programming",
        "time": "O(n·W)", "space": "O(n·W)",
        "difficulty": "Intermediate",
        "explanation": "Each item is taken or skipped. dp[i][c] = best value using first i items "
                       "with capacity c. Backtrack to recover the chosen items.",
        "best_for": "Resource allocation under a budget/weight limit.",
    },
    "lcs": {
        "name": "LCS", "category": "Dynamic Programming",
        "time": "O(m·n)", "space": "O(m·n)",
        "difficulty": "Intermediate",
        "explanation": "Longest Common Subsequence: if characters match, extend the diagonal; "
                       "else take the best of top/left. Basis of diff tools.",
        "best_for": "Diff utilities, DNA alignment, plagiarism detection.",
    },
    "coinchange": {
        "name": "Coin Change", "category": "Dynamic Programming",
        "time": "O(amount·coins)", "space": "O(amount)",
        "difficulty": "Intermediate",
        "explanation": "Min-coins: dp[x] = 1 + min(dp[x−c]). Also counts combinations by "
                       "iterating coins outer / amounts inner.",
        "best_for": "Change-making, any unbounded-composition problem.",
    },
    # ---------------- Pathfinding / Maze ----------------
    "maze_bfs": {
        "name": "Maze BFS", "category": "Pathfinding / Maze",
        "time": "O(rows·cols)", "space": "O(rows·cols)",
        "difficulty": "Beginner",
        "explanation": "Flood-fill from the start level by level. First time we reach the goal, "
                       "the path is the shortest possible.",
        "best_for": "Shortest maze path (unweighted grid).",
    },
    "maze_dfs": {
        "name": "Maze DFS", "category": "Pathfinding / Maze",
        "time": "O(rows·cols)", "space": "O(rows·cols)",
        "difficulty": "Beginner",
        "explanation": "Run down each corridor to its dead end before backtracking. Finds *a* "
                       "path fast, but rarely the shortest — fun to watch wander!",
        "best_for": "Fast 'any path' + maze generation.",
    },
    "maze_astar": {
        "name": "Maze A*", "category": "Pathfinding / Maze",
        "time": "O(rows·cols · log(rows·cols)) typical", "space": "O(rows·cols)",
        "difficulty": "Advanced",
        "explanation": "BFS guided by Manhattan distance to the goal — beelines toward the exit "
                       "while staying optimal on uniform grids.",
        "best_for": "Game maps: optimal + much less exploring than BFS.",
    },
    "maze_dijkstra": {
        "name": "Maze Dijkstra", "category": "Pathfinding / Maze",
        "time": "O(rows·cols · log(rows·cols))", "space": "O(rows·cols)",
        "difficulty": "Intermediate",
        "explanation": "Same as BFS on uniform grids; shines when cells have different movement "
                       "costs (mud vs road).",
        "best_for": "Weighted grids.",
    },
    # ---------------- Strings ----------------
    "naive_string": {
        "name": "Naive String Match", "category": "String",
        "time": "O(n·m)", "space": "O(1)",
        "difficulty": "Beginner",
        "explanation": "Slide the pattern along the text and compare character by character. "
                       "Simple baseline everything else beats.",
        "best_for": "Tiny patterns; baseline for comparison.",
    },
    "kmp": {
        "name": "KMP", "category": "String",
        "time": "O(n + m)", "space": "O(m)",
        "difficulty": "Advanced",
        "explanation": "Knuth-Morris-Pratt precomputes a prefix table so a mismatch skips ahead "
                       "without re-scanning text. Linear time, zero backtracking.",
        "best_for": "Single-pattern search in streams (never re-reads input).",
    },
    "rabinkarp": {
        "name": "Rabin-Karp", "category": "String",
        "time": "O(n + m) avg, O(n·m) worst", "space": "O(1)",
        "difficulty": "Intermediate",
        "explanation": "Rolling hash: compare hash values of each window, verify only on hash "
                       "match. Shines for searching many patterns at once.",
        "best_for": "Multi-pattern search, plagiarism detection.",
    },
    # ---------------- Extras ----------------
    "hanoi": {
        "name": "Tower of Hanoi", "category": "Extras",
        "time": "O(2ⁿ) moves (optimal!)", "space": "O(n) recursion",
        "difficulty": "Beginner",
        "explanation": "Move n−1 disks out of the way, move the biggest disk, stack n−1 back on "
                       "top. Recursion at its purest: 2ⁿ−1 moves, provably minimal.",
        "best_for": "Learning recursion; impressing friends with 64 disks (takes 585B years).",
    },
    "nqueens": {
        "name": "N-Queens", "category": "Extras",
        "time": "O(n!) backtracking (pruned)", "space": "O(n)",
        "difficulty": "Intermediate",
        "explanation": "Place queens row by row, rejecting columns/diagonals under attack. "
                       "Backtrack on dead ends. 8-queens has 92 solutions!",
        "best_for": "Backtracking, constraint satisfaction.",
    },
}

CATEGORIES = ["Sorting", "Searching", "Graph", "Dynamic Programming",
              "Pathfinding / Maze", "String", "Extras"]

CATEGORY_ICONS = {
    "Sorting": "🔀",
    "Searching": "🔍",
    "Graph": "🕸️",
    "Dynamic Programming": "🧠",
    "Pathfinding / Maze": "🗺️",
    "String": "🔤",
    "Extras": "🎉",
}


def algo_ids_for_category(category: str):
    return [k for k, v in ALGORITHMS.items() if v["category"] == category]


# ---------------------------------------------------- callable resolution ---
_FUNCS: dict = {}
_STEPS: dict = {}
_LOADED = False


def _ensure_loaded() -> None:
    """Lazily wire every registry id to its implementation (keeps import cost low)."""
    global _LOADED
    if _LOADED:
        return
    from . import dynamic_programming as dp
    from . import extras, graph, pathfinding, searching, sorting, strings

    _FUNCS.update(sorting.SORT_FUNCS)
    _FUNCS.update(searching.SEARCH_FUNCS)
    _FUNCS.update({
        "bfs": graph.bfs, "dfs": graph.dfs, "dijkstra": graph.dijkstra,
        "astar": graph.astar, "kruskal": graph.kruskal, "prim": graph.prim,
        "fib": dp.fib_tab, "knapsack": dp.knapsack_01, "lcs": dp.lcs,
        "coinchange": dp.coin_change_min,
        "maze_bfs": pathfinding.bfs_grid, "maze_dfs": pathfinding.dfs_grid,
        "maze_dijkstra": pathfinding.dijkstra_grid, "maze_astar": pathfinding.astar_grid,
        "naive_string": strings.naive_search, "kmp": strings.kmp_search,
        "rabinkarp": strings.rabin_karp_search,
        "hanoi": extras.hanoi, "nqueens": extras.nqueens,
    })
    _STEPS.update(sorting.SORT_STEP_FUNCS)
    _STEPS.update(searching.SEARCH_STEP_FUNCS)
    _STEPS.update({"kmp": strings.kmp_search_steps, "rabinkarp": strings.rabin_karp_steps})
    _LOADED = True


def get_function(algo_id: str):
    """Return the canonical implementation for ``algo_id`` (covers all 30 ids)."""
    _ensure_loaded()
    try:
        return _FUNCS[algo_id]
    except KeyError:
        raise KeyError(
            f"Unknown algorithm id {algo_id!r}. Valid ids: {sorted(ALGORITHMS)}"
        ) from None


def get_steps(algo_id: str):
    """Return the step-generator for ``algo_id``, or ``None`` if it has no animation."""
    _ensure_loaded()
    return _STEPS.get(algo_id)
