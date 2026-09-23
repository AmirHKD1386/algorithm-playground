"""Algorithm Playground — a fun, visual way to learn classic algorithms.

Run with:  streamlit run app.py

Thin entry point: page config, sidebar, header, and tab wiring.
All rendering lives in ``views.py``; all algorithm dispatch goes through
``algorithms.registry`` (``get_function`` / ``get_steps``).
"""
from __future__ import annotations

import streamlit as st

from algorithms.registry import ALGORITHMS, CATEGORIES, CATEGORY_ICONS, algo_ids_for_category
from views import (
    THEMES,
    inject_css,
    render_benchmark,
    render_compare,
    render_learn,
    render_visualize,
)

st.set_page_config(
    page_title="Algorithm Playground",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

inject_css(THEMES[st.session_state.theme])

# ================================================================ sidebar ===
with st.sidebar:
    st.markdown("# 🧪 Algorithm Playground")
    st.caption("Learn · Visualize · Benchmark · Compare — the fun way.")
    st.session_state.theme = st.radio("🎨 Theme", ["Dark", "Light"], horizontal=True,
                                      index=0 if st.session_state.theme == "Dark" else 1)
    T = THEMES[st.session_state.theme]
    inject_css(T)
    category = st.selectbox("📂 Category", CATEGORIES,
                            format_func=lambda c: f"{CATEGORY_ICONS.get(c,'')} {c}")
    algo_ids = algo_ids_for_category(category)
    algo_id = st.selectbox("🧠 Algorithm",
                           algo_ids, format_func=lambda k: ALGORITHMS[k]["name"])
    st.divider()
    st.markdown("### 🎲 Data")
    data_mode = st.radio("Input", ["Random", "Custom"], horizontal=True)
    seed = st.number_input("Seed", value=42, step=1)
    st.caption("Tip: change the seed for fresh random data. Share a seed with a friend to compare identical inputs!")
    st.divider()
    st.markdown("### ⚡ Animation")
    speed = st.slider("Speed (delay/step)", 0.0, 0.8, 0.08, 0.01,
                      help="Lower = faster animation")
    st.divider()
    st.markdown("`pip install -r requirements.txt` · `streamlit run app.py`")

meta = ALGORITHMS[algo_id]

# ================================================================= header ===
st.markdown(f"# {CATEGORY_ICONS.get(category,'')} {meta['name']}")
st.markdown(f"""
<div class="algo-card">
  <span class="badge badge-time">⏱ {meta['time']}</span>
  <span class="badge badge-space">💾 {meta['space']}</span>
  <span class="badge badge-diff">📶 {meta['difficulty']}</span><br><br>
  {meta['explanation']}<br>
  <span class="muted">⭐ Best for: {meta['best_for']}</span>
</div>
""", unsafe_allow_html=True)

tab_learn, tab_play, tab_bench, tab_compare = st.tabs(
    ["📚 Learn", "▶️ Visualize", "⏱️ Benchmark", "⚔️ Compare"])

with tab_learn:
    render_learn(meta, algo_ids, algo_id)

with tab_play:
    render_visualize(category=category, algo_id=algo_id, meta=meta,
                     data_mode=data_mode, seed=int(seed), speed=speed, theme=T)

with tab_bench:
    render_benchmark(category=category, algo_id=algo_id, meta=meta,
                     seed=int(seed), theme=T)

with tab_compare:
    render_compare(category=category, algo_ids=algo_ids, seed=int(seed), theme=T)

st.divider()
st.caption("Built with ❤️ + Streamlit · clean modular code under `algorithms/` · "
           "try the Rich CLI too: `python cli.py --help`")
