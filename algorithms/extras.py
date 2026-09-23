"""Fun extras: Tower of Hanoi + N-Queens."""

from __future__ import annotations

from typing import List, Tuple

Move = Tuple[int, str, str]  # (disk, from_peg, to_peg)


# --------------------------------------------------------- Tower of Hanoi ---
def hanoi(n: int, source: str = "A", target: str = "C", aux: str = "B") -> List[Move]:
    """Classic recursive solution — exactly 2^n − 1 moves (provably optimal)."""
    moves: List[Move] = []

    def rec(k: int, s: str, t: str, a: str):
        if k == 0:
            return
        rec(k - 1, s, a, t)      # move tower of k-1 off the largest disk
        moves.append((k, s, t))   # move largest disk
        rec(k - 1, a, t, s)       # stack k-1 back on top

    rec(n, source, target, aux)
    return moves


def hanoi_pegs_state(n: int, moves: List[Move], source="A", target="C", aux="B"):
    """Compute peg stacks from a move prefix (for drawing). Largest disk = n."""
    pegs = {source: list(range(n, 0, -1)), target: [], aux: []}
    for disk, s, t in moves:
        pegs[s].pop()
        pegs[t].append(disk)
    return pegs


# ---------------------------------------------------------------- N-Queens ---
def nqueens(n: int, max_solutions: int = 10) -> List[List[int]]:
    """Backtracking N-Queens. Returns boards as [col_of_queen_in_row_0, …].

    Caps at ``max_solutions`` so the UI stays snappy for n ≥ 9.
    """
    solutions: List[List[int]] = []
    cols: set = set()
    diag1: set = set()  # r + c
    diag2: set = set()  # r - c
    board = [-1] * n

    def backtrack(r: int):
        if len(solutions) >= max_solutions:
            return
        if r == n:
            solutions.append(list(board))
            return
        for c in range(n):
            if c in cols or (r + c) in diag1 or (r - c) in diag2:
                continue
            board[r] = c
            cols.add(c)
            diag1.add(r + c)
            diag2.add(r - c)
            backtrack(r + 1)
            cols.discard(c)
            diag1.discard(r + c)
            diag2.discard(r - c)
            board[r] = -1

    backtrack(0)
    return solutions


def nqueens_count(n: int) -> int:
    """Count ALL solutions (fast bit-mask) — for the 'total solutions' stat."""
    # bit-mask backtracking; handles n up to ~14 comfortably
    count = 0

    def bt(cols: int, d1: int, d2: int):
        nonlocal count
        if cols == (1 << n) - 1:
            count += 1
            return
        avail = ((1 << n) - 1) & ~(cols | d1 | d2)
        while avail:
            bit = avail & -avail
            avail -= bit
            bt(cols | bit, (d1 | bit) << 1, (d2 | bit) >> 1)

    bt(0, 0, 0)
    return count


def board_to_emoji(queens: List[int]) -> str:
    """Render a solution as text — ♛ for queens, · otherwise (CLI + fallback)."""
    n = len(queens)
    lines = []
    for r in range(n):
        lines.append(" ".join("♛" if queens[r] == c else "·" for c in range(n)))
    return "\n".join(lines)
