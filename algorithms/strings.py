"""String algorithms: Naive, KMP, Rabin-Karp."""

from __future__ import annotations

from typing import Generator, List, Tuple


# ------------------------------------------------------------------ Naive ---
def naive_search(text: str, pattern: str) -> List[int]:
    """Naive sliding window — O(n·m). Simple baseline."""
    if not pattern:
        return []
    out = []
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i + len(pattern)] == pattern:
            out.append(i)
    return out


# --------------------------------------------------------------------- KMP ---
def kmp_prefix(pattern: str) -> List[int]:
    """Prefix (failure) function π: longest proper prefix which is also suffix."""
    pi = [0] * len(pattern)
    for i in range(1, len(pattern)):
        j = pi[i - 1]
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    return pi


def kmp_search(text: str, pattern: str) -> List[int]:
    """Knuth-Morris-Pratt — O(n+m). Never re-scans text characters."""
    if not pattern:
        return []
    pi = kmp_prefix(pattern)
    out, j = [], 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = pi[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            out.append(i - j + 1)
            j = pi[j - 1]
    return out


def kmp_search_steps(text: str, pattern: str) -> Generator[Tuple[int, int, str], None, List[int]]:
    """Yield (i, j, message) per text character; returns match list."""
    if not pattern:
        return []
    pi = kmp_prefix(pattern)
    out, j = [], 0
    yield (-1, 0, f"Prefix table π = {pi}")
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            yield (i, j, f"text[{i}]='{ch}' ≠ pat[{j}]='{pattern[j]}' → fallback j=π[{j-1}]={pi[j-1]}")
            j = pi[j - 1]
        if ch == pattern[j]:
            j += 1
            yield (i, j, f"text[{i}]='{ch}' == pat[{j-1}] → advance j={j}")
        else:
            yield (i, j, f"text[{i}]='{ch}' ≠ pat[0] → stay j=0")
        if j == len(pattern):
            out.append(i - j + 1)
            yield (i, j, f"✔ Match at index {i-j+1}!")
            j = pi[j - 1]
    return out


# -------------------------------------------------------------- Rabin-Karp ---
def rabin_karp_search(text: str, pattern: str, base: int = 256, mod: int = 101_419) -> List[int]:
    """Rabin-Karp — rolling hash, average O(n+m). Great for multi-pattern search."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    h = pow(base, m - 1, mod)
    pat_hash = 0
    win_hash = 0
    for i in range(m):
        pat_hash = (pat_hash * base + ord(pattern[i])) % mod
        win_hash = (win_hash * base + ord(text[i])) % mod
    out = []
    for i in range(n - m + 1):
        if pat_hash == win_hash and text[i:i + m] == pattern:
            out.append(i)
        if i < n - m:
            # roll: drop leading char, shift, add trailing char
            win_hash = (win_hash - ord(text[i]) * h) % mod
            win_hash = (win_hash * base + ord(text[i + m])) % mod
    return out


def rabin_karp_steps(text: str, pattern: str, base: int = 256,
                     mod: int = 101_419) -> Generator[Tuple[int, int, int, str], None, List[int]]:
    """Yield (window_start, pat_hash, win_hash, message) per window."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    h = pow(base, m - 1, mod)
    pat_hash = win_hash = 0
    for i in range(m):
        pat_hash = (pat_hash * base + ord(pattern[i])) % mod
        win_hash = (win_hash * base + ord(text[i])) % mod
    out = []
    yield (0, pat_hash, win_hash, f"pat_hash={pat_hash}. Slide window of size {m}…")
    for i in range(n - m + 1):
        if pat_hash == win_hash:
            if text[i:i + m] == pattern:
                out.append(i)
                yield (i, pat_hash, win_hash, f"Window {i}: hash match + verify ✔ → MATCH")
            else:
                yield (i, pat_hash, win_hash, f"Window {i}: hash match but verify ✘ (spurious hit)")
        else:
            yield (i, pat_hash, win_hash, f"Window {i}: {win_hash} ≠ {pat_hash} → skip")
        if i < n - m:
            win_hash = (win_hash - ord(text[i]) * h) % mod
            win_hash = (win_hash * base + ord(text[i + m])) % mod
    return out
