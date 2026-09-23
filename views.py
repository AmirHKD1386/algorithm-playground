"""Streamlit view layer: theming, HTML/chart helpers, and the four tab renderers.

``app.py`` owns page config, sidebar widgets, and wiring; everything that
*renders inside a tab* lives here as an importable function so it can be
tested and reused. All algorithm dispatch goes through the registry
(``get_function`` / ``get_steps``) — no local id→function maps.
"""

from __future__ import annotations

import inspect
import random
import textwrap
import time

import pandas as pd
import streamlit as st

from algorithms import dynamic_programming as dp
from algorithms import extras, strings
from algorithms import graph as graph_algos
from algorithms.registry import ALGORITHMS, get_function, get_steps
from algorithms.utils import (
    benchmark,
    format_ms,
    generate_maze,
    generate_random_array,
    generate_random_graph,
    generate_random_text,
    parse_int_list,
)

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:  # graceful fallback to native charts
    HAS_PLOTLY = False

THEMES = {
    "Dark": {
        "bg": "#0e1117", "card": "#161b22", "text": "#e6edf3",
        "muted": "#8b949e", "accent": "#7c3aed", "accent2": "#06b6d4",
        "good": "#22c55e", "warn": "#f59e0b", "bad": "#ef4444",
        "plotly": "plotly_dark",
    },
    "Light": {
        "bg": "#f8fafc", "card": "#ffffff", "text": "#0f172a",
        "muted": "#64748b", "accent": "#7c3aed", "accent2": "#0891b2",
        "good": "#16a34a", "warn": "#d97706", "bad": "#dc2626",
        "plotly": "plotly_white",
    },
}

HIGHLIGHT_COLORS = {"compare": "#f59e0b", "swap": "#ef4444", "sorted": "#22c55e", "key": "#3b82f6"}


# ============================================================ helpers ========
def inject_css(theme: dict) -> None:
    st.markdown(f"""
    <style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    .block-container {{ animation: fadeIn .45s ease; }}
    .stApp {{ background: {theme['bg']}; color: {theme['text']}; }}
    .algo-card {{
        background: {theme['card']}; border: 1px solid rgba(127,127,127,.25);
        border-radius: 16px; padding: 18px 20px; margin-bottom: 14px;
        box-shadow: 0 8px 28px rgba(0,0,0,.25);
    }}
    .badge {{
        display: inline-block; padding: 3px 12px; border-radius: 999px;
        font-size: 12.5px; font-weight: 700; margin: 2px 4px 2px 0;
    }}
    .badge-time {{ background: rgba(124,58,237,.18); color: {theme['accent']}; border: 1px solid {theme['accent']}; }}
    .badge-space {{ background: rgba(6,182,212,.15); color: {theme['accent2']}; border: 1px solid {theme['accent2']}; }}
    .badge-diff {{ background: rgba(34,197,94,.15); color: {theme['good']}; border: 1px solid {theme['good']}; }}
    .muted {{ color: {theme['muted']}; }}
    .big-number {{ font-size: 34px; font-weight: 800; }}
    .maze-cell {{ width: 26px; height: 26px; display: inline-block; margin: 0; border-radius: 4px; }}
    .chess {{ border-collapse: collapse; }}
    .chess td {{ width: 38px; height: 38px; text-align: center; font-size: 24px; }}
    section[data-testid="stSidebar"] {{ background: {theme['card']}; }}
    .stProgress > div > div > div > div {{ background: linear-gradient(90deg, {theme['accent']}, {theme['accent2']}); }}
    </style>
    """, unsafe_allow_html=True)


def bar_fig(values, highlights=None, title="", theme=None):
    """Plotly bar chart for sorting/searching animation (falls back to st.bar_chart)."""
    highlights = highlights or {}
    if not HAS_PLOTLY:
        return None
    colors = [HIGHLIGHT_COLORS.get(highlights.get(i), "#6366f1") for i in range(len(values))]
    fig = go.Figure(go.Bar(x=list(range(len(values))), y=list(values),
                           marker_color=colors, text=list(values), textposition="outside"))
    fig.update_layout(template=(theme or THEMES["Dark"])["plotly"], title=title, height=380,
                      xaxis_title="index", yaxis_title="value",
                      margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    return fig


def benchmark_chart(df: pd.DataFrame, title: str, theme: dict) -> None:
    """Pretty line+marker chart from a {size -> ms} frame."""
    if HAS_PLOTLY:
        fig = go.Figure()
        for col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode="lines+markers",
                                     name=str(col), line=dict(width=3),
                                     marker=dict(size=9)))
        fig.update_layout(template=theme["plotly"], title=title, height=420,
                          xaxis_title="input size (n)", yaxis_title="time (ms, log scale)",
                          yaxis_type="log", margin=dict(l=10, r=10, t=40, b=10),
                          legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig, width="stretch")
    else:
        st.line_chart(df)


def get_source(func) -> str:
    try:
        return textwrap.dedent(inspect.getsource(func))
    except Exception:
        return "# (source unavailable)"


def get_array(data_mode: str, seed: int, n_default=18, lo=5, hi=99) -> list[int]:
    if data_mode == "Custom":
        txt = st.text_input("Custom array (comma-separated)", "34, 7, 23, 32, 5, 62, 32, 2, 6, 9")
        try:
            arr = parse_int_list(txt)
            if len(arr) > 80:
                st.warning("Custom array truncated to 80 elements for smooth animation.")
                arr = arr[:80]
            return arr
        except Exception as e:
            st.error(f"Couldn't parse that: {e}. Using random data.")
    n = st.slider("Array size", 5, 60, n_default)
    return generate_random_array(n, lo, hi, seed=int(seed))


def maze_html(grid, rows, cols, start, goal, visited=None, path=None) -> str:
    visited = set(visited or [])
    pathset = set(path or [])
    dark = st.session_state.theme == "Dark"
    cells = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if (r, c) == start:
                col = "#22c55e"
            elif (r, c) == goal:
                col = "#ef4444"
            elif (r, c) in pathset:
                col = "#7c3aed"
            elif (r, c) in visited:
                col = "#f59e0b"
            elif grid[r][c] == 1:
                col = "#334155" if dark else "#cbd5e1"
            else:
                col = "#1e293b" if dark else "#f1f5f9"
            row.append(f"<div class='maze-cell' style='background:{col}'></div>")
        cells.append("".join(row) + "<br>")
    return "".join(cells)


def pegs_html(pegs, theme: dict) -> str:
    html = "<div style='display:flex;gap:24px'>"
    for name in ["A", "B", "C"]:
        stack = pegs[name]
        bars = "".join(
            f"<div style='background:linear-gradient(90deg,#7c3aed,#06b6d4);"
            f"height:20px;width:{10+d*22}px;margin:2px auto;border-radius:6px'></div>"
            for d in reversed(stack)) or "<div style='height:20px'></div>"
        html += (f"<div style='flex:1;text-align:center;background:{theme['card']};"
                 f"border-radius:12px;padding:10px'><b>Peg {name}</b><br>{bars}</div>")
    return html + "</div>"


def chess_html(queens, n: int) -> str:
    html = "<table class='chess'>"
    for r in range(n):
        html += "<tr>"
        for c in range(n):
            bg = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"
            q = "♛" if queens[r] == c else ""
            html += f"<td style='background:{bg}'>{q}</td>"
        html += "</tr>"
    return html + "</table>"


# ================================================================= LEARN =====
def render_learn(meta: dict, algo_ids: list[str], algo_id: str) -> None:
    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.subheader("💡 How it works")
        st.write(meta["explanation"])
        st.info(f"**Best for:** {meta['best_for']}")
        rows = [{"Algorithm": ALGORITHMS[k]["name"], "Time": ALGORITHMS[k]["time"],
                 "Space": ALGORITHMS[k]["space"]} for k in algo_ids]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    with col_b:
        st.subheader("📊 At a glance")
        st.markdown(f"<div class='big-number'>{meta['time'].split(',')[0]}</div>"
                    f"<span class='muted'>time complexity</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-number'>{meta['space']}</div>"
                    f"<span class='muted'>space complexity</span>", unsafe_allow_html=True)
    st.subheader("🐍 Clean, commented implementation")
    st.code(get_source(get_function(algo_id)), language="python")


# =========================================================== VISUALIZE ======
def render_visualize(*, category: str, algo_id: str, meta: dict,
                     data_mode: str, seed: int, speed: float, theme: dict) -> None:
    # ---------------- SORTING ----------------
    if category == "Sorting":
        arr = get_array(data_mode, seed)
        st.write(f"Input array ({len(arr)} elements): `{arr}`")
        if st.button("▶️ Animate sort", type="primary", key="sort_run"):
            steps = list(get_steps(algo_id)(arr))
            stride = max(1, len(steps) // 400)
            frames = steps[::stride]
            chart = st.empty()
            msg = st.empty()
            prog = st.progress(0)
            for i, (snap, hl, label) in enumerate(frames):
                fig = bar_fig(snap, hl, f"{meta['name']} — step {i+1}/{len(frames)}", theme)
                if fig is not None:
                    chart.plotly_chart(fig, width="stretch", key=f"sf{i}")
                else:
                    chart.bar_chart(pd.DataFrame({"v": snap}))
                msg.markdown(f"**{label}**")
                prog.progress((i + 1) / len(frames))
                if speed:
                    time.sleep(speed)
            st.success(f"Sorted in {len(steps)} micro-steps → `{frames[-1][0]}`")
            st.balloons()
        else:
            fig = bar_fig(arr, {}, "Preview — press ▶️ Animate sort", theme)
            if fig is not None:
                st.plotly_chart(fig, width="stretch")
            else:
                st.bar_chart(pd.DataFrame({"v": arr}))

    # ---------------- SEARCHING ----------------
    elif category == "Searching":
        base = get_array(data_mode, seed, 20)
        if algo_id != "linear":
            base = sorted(base)
            st.caption("Sorted automatically (required for binary / jump / interpolation).")
        st.write(f"Array: `{base}`")
        target = st.number_input("Target value", value=int(base[len(base)//2]) if base else 0)
        if st.button("🔍 Step through search", type="primary"):
            tracer = get_steps(algo_id)(base, int(target))
            visited, found_idx = [], -1
            try:
                while True:
                    visited, m = next(tracer)
                    st.markdown(f"- {m}")
            except StopIteration as e:
                found_idx = e.value
            hl = {i: ("sorted" if base[i] == target else "compare") for i in visited}
            fig = bar_fig(base, hl, f"{meta['name']} — visited {len(visited)} indices", theme)
            if fig is not None:
                st.plotly_chart(fig, width="stretch")
            else:
                st.bar_chart(pd.DataFrame({"v": base}))
            if found_idx != -1:
                st.success(f"Found {target} at index {found_idx} after visiting {len(visited)} positions.")
            else:
                st.warning(f"{target} not in array. Visited {len(visited)} positions.")

    # ---------------- GRAPH ----------------
    elif category == "Graph":
        n = st.slider("Nodes", 4, 12, 7)
        p = st.slider("Edge density", 0.1, 0.8, 0.35, 0.05)
        adj = generate_random_graph(n, p, True, seed=int(seed))
        edges = sorted({tuple(sorted((u, v)) + [w]) for u, nbs in adj.items() for v, w in nbs})
        st.write(f"Random connected graph — {n} nodes, {len(edges)} edges (seed {int(seed)})")
        st.dataframe(pd.DataFrame(
            [{"from": u, "to": v, "weight": w} for u, v, w in edges]),
            width="stretch", hide_index=True)
        start = st.number_input("Start node", 0, n - 1, 0)
        goal = st.number_input("Goal node (Dijkstra/A*)", 0, n - 1, min(n - 1, 3))
        if st.button("▶️ Run algorithm", type="primary"):
            if algo_id in ("bfs", "dfs"):
                order = graph_algos.bfs(adj, start) if algo_id == "bfs" else graph_algos.dfs(adj, start)
                label = algo_id.upper()
                box = st.empty()
                prog = st.progress(0)
                for i in range(len(order)):
                    box.markdown(f"**{label} order:** {'→ '.join(map(str, order[:i+1]))}")
                    prog.progress((i + 1) / len(order))
                    if speed:
                        time.sleep(min(speed, 0.3))
                st.success(f"{label} order: {order}")
            elif algo_id == "dijkstra":
                dist, prev = graph_algos.dijkstra(adj, start)
                path = graph_algos.reconstruct_path(prev, start, goal)
                c1, c2 = st.columns(2)
                c1.metric("Distance to goal", f"{dist.get(goal, float('inf'))}")
                c2.write(f"Path: `{path if path else 'unreachable'}`")
                st.dataframe(pd.DataFrame(
                    [{"node": k, "dist": v} for k, v in sorted(dist.items())]),
                    width="stretch", hide_index=True)
                fig_df = pd.DataFrame({"dist": [dist[k] for k in sorted(dist)]})
                st.bar_chart(fig_df)
            elif algo_id == "astar":
                pos = {i: (i % 4, i // 4) for i in range(n)}  # grid-ish heuristic

                def h(a, b):
                    return abs(pos[a][0] - pos[b][0]) + abs(pos[a][1] - pos[b][1])

                path, cost = graph_algos.astar(adj, start, goal, h)
                st.success(f"A* path: {path} (cost {cost})")
            elif algo_id == "kruskal":
                mst, total = graph_algos.kruskal(adj)
                st.success(f"MST weight = {total}")
                st.dataframe(pd.DataFrame(
                    [{"from": u, "to": v, "w": w} for u, v, w in mst]),
                    width="stretch", hide_index=True)
            else:  # prim
                mst, total = graph_algos.prim(adj, start)
                st.success(f"MST weight = {total} (grown from {start})")
                st.dataframe(pd.DataFrame(
                    [{"from": u, "to": v, "w": w} for u, v, w in mst]),
                    width="stretch", hide_index=True)

    # ---------------- DYNAMIC PROGRAMMING ----------------
    elif category == "Dynamic Programming":
        if algo_id == "fib":
            n = st.slider("Fibonacci n", 0, 30, 12)
            seq = dp.fib_sequence(n)
            c1, c2, c3 = st.columns(3)
            c1.metric("F(n) tabulated", seq[-1])
            c2.metric("F(n) memoized", dp.fib_memo(n))
            with c3:
                if n <= 22:
                    t0 = time.perf_counter()
                    dp.fib_recursive(n)
                    t1 = time.perf_counter()
                    st.metric("Naive recursion time", format_ms((t1 - t0) * 1000))
                else:
                    st.caption("Naive recursion skipped for n>22 (would hang!).")
            st.line_chart(pd.DataFrame({"Fibonacci": seq}))
            st.caption("Watch it explode exponentially — that hockey-stick curve is why memoization matters.")
        elif algo_id == "knapsack":
            st.write("Weights / values (comma-separated), capacity slider.")
            w_txt = st.text_input("Weights", "2, 3, 4, 5")
            v_txt = st.text_input("Values", "3, 4, 5, 6")
            cap = st.slider("Capacity", 1, 30, 8)
            try:
                ws = parse_int_list(w_txt)
                vs = parse_int_list(v_txt)
            except ValueError as e:
                st.error(f"Couldn't parse that: {e}")
                ws = vs = None
            if ws is not None:
                if len(ws) != len(vs):
                    st.error("Weights and values must have equal length.")
                else:
                    best, chosen, table = dp.knapsack_01(ws, vs, cap)
                    st.success(f"Max value = **{best}**, take items {chosen}")
                    st.dataframe(pd.DataFrame(table,
                                 columns=[f"c={c}" for c in range(cap + 1)]),
                                 width="stretch")
        elif algo_id == "lcs":
            a = st.text_input("String A", "AGGTAB")
            b = st.text_input("String B", "GXTXAYB")
            s, length, table = dp.lcs(a, b)
            st.success(f"LCS = **'{s}'** (length {length})")
            st.dataframe(pd.DataFrame(table), width="stretch")
        else:  # coin change
            coins_txt = st.text_input("Coins", "1, 5, 10, 25")
            amount = st.slider("Amount", 0, 200, 63)
            try:
                coins = parse_int_list(coins_txt)
            except ValueError as e:
                st.error(f"Couldn't parse that: {e}")
                coins = None
            if coins is not None:
                count, used = dp.coin_change_min(coins, amount)
                ways = dp.coin_change_ways(coins, amount)
                st.success(f"Min coins: **{count}** → {used} · combinations: **{ways}**")

    # ---------------- PATHFINDING / MAZE ----------------
    elif category == "Pathfinding / Maze":
        rows = st.slider("Rows", 5, 25, 13)
        cols = st.slider("Cols", 7, 31, 19)
        wall_p = st.slider("Wall density", 0.0, 0.45, 0.26, 0.01)
        # sidebar seed changes must take effect again after a "New maze" click
        if st.session_state.get("_maze_seed_src") != int(seed):
            st.session_state["_maze_seed_src"] = int(seed)
            st.session_state.pop("maze_seed", None)
        if st.button("🎲 New maze", key="newmaze"):
            st.session_state.maze_seed = random.randint(0, 99999)
        mseed = st.session_state.get("maze_seed", int(seed))
        grid = generate_maze(rows, cols, wall_p, seed=mseed)
        start, goal = (0, 0), (rows - 1, cols - 1)
        grid[start[0]][start[1]] = 0
        grid[goal[0]][goal[1]] = 0

        def draw(g, visited=None, path=None):
            return maze_html(g, rows, cols, start, goal, visited, path)

        if st.button("▶️ Solve maze", type="primary"):
            result = get_function(algo_id)(grid, start, goal)
            path, order = result[0], result[1]  # dijkstra returns a 3rd cost value
            box = st.empty()
            msg = st.empty()
            prog = st.progress(0)
            stride = max(1, len(order) // 200)
            shown = order[::stride]
            for i in range(len(shown)):
                box.markdown(draw(grid, shown[:i + 1]), unsafe_allow_html=True)
                msg.caption(f"Exploring… {min((i + 1) * stride, len(order))}/{len(order)} cells")
                prog.progress((i + 1) / len(shown))
                if speed:
                    time.sleep(speed / 3)
            box.markdown(draw(grid, order, path), unsafe_allow_html=True)
            if path:
                st.success(f"Path found! length={len(path)}, explored={len(order)} cells.")
                st.balloons()
            else:
                st.error("No path exists — try fewer walls or a new maze.")
        else:
            st.markdown(draw(grid), unsafe_allow_html=True)
            st.caption("Press ▶️ Solve maze to animate the search. 🟩 start · 🟥 goal · 🟧 explored · 🟪 path")

    # ---------------- STRING ----------------
    elif category == "String":
        text = st.text_area("Text", generate_random_text(220, seed=int(seed)) if data_mode == "Random"
                            else "ababcababcabcababc", height=100)
        pattern = st.text_input("Pattern", "abc")
        if st.button("🔤 Find matches", type="primary"):
            if algo_id == "naive_string":
                matches = strings.naive_search(text, pattern)
                st.success(f"Naive: {len(matches)} match(es) at {matches[:20]}")
            elif algo_id == "kmp":
                pi = strings.kmp_prefix(pattern)
                st.write(f"Prefix table π = `{pi}`")
                gen = strings.kmp_search_steps(text, pattern)
                msgs = []
                try:
                    while True:
                        i, j, m = next(gen)
                        msgs.append(m)
                except StopIteration as e:
                    matches = e.value
                with st.expander(f"KMP trace ({len(msgs)} steps, showing first 60)"):
                    for m in msgs[:60]:
                        st.markdown(f"- {m}")
                st.success(f"KMP: {len(matches)} match(es) at {matches[:20]}")
            else:
                gen = strings.rabin_karp_steps(text, pattern)
                try:
                    while True:
                        next(gen)
                except StopIteration as e:
                    matches = e.value
                st.success(f"Rabin-Karp: {len(matches)} match(es) at {matches[:20]}")
            if matches and pattern:
                hl_text = text
                for m in sorted(matches, reverse=True)[:50]:
                    hl_text = (hl_text[:m] + "⟦" + hl_text[m:m + len(pattern)] + "⟧"
                               + hl_text[m + len(pattern):])
                st.text_area("Matches marked with ⟦ ⟧", hl_text, height=120)

    # ---------------- EXTRAS ----------------
    else:
        if algo_id == "hanoi":
            n = st.slider("Disks", 1, 7, 4)
            moves = extras.hanoi(n)
            st.write(f"Optimal solution = **2^{n} − 1 = {len(moves)} moves**")

            if st.button("▶️ Animate solution", type="primary"):
                box = st.empty()
                msg = st.empty()
                prog = st.progress(0)
                for i, (dsk, s, t) in enumerate(moves):
                    state = extras.hanoi_pegs_state(n, moves[:i + 1])
                    box.markdown(pegs_html(state, theme), unsafe_allow_html=True)
                    msg.markdown(f"**Move {i + 1}/{len(moves)}:** disk {dsk} {s} → {t}")
                    prog.progress((i + 1) / len(moves))
                    if speed:
                        time.sleep(speed + 0.05)
                st.success("Solved! 🎉")
                st.balloons()
            else:
                st.markdown(pegs_html(extras.hanoi_pegs_state(n, []), theme), unsafe_allow_html=True)
            with st.expander("Full move list"):
                for i, (dsk, s, t) in enumerate(moves, 1):
                    st.markdown(f"{i}. disk {dsk}: {s} → {t}")
        else:  # nqueens
            n = st.slider("Board size N", 4, 10, 8)
            maxsol = st.slider("Solutions to show", 1, 6, 3)
            if st.button("👑 Solve N-Queens", type="primary"):
                with st.spinner("Backtracking…"):
                    sols = extras.nqueens(n, max_solutions=maxsol)
                    total = extras.nqueens_count(n) if n <= 10 else "?"
                st.success(f"Showing {len(sols)} of {total} total solutions for N={n}")
                for si, queens in enumerate(sols, 1):
                    st.markdown(f"**Solution {si}:** `{queens}`")
                    st.markdown(chess_html(queens, n), unsafe_allow_html=True)


# ============================================================ BENCHMARK =====
def render_benchmark(*, category: str, algo_id: str, meta: dict,
                     seed: int, theme: dict) -> None:
    st.subheader(f"⏱️ Live benchmark — {meta['name']}")
    sizes_txt = st.text_input("Input sizes (comma-separated)", "100, 500, 1000, 2000, 5000")
    try:
        sizes = [int(x) for x in sizes_txt.split(",") if x.strip()]
    except ValueError:
        st.error("Sizes must be integers.")
        sizes = []
    repeats = st.slider("Repeats per size", 1, 7, 3)
    if st.button("🚀 Run benchmark", type="primary") and sizes:
        results = {}
        prog = st.progress(0)
        status = st.empty()
        if category == "Sorting":
            fn = get_function(algo_id)
            for idx, n in enumerate(sizes):
                base = generate_random_array(n, seed=int(seed))
                status.write(f"Benchmarking n={n}… ({idx + 1}/{len(sizes)})")
                results[n] = benchmark(fn, list(base), repeats=repeats)["best_ms"]
                prog.progress((idx + 1) / len(sizes))
        elif category == "Searching":
            st.caption("Target = last element (worst case) — same strategy as the Compare tab.")
            fn = get_function(algo_id)
            for idx, n in enumerate(sizes):
                arr = sorted(generate_random_array(n, seed=int(seed)))
                tgt = arr[-1] if arr else 0
                status.write(f"Benchmarking n={n}…")
                results[n] = benchmark(fn, arr, tgt, repeats=repeats)["best_ms"]
                prog.progress((idx + 1) / len(sizes))
        elif category == "String":
            fn = get_function(algo_id)
            for idx, n in enumerate(sizes):
                txt = generate_random_text(n, seed=int(seed))
                status.write(f"Benchmarking chars={n}…")
                results[n] = benchmark(fn, txt, "abc", repeats=repeats)["best_ms"]
                prog.progress((idx + 1) / len(sizes))
        elif category == "Dynamic Programming":
            capped = []
            fn = get_function(algo_id)
            for idx, n in enumerate(sizes):
                status.write(f"Benchmarking n={n}…")
                if algo_id == "fib":
                    actual = min(n, 5000)
                    results[actual] = benchmark(fn, actual, repeats=repeats)["best_ms"]
                elif algo_id == "coinchange":
                    actual = min(n, 2000)
                    results[actual] = benchmark(fn, [1, 5, 10, 25], actual,
                                                repeats=repeats)["best_ms"]
                elif algo_id == "lcs":
                    actual = min(n, 400)
                    results[actual] = benchmark(fn, "A" * actual, "B" * actual, repeats=1)["best_ms"]
                else:  # knapsack: n = number of items
                    actual = min(n, 60)
                    ws = list(range(1, actual + 1))
                    vs = [w * 2 for w in ws]
                    results[actual] = benchmark(fn, ws, vs, min(n, 300), repeats=1)["best_ms"]
                if actual != n:
                    capped.append(f"n={n} → {actual}")
                prog.progress((idx + 1) / len(sizes))
            if capped:
                st.warning("Some sizes were capped for feasibility: "
                           + ", ".join(capped)
                           + ". Chart shows the actual sizes run.")
        else:
            st.info("Benchmarking is richest for Sorting/Searching/Strings/DP. "
                    "Use ⚔️ Compare for graph & maze algorithm tables.")
            results = {}
        if results:
            df = pd.DataFrame({"ms": results})
            st.dataframe(df.style.format({"ms": "{:.3f}"}), width="stretch")
            benchmark_chart(pd.DataFrame({meta["name"]: results}),
                            "Execution time vs input size", theme)
            st.toast("Benchmark finished!", icon="⚡")


# ============================================================== COMPARE =====
def render_compare(*, category: str, algo_ids: list[str], seed: int, theme: dict) -> None:
    st.subheader(f"⚔️ Side-by-side — {category}")
    if category == "Sorting":
        chosen = st.multiselect("Algorithms to compare", algo_ids,
                                default=algo_ids[:4],
                                format_func=lambda k: ALGORITHMS[k]["name"])
        if st.button("⚔️ Run comparison", type="primary") and chosen:
            try:
                sizes_c = [int(x) for x in st.text_input("Sizes", "200, 800, 2000",
                                                         key="cmp_sizes").split(",") if x.strip()]
            except ValueError:
                sizes_c = [200, 800, 2000]
            table: dict[str, dict] = {ALGORITHMS[c]["name"]: {} for c in chosen}
            prog = st.progress(0)
            total = len(sizes_c) * len(chosen)
            done = 0
            for n in sizes_c:
                base = generate_random_array(n, seed=int(seed))
                for c in chosen:
                    ms = benchmark(get_function(c), list(base), repeats=3)["best_ms"]
                    table[ALGORITHMS[c]["name"]][n] = ms
                    done += 1
                    prog.progress(done / total)
            df = pd.DataFrame(table)
            st.dataframe(df.style.format("{:.3f}").highlight_min(axis=1, color="#22c55e55"),
                         width="stretch")
            benchmark_chart(df, "Sorting showdown — lower is faster ⚡", theme)
            winner = df.iloc[-1].idxmin()
            st.success(f"🏆 Fastest at n={df.index[-1]}: **{winner}** ({format_ms(df.iloc[-1].min())})")
            st.balloons()
            with st.expander("👀 Code side-by-side"):
                cols = st.columns(len(chosen))
                for col, c in zip(cols, chosen):
                    with col:
                        st.markdown(f"**{ALGORITHMS[c]['name']}**")
                        st.code(get_source(get_function(c)), language="python")
    elif category == "Searching":
        chosen = st.multiselect("Algorithms", algo_ids,
                                default=["linear", "binary"],
                                format_func=lambda k: ALGORITHMS[k]["name"], key="cmp_s")
        if st.button("⚔️ Run comparison", type="primary", key="cmp_s_go") and chosen:
            sizes_c = [200, 1000, 5000, 20000]
            table = {ALGORITHMS[c]["name"]: {} for c in chosen}
            for n in sizes_c:
                arr = sorted(generate_random_array(n, seed=int(seed)))
                tgt = arr[-1]  # worst case → fair fight
                for c in chosen:
                    table[ALGORITHMS[c]["name"]][n] = benchmark(
                        get_function(c), arr, tgt, repeats=5)["best_ms"]
            df = pd.DataFrame(table)
            st.dataframe(df.style.format("{:.4f}").highlight_min(axis=1, color="#22c55e55"),
                         width="stretch")
            benchmark_chart(df, "Searching showdown (worst-case target)", theme)
    elif category == "String":
        txt = generate_random_text(5000, seed=int(seed))
        pat = st.text_input("Pattern", "abcab", key="cmp_pat")
        if st.button("⚔️ Run comparison", type="primary", key="cmp_str_go"):
            res = {name: benchmark(get_function(fid), txt, pat, repeats=3)["best_ms"]
                   for name, fid in [("Naive", "naive_string"), ("KMP", "kmp"),
                                     ("Rabin-Karp", "rabinkarp")]}
            st.dataframe(pd.DataFrame([res]).T.rename(columns={0: "ms"}).style.format("{:.3f}"),
                         width="stretch")
            st.bar_chart(pd.DataFrame(res, index=["ms"]).T)
    else:
        st.info("Head-to-head timing is most meaningful for Sorting / Searching / Strings. "
                "For this category, compare the complexity table instead:")
        rows = [{"Algorithm": ALGORITHMS[k]["name"], "Time": ALGORITHMS[k]["time"],
                 "Space": ALGORITHMS[k]["space"],
                 "Best for": ALGORITHMS[k]["best_for"]} for k in algo_ids]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.caption("Tip: switch to the Sorting category and hit ⚔️ Compare to see the full racing experience.")
