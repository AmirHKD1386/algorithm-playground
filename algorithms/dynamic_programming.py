"""Dynamic programming classics: Fibonacci, Knapsack, LCS, Coin Change."""

from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple


# -------------------------------------------------------------- Fibonacci ---
def fib_recursive(n: int) -> int:
    """Naive recursion — O(2^n). Only for tiny n (shows why memo matters)."""
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)


def fib_memo(n: int) -> int:
    """Top-down memoization — O(n) time, O(n) space."""
    @lru_cache(maxsize=None)
    def f(k: int) -> int:
        if k <= 1:
            return k
        return f(k - 1) + f(k - 2)
    return f(n)


def fib_tab(n: int) -> int:
    """Bottom-up tabulation — O(n) time, O(1) space."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fib_sequence(n: int) -> List[int]:
    """First n+1 Fibonacci numbers (for charts)."""
    seq = []
    a, b = 0, 1
    for _ in range(n + 1):
        seq.append(a)
        a, b = b, a + b
    return seq


# --------------------------------------------------------------- Knapsack ---
def knapsack_01(weights: List[int], values: List[int], capacity: int) -> Tuple[int, List[int], List[List[int]]]:
    """0/1 Knapsack — DP table O(n·W). Returns (max_value, chosen_idx, table)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]  # skip item i
            if w <= c:  # take item i
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)
    # backtrack chosen items
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(i - 1)
            c -= weights[i - 1]
    return dp[n][capacity], sorted(chosen), dp


# -------------------------------------------------------------------- LCS ---
def lcs(a: str, b: str) -> Tuple[str, int, List[List[int]]]:
    """Longest Common Subsequence — O(|a|·|b|). Returns (lcs_str, length, table)."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # backtrack one LCS string
    i, j, chars = m, n, []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            chars.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(chars)), dp[m][n], dp


# ------------------------------------------------------------ Coin Change ---
def coin_change_min(coins: List[int], amount: int) -> Tuple[int, List[int]]:
    """Min coins to make ``amount`` — O(amount·coins). Returns (count, coin_list)."""
    INF = float("inf")
    dp = [INF] * (amount + 1)
    use = [-1] * (amount + 1)
    dp[0] = 0
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and dp[x - c] + 1 < dp[x]:
                dp[x] = dp[x - c] + 1
                use[x] = c
    if dp[amount] == INF:
        return -1, []
    out, x = [], amount
    while x > 0:
        out.append(use[x])
        x -= use[x]
    return int(dp[amount]), out


def coin_change_ways(coins: List[int], amount: int) -> int:
    """Count combinations (order-independent) — O(amount·coins)."""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]
