"""Searching algorithms with step traces for visualization."""

from __future__ import annotations

import math
from typing import Generator, List, Tuple

Trace = Generator[Tuple[List[int], str], None, int]
# yields (visited_indices_so_far, message), returns found index (or -1)


def linear_search(arr: List[int], target: int) -> int:
    """Linear Search — scan left→right. O(n). Works on anything."""
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1


def linear_search_steps(arr: List[int], target: int) -> Trace:
    visited: List[int] = []
    for i, v in enumerate(arr):
        visited.append(i)
        yield (list(visited), f"Check index {i}: {v} {'✔ FOUND!' if v == target else '≠ ' + str(target)}")
        if v == target:
            return i
    return -1


def binary_search(arr: List[int], target: int) -> int:
    """Binary Search — halve a *sorted* array each step. O(log n)."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def binary_search_steps(arr: List[int], target: int) -> Trace:
    lo, hi = 0, len(arr) - 1
    visited: List[int] = []
    step = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        visited.append(mid)
        step += 1
        yield (list(visited),
               f"Step {step}: lo={lo}, hi={hi}, mid={mid} (value {arr[mid]})")
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def jump_search(arr: List[int], target: int) -> int:
    """Jump Search — jump √n blocks, then linear-scan backwards block. O(√n)."""
    n = len(arr)
    if n == 0:
        return -1
    step = int(math.sqrt(n)) or 1
    # standard formulation:
    prev = 0
    curr = step
    while curr < n and arr[curr - 1] < target:
        prev = curr
        curr += step
    for i in range(prev, min(curr, n)):
        if arr[i] == target:
            return i
    return -1


def jump_search_steps(arr: List[int], target: int) -> Trace:
    n = len(arr)
    visited: List[int] = []
    if n == 0:
        return -1
    step = int(math.sqrt(n)) or 1
    prev = 0
    yield (list(visited), f"Block size = √{n} ≈ {step}. Jumping…")
    curr = step
    while curr < n and arr[min(curr - 1, n - 1)] < target:
        visited.append(min(curr - 1, n - 1))
        yield (list(visited), f"Jump to index {min(curr-1, n-1)} (value {arr[min(curr-1, n-1)]}) < {target} → skip block")
        prev = curr
        curr += step
    if prev < n:
        visited.append(prev)
    yield (list(visited), f"Target may be in block [{prev}:{min(curr, n)-1}] — linear scan…")
    for i in range(prev, min(curr, n)):
        visited.append(i)
        yield (list(visited), f"Linear check index {i}: {arr[i]} {'✔ FOUND!' if arr[i]==target else ''}")
        if arr[i] == target:
            return i
    return -1


def interpolation_search(arr: List[int], target: int) -> int:
    """Interpolation Search — guess position proportionally (uniform data → O(log log n))."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi and len(arr) and arr[lo] <= target <= arr[hi]:
        if arr[hi] == arr[lo]:
            return lo if arr[lo] == target else -1
        pos = lo + int((target - arr[lo]) * (hi - lo) / (arr[hi] - arr[lo]))
        pos = max(lo, min(hi, pos))
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


def interpolation_search_steps(arr: List[int], target: int) -> Trace:
    lo, hi = 0, len(arr) - 1
    visited: List[int] = []
    step = 0
    while lo <= hi and arr and arr[lo] <= target <= arr[hi]:
        if arr[hi] == arr[lo]:
            visited.append(lo)
            yield (list(visited), f"Flat segment — check {lo}")
            return lo if arr[lo] == target else -1
        pos = lo + int((target - arr[lo]) * (hi - lo) / (arr[hi] - arr[lo]))
        pos = max(lo, min(hi, pos))
        visited.append(pos)
        step += 1
        yield (list(visited),
               f"Step {step}: interpolate pos={pos} (value {arr[pos]}), range [{lo}:{hi}]")
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


SEARCH_FUNCS = {
    "linear": linear_search,
    "binary": binary_search,
    "jump": jump_search,
    "interpolation": interpolation_search,
}

SEARCH_STEP_FUNCS = {
    "linear": linear_search_steps,
    "binary": binary_search_steps,
    "jump": jump_search_steps,
    "interpolation": interpolation_search_steps,
}
