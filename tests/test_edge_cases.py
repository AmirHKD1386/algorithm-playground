"""Edge cases that historically broke the playground (empty, duplicates, negatives, junk input)."""
import pytest

from algorithms import searching, sorting, strings
from algorithms.dynamic_programming import fib_memo, fib_tab
from algorithms.utils import parse_int_list

SORT_IDS = list(sorting.SORT_FUNCS)
SORT_FNS = list(sorting.SORT_FUNCS.values())
SEARCH_IDS = list(searching.SEARCH_FUNCS)
SEARCH_FNS = list(searching.SEARCH_FUNCS.values())

EDGE_ARRAYS = [
    [],
    [1],
    [2, 1],
    [5, 5, 5, 5],
    [-3, -1, -4, -1, -5],
    list(range(2000)),
    list(range(2000, 0, -1)),
]
EDGE_IDS = ["empty", "single", "two", "all-equal", "negatives", "sorted-2k", "reverse-2k"]


@pytest.mark.parametrize("fn, name", zip(SORT_FNS, SORT_IDS), ids=SORT_IDS)
@pytest.mark.parametrize("data", EDGE_ARRAYS, ids=EDGE_IDS)
def test_sorts_handle_edge_inputs(fn, name, data):
    assert fn(data) == sorted(data), name


def test_sorts_do_not_mutate_caller_list():
    data = [3, 1, 2]
    for fn in SORT_FNS:
        fn(data)
    assert data == [3, 1, 2]


def test_quicksort_survives_pathological_input():
    # old last-element Lomuto pivot hit RecursionError here
    data = [7] * 5000 + list(range(1000, 0, -1))
    assert sorting.quick_sort(data) == sorted(data)


@pytest.mark.parametrize("fn, name", zip(SEARCH_FNS, SEARCH_IDS), ids=SEARCH_IDS)
def test_searches_on_empty_array(fn, name):
    assert fn([], 42) == -1, name


@pytest.mark.parametrize("fn, name", zip(SEARCH_FNS, SEARCH_IDS), ids=SEARCH_IDS)
def test_search_absent_target(fn, name):
    assert fn([1, 3, 5, 7], 4) == -1, name


def test_string_searches_empty_pattern_and_text():
    for fn in (strings.naive_search, strings.kmp_search, strings.rabin_karp_search):
        assert fn("abc", "") == []
        assert fn("", "a") == []
        assert fn("", "") == []


def test_fib_variants_agree_up_to_24():
    for n in range(25):
        assert fib_tab(n) == fib_memo(n), n


def test_parse_int_list_accepts_mixed_separators():
    assert parse_int_list("3, 1, 4; 1, 5") == [3, 1, 4, 1, 5]
    assert parse_int_list("-2, 0, +7") == [-2, 0, 7]


@pytest.mark.parametrize("junk", ["", "   ", "1, abc, 3", "1.5, 2"])
def test_parse_int_list_rejects_junk(junk):
    with pytest.raises(ValueError):
        parse_int_list(junk)
