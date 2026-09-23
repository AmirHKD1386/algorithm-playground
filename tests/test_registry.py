"""Registry consistency — the single source of truth must actually cover everything."""
import inspect

import pytest

from algorithms.registry import (
    ALGORITHMS,
    CATEGORIES,
    CATEGORY_ICONS,
    algo_ids_for_category,
    get_function,
    get_steps,
)

REQUIRED_FIELDS = {"name", "category", "time", "space", "difficulty", "explanation", "best_for"}
SORTING_IDS = set(algo_ids_for_category("Sorting"))
SEARCHING_IDS = set(algo_ids_for_category("Searching"))


def test_thirty_algorithms_across_seven_categories():
    assert len(ALGORITHMS) == 30
    assert len(CATEGORIES) == 7
    assert set(CATEGORY_ICONS) == set(CATEGORIES)


def test_every_id_has_complete_metadata():
    for aid, meta in ALGORITHMS.items():
        missing = REQUIRED_FIELDS - meta.keys()
        assert not missing, f"{aid} missing fields: {missing}"
        assert meta["category"] in CATEGORIES, f"{aid} has unknown category"


def test_every_category_has_ids():
    for cat in CATEGORIES:
        assert algo_ids_for_category(cat), f"no algorithms registered under {cat!r}"


@pytest.mark.parametrize("aid", sorted(ALGORITHMS))
def test_get_function_resolves_to_source_available_callable(aid):
    """All 30 ids must resolve — this is what CLI `show` and the Learn tab rely on."""
    fn = get_function(aid)
    assert callable(fn), aid
    assert inspect.getsource(fn), f"no source for {aid}"


@pytest.mark.parametrize("aid", sorted(SORTING_IDS | SEARCHING_IDS))
def test_sorting_and_searching_have_step_generators(aid):
    steps = get_steps(aid)
    assert steps is not None and callable(steps), aid


def test_string_algorithms_with_traces_have_steps():
    assert callable(get_steps("kmp"))
    assert callable(get_steps("rabinkarp"))


@pytest.mark.parametrize("aid", ["bfs", "dijkstra", "fib", "hanoi", "maze_bfs"])
def test_ids_without_animation_return_none(aid):
    assert get_steps(aid) is None


def test_unknown_id_raises_helpful_keyerror():
    with pytest.raises(KeyError, match="Unknown algorithm id"):
        get_function("does_not_exist")
