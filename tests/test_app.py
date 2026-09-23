"""Streamlit AppTest smoke — the app must render every category without exceptions."""
from pathlib import Path

import pytest

v1 = pytest.importorskip("streamlit.testing.v1", reason="requires streamlit>=1.28")
AppTest = v1.AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"
CATEGORIES = ["Sorting", "Searching", "Graph", "Dynamic Programming",
              "Pathfinding / Maze", "String", "Extras"]


@pytest.fixture
def at():
    test_at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    test_at.run()
    return test_at


def test_app_renders_default_state(at):
    assert not at.exception, at.exception
    assert len(at.tabs) == 4
    # sidebar exposes category + algorithm pickers
    assert len(at.sidebar.selectbox) >= 2


def test_theme_toggle_renders(at):
    at.sidebar.radio[0].set_value("Light")
    at.run()
    assert not at.exception, at.exception


@pytest.mark.parametrize("category", CATEGORIES)
def test_each_category_renders(at, category):
    at.sidebar.selectbox[0].select(category)
    at.run()
    assert not at.exception, f"{category}: {at.exception}"


def test_algorithm_switch_within_category(at):
    at.sidebar.selectbox[0].select("Sorting")
    at.run()
    assert not at.exception
    at.sidebar.selectbox[1].select("merge")
    at.run()
    assert not at.exception, at.exception
    # Learn tab shows the selected algorithm's name
    assert any("Merge Sort" in getattr(md, "value", "") for md in at.markdown)
