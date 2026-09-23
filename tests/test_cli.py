"""CLI unit tests — drive ``main(argv=[...])`` directly, no subprocess needed."""
import pytest

from cli import main


def test_list_prints_all_categories(capsys):
    main(["list"])
    out = capsys.readouterr().out
    assert "Sorting" in out
    assert "bubble" in out
    assert "Pathfinding / Maze" in out


def test_show_known_algorithm(capsys):
    main(["show", "quick"])
    out = capsys.readouterr().out
    assert "Quick Sort" in out


def test_show_prints_source_for_previously_missing_ids(capsys):
    # these 18 ids used to silently print no source at all
    for aid, marker in [("dijkstra", "def dijkstra"),
                        ("knapsack", "def knapsack_01"),
                        ("maze_astar", "def astar_grid"),
                        ("coinchange", "def coin_change_min")]:
        main(["show", aid])
        out = capsys.readouterr().out
        assert marker in out, f"`show {aid}` did not print source"


def test_show_unknown_algorithm_exits_with_code_1(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["show", "nope"])
    assert exc.value.code == 1


def test_hanoi_prints_move_list(capsys):
    main(["hanoi", "--disks", "3"])
    out = capsys.readouterr().out
    assert "7" in out  # 2^3 − 1


@pytest.mark.parametrize("bad", ["-1", "13", "30"])
def test_hanoi_rejects_out_of_range_disks(bad):
    # -1 used to cause infinite recursion; 30 would OOM
    with pytest.raises(SystemExit):
        main(["hanoi", "--disks", bad])


def test_bench_sizes_rejects_non_integers():
    with pytest.raises(SystemExit) as exc:
        main(["bench-sorting", "--sizes", "200,abc"])
    assert exc.value.code == 1


def test_bench_sizes_rejects_non_positive():
    with pytest.raises(SystemExit) as exc:
        main(["bench-sorting", "--sizes", "0,-5"])
    assert exc.value.code == 1


def test_bench_runs_tiny_case(capsys):
    main(["bench-sorting", "--sizes", "50", "--algos", "bubble,insertion",
          "--repeats", "1"])
    out = capsys.readouterr().out
    assert "Bubble Sort" in out


def test_bench_rejects_unknown_algo():
    with pytest.raises(SystemExit) as exc:
        main(["bench-sorting", "--algos", "bogosort"])
    assert exc.value.code == 1


def test_search_command_runs(capsys):
    main(["search", "--algo", "binary", "--n", "100"])
    out = capsys.readouterr().out
    assert "Binary Search" in out


def test_nqueens_command_runs(capsys):
    main(["nqueens", "--n", "4"])
    out = capsys.readouterr().out
    assert "2" in out  # 4-queens has 2 solutions
