"""Polished Rich CLI for the Algorithm Playground.

Usage:
    python cli.py list
    python cli.py show quick
    python cli.py bench-sorting --sizes 200,1000,3000 --algos bubble,quick,merge,timsort
    python cli.py search --algo binary
    python cli.py hanoi --disks 4
    python cli.py nqueens --n 8
"""
from __future__ import annotations

import argparse
import inspect
import sys
import time

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.syntax import Syntax
from rich.table import Table

from algorithms import extras, searching, sorting, strings
from algorithms.registry import (
    ALGORITHMS,
    CATEGORIES,
    algo_ids_for_category,
    get_function,
)
from algorithms.utils import benchmark, format_ms, generate_random_array, generate_random_text

# Windows legacy consoles (cp1256 etc.) can't render unicode math symbols —
# sanitize table text so `python cli.py list` never crashes there.
# (The Streamlit app keeps the pretty unicode versions.)
_UNI_FIX = {"²": "^2", "³": "^3", "ⁿ": "^n", "√n": "sqrt(n)", "√": "sqrt",
            "·": "*", "→": "->", "∞": "inf", "π": "pi",
            "✔": "OK", "✘": "x", "⟦": "[", "⟧": "]", "⚡": "*",
            "❤": "<3"}
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe(s: object) -> str:
    t = str(s)
    for k, v in _UNI_FIX.items():
        t = t.replace(k, v)
    return t.encode("ascii", errors="replace").decode("ascii")


console = Console(legacy_windows=False)


def cmd_list(_args):
    for cat in CATEGORIES:
        t = Table(title=f"{cat}", box=box.ROUNDED, show_lines=False)
        t.add_column("ID", style="cyan bold")
        t.add_column("Name", style="white")
        t.add_column("Time", style="magenta")
        t.add_column("Space", style="green")
        for aid in algo_ids_for_category(cat):
            m = ALGORITHMS[aid]
            t.add_row(_safe(aid), _safe(m["name"]), _safe(m["time"]), _safe(m["space"]))
        console.print(t)


def cmd_show(args):
    aid = args.algo
    if aid not in ALGORITHMS:
        console.print(f"[red]Unknown algorithm '{aid}'. Try: python cli.py list[/red]")
        sys.exit(1)
    m = ALGORITHMS[aid]
    console.print(Panel(f"[bold]{m['name']}[/bold]  ({m['category']})\n\n"
                        f"{m['explanation']}\n\n"
                        f"[cyan]Time:[/cyan] {m['time']}   [green]Space:[/green] {m['space']}\n"
                        f"[yellow]Best for:[/yellow] {m['best_for']}",
                        title="📚 Algorithm card", box=box.DOUBLE))
    fn = get_function(aid)  # registry covers all 30 ids
    try:
        src = inspect.getsource(fn)
    except (OSError, TypeError):
        console.print("[yellow]Source not available — see the Streamlit app "
                      "(Learn tab) or the `algorithms/` package.[/yellow]")
    else:
        console.print(Syntax(src, "python", theme="monokai", line_numbers=True))


def cmd_bench_sorting(args):
    try:
        sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
    except ValueError:
        console.print("[red]--sizes must be comma-separated integers, "
                      "e.g. 200,1000,3000[/red]")
        sys.exit(1)
    if not sizes or any(n <= 0 for n in sizes):
        console.print("[red]--sizes must contain positive integers.[/red]")
        sys.exit(1)
    algos = [a.strip() for a in args.algos.split(",") if a.strip()]
    for a in algos:
        if a not in sorting.SORT_FUNCS:
            console.print(f"[red]Unknown sorting algo '{a}'. Choices: {list(sorting.SORT_FUNCS)}[/red]")
            sys.exit(1)
    table = Table(title="⚔️ Sorting showdown (best of repeats, lower is faster)",
                  box=box.HEAVY_HEAD)
    table.add_column("n", style="bold")
    for a in algos:
        table.add_column(ALGORITHMS[a]["name"], justify="right")
    for n in track(sizes, description="Benchmarking…"):
        base = generate_random_array(n, seed=args.seed)
        row = [str(n)]
        for a in algos:
            ms = benchmark(sorting.SORT_FUNCS[a], list(base), repeats=args.repeats)["best_ms"]
            row.append(format_ms(ms))
        table.add_row(*row)
    console.print(table)
    console.print("[green]Done! Tip: run the Streamlit app for animated charts: "
                 "[bold]streamlit run app.py[/bold][/green]")


def cmd_search(args):
    n = args.n
    arr = sorted(generate_random_array(n, seed=args.seed))
    target = arr[-1] if args.target is None else args.target
    fn = searching.SEARCH_FUNCS[args.algo]
    t0 = time.perf_counter()
    idx = fn(arr, target)
    dt_ms = (time.perf_counter() - t0) * 1000
    console.print(Panel(f"Array size {n}, target {target} → index [bold]{idx}[/bold] "
                        f"in {format_ms(dt_ms)}", title=f"🔍 {ALGORITHMS[args.algo]['name']}"))


def _disks_arg(value: str) -> int:
    """argparse type: bound --disks so negative/huge values can't hang or OOM."""
    n = int(value)
    if not 0 <= n <= 12:
        raise argparse.ArgumentTypeError("--disks must be between 0 and 12")
    return n


def cmd_hanoi(args):
    moves = extras.hanoi(args.disks)
    console.print(Panel(f"{args.disks} disks → [bold]{len(moves)}[/bold] optimal moves "
                        f"(2^n − 1)", title="🗼 Tower of Hanoi"))
    for i, (d, s, t) in enumerate(moves, 1):
        console.print(f"  {i:3d}. disk {d}: {s} → {t}")
        if i >= 60:
            console.print(f"  … and {len(moves)-60} more (full list in the Streamlit app!)")
            break


def cmd_nqueens(args):
    sols = extras.nqueens(args.n, max_solutions=3)
    total = extras.nqueens_count(args.n) if args.n <= 10 else "?"
    console.print(Panel(f"N={args.n}: [bold]{total}[/bold] total solutions "
                        f"(showing {len(sols)})", title="👑 N-Queens"))
    for q in sols:
        console.print(Panel(extras.board_to_emoji(q), title=f"solution {q}"))


def cmd_strings(args):
    text = generate_random_text(args.chars, seed=args.seed)
    pat = args.pattern
    results = {}
    for name, fn in [("naive", strings.naive_search), ("kmp", strings.kmp_search),
                     ("rabin_karp", strings.rabin_karp_search)]:
        stats = benchmark(fn, text, pat, repeats=args.repeats)
        results[name] = (stats["best_ms"], len(fn(text, pat)))
    t = Table(title=f"🔤 String search on {args.chars} chars, pattern '{pat}'", box=box.ROUNDED)
    t.add_column("Algorithm", style="cyan")
    t.add_column("Best time", justify="right", style="magenta")
    t.add_column("Matches", justify="right", style="green")
    for k, (ms, c) in results.items():
        t.add_row(k, format_ms(ms), str(c))
    console.print(t)


def main(argv=None):
    p = argparse.ArgumentParser(description="Algorithm Playground CLI (Rich-powered)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all algorithms grouped by category")

    ps = sub.add_parser("show", help="Show explanation + source for one algorithm")
    ps.add_argument("algo", help="algorithm id (see `list`), e.g. quick, kmp, hanoi")

    pb = sub.add_parser("bench-sorting", help="Benchmark sorting algorithms head-to-head")
    pb.add_argument("--sizes", default="200,1000,3000")
    pb.add_argument("--algos", default="bubble,insertion,merge,quick,heap,timsort")
    pb.add_argument("--repeats", type=int, default=3)
    pb.add_argument("--seed", type=int, default=42)

    ps2 = sub.add_parser("search", help="Run a search algorithm once")
    ps2.add_argument("--algo", default="binary",
                     choices=list(searching.SEARCH_FUNCS.keys()))
    ps2.add_argument("--n", type=int, default=10000)
    ps2.add_argument("--target", type=int, default=None)
    ps2.add_argument("--seed", type=int, default=42)

    ph = sub.add_parser("hanoi", help="Print Tower of Hanoi moves")
    ph.add_argument("--disks", type=_disks_arg, default=4)

    pn = sub.add_parser("nqueens", help="Solve N-Queens")
    pn.add_argument("--n", type=int, default=8)

    pst = sub.add_parser("strings", help="Benchmark string-search algorithms")
    pst.add_argument("--chars", type=int, default=20000)
    pst.add_argument("--pattern", default="abcab")
    pst.add_argument("--repeats", type=int, default=3)
    pst.add_argument("--seed", type=int, default=42)

    args = p.parse_args(argv)
    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "show":
        cmd_show(args)
    elif args.cmd == "bench-sorting":
        cmd_bench_sorting(args)
    elif args.cmd == "search":
        cmd_search(args)
    elif args.cmd == "hanoi":
        cmd_hanoi(args)
    elif args.cmd == "nqueens":
        cmd_nqueens(args)
    elif args.cmd == "strings":
        cmd_strings(args)


if __name__ == "__main__":
    main()
