"""Sorting algorithms — clean implementations + step generators for animation.

Each algorithm has two faces:
  1. ``*_sort(arr)`` — pure function returning a new sorted list (used for benchmarking).
  2. ``*_sort_steps(arr)`` — generator yielding ``(snapshot, highlights, label)``
     snapshots so the Streamlit UI can animate the process.

Snapshot protocol: ``snapshot`` is a list copy, ``highlights`` is a dict
mapping index -> role string ("compare", "swap", "sorted", "key", ...),
``label`` is a short human-readable message for that step.
"""

from __future__ import annotations

import random
from typing import Dict, Generator, List, Tuple

Step = Tuple[List[int], Dict[int, str], str]


# ---------------------------------------------------------------- Bubble ---
def bubble_sort(arr: List[int]) -> List[int]:
    """Bubble Sort — repeatedly bubble the largest unsorted value to the end."""
    a = list(arr)
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:  # early exit: already sorted
            break
    return a


def bubble_sort_steps(arr: List[int]) -> Generator[Step, None, None]:
    a = list(arr)
    n = len(a)
    yield (list(a), {}, "Start: Bubble Sort — compare neighbours, bubble max right.")
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            yield (list(a), {j: "compare", j + 1: "compare"}, f"Compare a[{j}]={a[j]} vs a[{j+1}]={a[j+1]}")
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                yield (list(a), {j: "swap", j + 1: "swap"}, f"Swap → {a[j]} and {a[j+1]}")
        # tail is now sorted
        highlights = {k: "sorted" for k in range(n - 1 - i, n)}
        yield (list(a), highlights, f"Pass {i+1} done — tail locked in.")
        if not swapped:
            yield (list(a), {k: "sorted" for k in range(n)}, "Early exit — array already sorted!")
            break
    yield (list(a), {k: "sorted" for k in range(n)}, "Sorted!")


# --------------------------------------------------------------- Selection ---
def selection_sort(arr: List[int]) -> List[int]:
    """Selection Sort — repeatedly select the minimum of the unsorted suffix."""
    a = list(arr)
    for i in range(len(a)):
        min_idx = i
        for j in range(i + 1, len(a)):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def selection_sort_steps(arr: List[int]) -> Generator[Step, None, None]:
    a = list(arr)
    n = len(a)
    yield (list(a), {}, "Start: find the minimum, swap it to the front.")
    for i in range(n):
        min_idx = i
        yield (list(a), {i: "key"}, f"Position {i}: searching minimum…")
        for j in range(i + 1, n):
            yield (list(a), {i: "key", j: "compare", min_idx: "swap"},
                   f"Compare a[{j}]={a[j]} with current min a[{min_idx}]={a[min_idx]}")
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
        highlights = {k: "sorted" for k in range(i + 1)}
        highlights[i] = "sorted"
        yield (list(a), highlights, f"Swap min {a[i]} into position {i}.")
    yield (list(a), {k: "sorted" for k in range(n)}, "Sorted!")


# --------------------------------------------------------------- Insertion ---
def insertion_sort(arr: List[int]) -> List[int]:
    """Insertion Sort — build a sorted prefix, inserting each new card in place."""
    a = list(arr)
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def insertion_sort_steps(arr: List[int]) -> Generator[Step, None, None]:
    a = list(arr)
    yield (list(a), {0: "sorted"}, "Start: left prefix is 'sorted', grow it right.")
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        yield (list(a), {i: "key", **{k: "sorted" for k in range(i)}},
               f"Insert key={key} into sorted prefix.")
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            yield (list(a), {j: "compare", j + 1: "swap"},
                   f"Shift {a[j]} right to make room.")
            j -= 1
        a[j + 1] = key
        yield (list(a), {**{k: "sorted" for k in range(i + 1)}},
               f"Placed {key} at index {j+1}.")
    yield (list(a), {k: "sorted" for k in range(len(a))}, "Sorted!")


# ------------------------------------------------------------------- Merge ---
def merge_sort(arr: List[int]) -> List[int]:
    """Merge Sort — divide & conquer: sort halves, then merge (stable)."""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def _merge_in_place(a: List[int], lo: int, mid: int, hi: int):
    """Yield-friendly merge that visualizes well on the full array."""
    left = a[lo:mid + 1]
    right = a[mid + 1:hi + 1]
    i = j = 0
    k = lo
    events = []  # collect (k, value, msg)
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            a[k] = left[i]
            events.append((k, left[i], f"Take {left[i]} from left"))
            i += 1
        else:
            a[k] = right[j]
            events.append((k, right[j], f"Take {right[j]} from right"))
            j += 1
        k += 1
    while i < len(left):
        a[k] = left[i]
        events.append((k, left[i], f"Flush {left[i]}"))
        i += 1
        k += 1
    while j < len(right):
        a[k] = right[j]
        events.append((k, right[j], f"Flush {right[j]}"))
        j += 1
        k += 1
    return events


def merge_sort_steps(arr: List[int]) -> Generator[Step, None, None]:
    a = list(arr)
    yield (list(a), {}, "Start: divide the array, then merge sorted halves.")

    def rec(lo: int, hi: int):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        yield (list(a), {k: "compare" for k in range(lo, hi + 1)},
               f"Split [{lo}:{hi}] → [{lo}:{mid}] + [{mid+1}:{hi}]")
        yield from rec(lo, mid)
        yield from rec(mid + 1, hi)
        # merge step, emit after each placement
        left = a[lo:mid + 1]
        right = a[mid + 1:hi + 1]
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                a[k] = left[i]
                i += 1
            else:
                a[k] = right[j]
                j += 1
            yield (list(a), {k: "swap", **{t: "compare" for t in range(lo, hi + 1) if t != k}},
                   f"Merging [{lo}:{hi}] — wrote index {k}")
            k += 1
        while i < len(left):
            a[k] = left[i]
            i += 1
            yield (list(a), {k: "swap"}, f"Merging — flush left into {k}")
            k += 1
        while j < len(right):
            a[k] = right[j]
            j += 1
            yield (list(a), {k: "swap"}, f"Merging — flush right into {k}")
            k += 1
        yield (list(a), {t: "sorted" for t in range(lo, hi + 1)}, f"Segment [{lo}:{hi}] merged ✔")

    yield from rec(0, len(a) - 1)
    yield (list(a), {k: "sorted" for k in range(len(a))}, "Sorted!")


# ------------------------------------------------------------------- Quick ---
def quick_sort(arr: List[int]) -> List[int]:
    """Quick Sort — Lomuto partition around a randomized pivot.

    Robustness tricks: random pivot (avoids O(n²) on sorted/duplicate-heavy
    input), insertion-sort cutoff for small slices, and recurse only into the
    smaller side so stack depth stays O(log n).
    """
    a = list(arr)
    cutoff = 16

    def _insertion(lo: int, hi: int):
        for i in range(lo + 1, hi + 1):
            key = a[i]
            j = i - 1
            while j >= lo and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key

    def _qs(lo: int, hi: int):
        while lo < hi:
            if hi - lo + 1 <= cutoff:
                _insertion(lo, hi)
                return
            p = random.randint(lo, hi)  # random pivot → move to end for Lomuto
            a[p], a[hi] = a[hi], a[p]
            pivot = a[hi]
            i = lo
            for j in range(lo, hi):
                if a[j] < pivot:
                    a[i], a[j] = a[j], a[i]
                    i += 1
            a[i], a[hi] = a[hi], a[i]
            # recurse into smaller side, loop on the larger → O(log n) depth
            if i - lo < hi - i:
                _qs(lo, i - 1)
                lo = i + 1
            else:
                _qs(i + 1, hi)
                hi = i - 1

    if a:
        _qs(0, len(a) - 1)
    return a


def quick_sort_steps(arr: List[int]) -> Generator[Step, None, None]:
    a = list(arr)
    yield (list(a), {}, "Start: pick a pivot, partition smaller← →larger.")

    def rec(lo: int, hi: int):
        if lo >= hi:
            if lo == hi:
                yield (list(a), {lo: "sorted"}, f"Single element at {lo} ✔")
            return
        pivot = a[hi]
        yield (list(a), {hi: "key", **{k: "compare" for k in range(lo, hi)}},
               f"Partition [{lo}:{hi}], pivot={pivot}")
        i = lo
        for j in range(lo, hi):
            yield (list(a), {j: "compare", hi: "key", i: "swap"},
                   f"Is a[{j}]={a[j]} < pivot {pivot}?")
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                yield (list(a), {i: "swap", j: "swap", hi: "key"},
                       f"Yes → swap into boundary {i}")
                i += 1
        a[i], a[hi] = a[hi], a[i]
        yield (list(a), {i: "sorted", hi: "swap"}, f"Pivot {pivot} lands at {i} ✔")
        yield from rec(lo, i - 1)
        yield from rec(i + 1, hi)

    yield from rec(0, len(a) - 1)
    yield (list(a), {k: "sorted" for k in range(len(a))}, "Sorted!")


# -------------------------------------------------------------------- Heap ---
def heap_sort(arr: List[int]) -> List[int]:
    """Heap Sort — build a max-heap in place, then repeatedly extract the max.

    Same algorithm as ``heap_sort_steps`` (iterative sift-down, no extra
    buffer) so benchmarks and animation measure/teach the same thing: true
    in-place O(1) auxiliary space, guaranteed O(n log n).
    """
    a = list(arr)
    n = len(a)

    def sift(hi: int, i: int):
        while True:
            largest = i
            left_child = 2 * i + 1
            right_child = 2 * i + 2
            if left_child < hi and a[left_child] > a[largest]:
                largest = left_child
            if right_child < hi and a[right_child] > a[largest]:
                largest = right_child
            if largest == i:
                return
            a[i], a[largest] = a[largest], a[i]
            i = largest

    for i in range(n // 2 - 1, -1, -1):
        sift(n, i)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift(end, 0)
    return a


def heap_sort_steps(arr: List[int]) -> Generator[Step, None, None]:
    # Educational in-place max-heap version so steps make sense.
    a = list(arr)
    n = len(a)
    yield (list(a), {}, "Start: build a max-heap, then extract max repeatedly.")

    def sift(hi: int, i: int):
        while True:
            largest = i
            left_child = 2 * i + 1
            right_child = 2 * i + 2
            if left_child < hi and a[left_child] > a[largest]:
                largest = left_child
            if right_child < hi and a[right_child] > a[largest]:
                largest = right_child
            if largest == i:
                return
            a[i], a[largest] = a[largest], a[i]
            yield (list(a), {i: "swap", largest: "swap"}, f"Heapify: swap {a[i]} ↔ {a[largest]}")
            i = largest

    # build heap
    for i in range(n // 2 - 1, -1, -1):
        yield from sift(n, i)
    yield (list(a), {k: "compare" for k in range(n)}, "Max-heap built ✔")
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        yield (list(a), {0: "swap", end: "sorted"}, f"Extract max → position {end}")
        yield from sift(end, 0)
    yield (list(a), {k: "sorted" for k in range(n)}, "Sorted!")


# ----------------------------------------------------------------- Timsort ---
def timsort(arr: List[int]) -> List[int]:
    """Timsort — Python's own ``sorted()``: insertion sort on small runs + merge."""
    return sorted(arr)


def timsort_steps(arr: List[int]) -> Generator[Step, None, None]:
    # Demonstrate via insertion-on-runs then merge, simplified for animation.
    MIN_RUN = 4
    a = list(arr)
    n = len(a)
    yield (list(a), {}, f"Start: Timsort — insertion-sort runs of {MIN_RUN}, then merge.")
    # 1) sort runs with insertion sort
    for start in range(0, n, MIN_RUN):
        end = min(start + MIN_RUN - 1, n - 1)
        for i in range(start + 1, end + 1):
            key, j = a[i], i - 1
            while j >= start and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key
        yield (list(a), {k: "sorted" for k in range(start, end + 1)},
               f"Run [{start}:{end}] insertion-sorted ✔")
    # 2) merge runs doubling
    size = MIN_RUN
    while size < n:
        for lo in range(0, n, 2 * size):
            mid = min(lo + size - 1, n - 1)
            hi = min(lo + 2 * size - 1, n - 1)
            if mid < hi:
                left, right = a[lo:mid + 1], a[mid + 1:hi + 1]
                i = j = 0
                k = lo
                while i < len(left) and j < len(right):
                    a[k] = left[i] if left[i] <= right[j] else right[j]
                    if left[i] <= right[j]:
                        i += 1
                    else:
                        j += 1
                    k += 1
                while i < len(left):
                    a[k] = left[i]
                    i += 1
                    k += 1
                while j < len(right):
                    a[k] = right[j]
                    j += 1
                    k += 1
                yield (list(a), {t: "swap" for t in range(lo, hi + 1)},
                       f"Merged runs [{lo}:{mid}] + [{mid+1}:{hi}]")
        size *= 2
    yield (list(a), {k: "sorted" for k in range(n)}, "Sorted (Timsort)!")


SORT_FUNCS = {
    "bubble": bubble_sort,
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "heap": heap_sort,
    "timsort": timsort,
}

SORT_STEP_FUNCS = {
    "bubble": bubble_sort_steps,
    "selection": selection_sort_steps,
    "insertion": insertion_sort_steps,
    "merge": merge_sort_steps,
    "quick": quick_sort_steps,
    "heap": heap_sort_steps,
    "timsort": timsort_steps,
}
