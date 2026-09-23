"""Grid pathfinding: all four solvers, walls, unreachable goals, maze solvability."""
import pytest

from algorithms import pathfinding
from algorithms.pathfinding import PATH_FUNCS, grid_to_adjacency
from algorithms.utils import generate_maze

START, GOAL = (0, 0), (4, 4)
SOLVERS = sorted(PATH_FUNCS)


def open_grid(n=5):
    return [[0] * n for _ in range(n)]


def walled_grid():
    """Full wall row at r=2 → goal unreachable from start."""
    grid = open_grid()
    for c in range(5):
        grid[2][c] = 1
    return grid


@pytest.mark.parametrize("algo", SOLVERS)
def test_every_solver_finds_a_path_on_open_grid(algo):
    result = PATH_FUNCS[algo](open_grid(), START, GOAL)
    path, order = result[0], result[1]
    assert path[0] == START and path[-1] == GOAL
    assert START in order


@pytest.mark.parametrize("algo", ["bfs", "astar", "dijkstra"])
def test_optimal_solvers_get_manhattan_shortest(algo):
    path = PATH_FUNCS[algo](open_grid(), START, GOAL)[0]
    assert len(path) == 9  # 4+4 moves + start


def test_dijkstra_grid_returns_cost():
    path, order, cost = pathfinding.dijkstra_grid(open_grid(), START, GOAL)
    assert len(path) == 9
    assert cost == 8  # 8 unit-cost moves
    assert order


@pytest.mark.parametrize("algo", SOLVERS)
def test_unreachable_goal_returns_empty_path(algo):
    result = PATH_FUNCS[algo](walled_grid(), START, GOAL)
    assert result[0] == []


def test_dijkstra_unreachable_returns_infinite_cost():
    _, order, cost = pathfinding.dijkstra_grid(walled_grid(), START, GOAL)
    assert cost == float("inf")
    assert order  # still explored the reachable half


def test_dfs_routes_around_a_wall():
    grid = open_grid()
    for r in range(4):
        grid[r][1] = 1  # wall column with a gap at the bottom row
    path, _ = pathfinding.dfs_grid(grid, START, GOAL)
    assert path and path[-1] == GOAL
    assert all(grid[r][c] == 0 for r, c in path[1:])  # never enters a wall


@pytest.mark.parametrize("algo", SOLVERS)
def test_start_equals_goal(algo):
    result = PATH_FUNCS[algo](open_grid(), START, START)
    assert result[0] == [START]


def test_grid_to_adjacency_skips_walls():
    grid = open_grid()
    grid[2][2] = 1
    adj = grid_to_adjacency(grid)
    assert (2, 2) not in adj
    assert (1, 2) in adj and (3, 2) in adj
    # (1,2) neighbours: up/down/left — but not through the wall at (2,2)
    nbs = {v for v, _ in adj[(1, 2)]}
    assert nbs == {(0, 2), (1, 1), (1, 3)}


def test_grid_to_adjacency_ensure_includes_walled_start():
    grid = open_grid()
    grid[0][0] = 1
    adj = grid_to_adjacency(grid, ensure=((0, 0),))
    assert (0, 0) in adj
    assert (0, 1) in {v for v, _ in adj[(0, 0)]}  # still exits to free cells


@pytest.mark.parametrize("density", [0.0, 0.26, 0.45])
@pytest.mark.parametrize("seed", range(20))
def test_generated_mazes_are_always_solvable(density, seed):
    rows, cols = 13, 19
    grid = generate_maze(rows, cols, density, seed=seed)
    goal = (rows - 1, cols - 1)
    assert grid[0][0] == 0 and grid[goal[0]][goal[1]] == 0
    path, _ = pathfinding.bfs_grid(grid, (0, 0), goal)
    assert path, f"unsolvable maze: density={density} seed={seed}"
