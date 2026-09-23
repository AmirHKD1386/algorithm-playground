"""Smoke tests for every algorithm family. Run: python -m pytest tests/ -q"""

from algorithms import dynamic_programming as dp
from algorithms import extras, pathfinding, searching, sorting, strings
from algorithms import graph as g
from algorithms.utils import generate_random_graph


def test_sorting_correctness():
    data = [5, 2, 9, 1, 5, 6, 3, 8, 0, -1]
    for name, fn in sorting.SORT_FUNCS.items():
        assert fn(data) == sorted(data), f"{name} failed"
        assert data == [5, 2, 9, 1, 5, 6, 3, 8, 0, -1], "input mutated!"


def test_sorting_steps_end_sorted():
    arr = [4, 3, 2, 1]
    for name, gen in sorting.SORT_STEP_FUNCS.items():
        steps = list(gen(arr))
        assert steps[-1][0] == [1, 2, 3, 4], f"{name} steps don't end sorted"


def test_searching():
    arr = list(range(0, 40, 2))  # even numbers
    assert searching.binary_search(arr, 10) == 5
    assert searching.binary_search(arr, 11) == -1
    assert searching.linear_search(arr, 10) == 5
    assert searching.jump_search(arr, 10) == 5
    assert searching.interpolation_search(arr, 10) == 5
    assert searching.interpolation_search(arr, 11) == -1


def test_graph():
    adj = generate_random_graph(8, 0.4, True, seed=1)
    assert set(graph_bfs(adj)) == set(range(8))  # connected
    dist, prev = g.dijkstra(adj, 0)
    assert dist[0] == 0 and all(v >= 0 for v in dist.values())
    mst, total = g.kruskal(adj)
    assert len(mst) == 7 and total > 0
    mst2, total2 = g.prim(adj, 0)
    assert abs(total - total2) < 1e-9, "Kruskal and Prim must agree on MST weight"


def graph_bfs(adj):
    return g.bfs(adj, 0)


def test_dp():
    assert dp.fib_tab(10) == 55 and dp.fib_memo(10) == 55
    best, chosen, _ = dp.knapsack_01([2, 3, 4, 5], [3, 4, 5, 6], 5)
    assert best == 7  # items 0+1
    s, ln, _ = dp.lcs("AGGTAB", "GXTXAYB")
    assert ln == 4 and s == "GTAB"
    c, used = dp.coin_change_min([1, 5, 10, 25], 63)
    assert c == 6 and sum(used) == 63
    assert dp.coin_change_ways([1, 2, 5], 5) == 4


def test_pathfinding():
    grid = [[0] * 5 for _ in range(5)]
    path, order = pathfinding.bfs_grid(grid, (0, 0), (4, 4))
    assert len(path) == 9  # Manhattan shortest
    path2, _ = pathfinding.astar_grid(grid, (0, 0), (4, 4))
    assert len(path2) == 9


def test_strings():
    text, pat = "ababcababcabc", "abc"
    expected = [2, 7, 10]
    assert strings.naive_search(text, pat) == expected
    assert strings.kmp_search(text, pat) == expected
    assert strings.rabin_karp_search(text, pat) == expected


def test_extras():
    assert len(extras.hanoi(3)) == 7
    sols = extras.nqueens(4)
    assert len(sols) == 2
    assert extras.nqueens_count(8) == 92


if __name__ == "__main__":
    test_sorting_correctness()
    test_sorting_steps_end_sorted()
    test_searching()
    test_graph()
    test_dp()
    test_pathfinding()
    test_strings()
    test_extras()
    print("All algorithm smoke tests passed OK")
