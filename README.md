# 🧪 Algorithm Playground

[![CI](https://github.com/AmirHKD1386/algorithm-playground/actions/workflows/ci.yml/badge.svg)](https://github.com/AmirHKD1386/algorithm-playground/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A modern, interactive playground for **classic algorithms** — learn how they work,
watch them run step-by-step, benchmark them live, and race them head-to-head.

- 🖥️ **Streamlit GUI** — dark/light theme, animated bar charts, maze animator,
  N-Queens chessboards, Hanoi towers, syntax-highlighted code, Plotly timing charts
- ⌨️ **Rich CLI** — colorful tables, `list / show / bench-sorting / search / hanoi / nqueens / strings`
- 📦 **Clean modular code** — one file per category under `algorithms/`, single-source registry

## ✨ What's inside

| Category | Algorithms |
|---|---|
| 🔀 Sorting | Bubble, Selection, Insertion, Merge, Quick, Heap, Timsort (`sorted`) |
| 🔍 Searching | Linear, Binary, Jump, Interpolation |
| 🕸️ Graph | BFS, DFS, Dijkstra, A\*, Kruskal, Prim |
| 🧠 Dynamic Programming | Fibonacci (naive/memo/tab), 0/1 Knapsack, LCS, Coin Change |
| 🗺️ Pathfinding / Maze | BFS, DFS, Dijkstra, A\* on random mazes with animation |
| 🔤 String | Naive, KMP, Rabin-Karp |
| 🎉 Extras | Tower of Hanoi (animated), N-Queens visualizer |

Every algorithm ships with: clean commented implementation · Big-O time/space ·
friendly explanation · step generator for animation · benchmark harness.

## 🚀 Quickstart

```bash
git clone https://github.com/AmirHKD1386/algorithm-playground.git
cd algorithm-playground
pip install -r requirements.txt

# GUI (recommended)
streamlit run app.py

# CLI
python cli.py list
python cli.py show quick
python cli.py bench-sorting --sizes 200,1000,3000 --algos bubble,quick,merge,timsort
python cli.py search --algo binary --n 10000
python cli.py hanoi --disks 4
python cli.py nqueens --n 8
python cli.py strings --chars 20000 --pattern abcab
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## 🗂️ Project structure

```
algorithm-playground/
├── app.py                  # Streamlit entry point (sidebar + tab wiring)
├── views.py                # Learn / Visualize / Benchmark / Compare renderers
├── cli.py                  # Rich-powered CLI
├── requirements.txt
├── requirements-dev.txt     # pytest + ruff
├── pyproject.toml           # metadata, ruff/pytest config
├── LICENSE                  # MIT
├── .streamlit/config.toml   # dark theme defaults
├── .github/workflows/ci.yml # ruff + pytest on 3.10–3.12
├── tests/                   # 229 tests (unit + CLI + Streamlit AppTest)
└── algorithms/
    ├── __init__.py
    ├── sorting.py           # 7 sorts + *_steps() generators for animation
    ├── searching.py         # 4 searches + step traces
    ├── graph.py             # BFS/DFS/Dijkstra/A*/Kruskal/Prim + shared search cores
    ├── dynamic_programming.py  # Fib, Knapsack, LCS, Coin Change
    ├── pathfinding.py       # grid BFS/DFS/Dijkstra/A* via grid_to_adjacency
    ├── strings.py           # Naive, KMP (+prefix table), Rabin-Karp
    ├── extras.py            # Hanoi, N-Queens
    ├── registry.py          # names, Big-O, explanations (single source of truth)
    └── utils.py             # random data, timing, parsing, maze generator
```

## 🎮 How to play

1. Pick a **category + algorithm** in the sidebar.
2. **📚 Learn** — read the friendly explanation + complexity badges + real source code.
3. **▶️ Visualize** — random or custom data, press animate, drag the speed slider.
4. **⏱️ Benchmark** — type input sizes (e.g. `100, 500, 1000, 2000, 5000`), hit run, watch the log-scale chart.
5. **⚔️ Compare** — multi-select algorithms, race them on identical data, see winner + side-by-side code.
6. Toggle **Dark/Light** theme anytime in the sidebar.

### Fun challenges
- Race `bubble` vs `timsort` at n=3000. How many × faster is Timsort?
- Binary vs interpolation search on uniform data (n=20000, worst-case target).
- Solve a 13×19 maze with BFS vs DFS vs A\* — count explored cells.
- N=8 queens: find all 92 solutions (we show a few; `nqueens_count(8)` proves 92).
- Hanoi with 7 disks = 127 moves. With 64 disks? 585 billion years at 1 move/sec. 😱

## 🧪 Tests & quality

```bash
pip install -r requirements-dev.txt

# full suite (229 tests: algorithms, registry, pathfinding, edge cases, CLI, AppTest)
pytest tests/ -q

# lint
ruff check .

# optional: install git hooks
pre-commit install
pre-commit run --all-files
```

CI runs ruff + pytest on Python 3.10, 3.11, and 3.12 for every push and PR.

## 📝 Notes

- Sorting `*_sort()` functions never mutate the caller's list (they copy).
- Benchmarks use `timeit.repeat` best-of; charts use log-scale y so O(n²) vs O(n log n) gaps stay readable.
- Plotly is optional — the app falls back to native Streamlit charts if it's missing.
- No API keys, no network, no database. Everything runs locally.

## 📄 License

MIT — see [LICENSE](LICENSE).
