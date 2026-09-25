"""Legacy Bridge demo page: one click runs the pipeline and shows the report.

Run locally:  streamlit run app.py
Mode: live Bob if BOB_CMD is set, otherwise a replay of recorded Bob sessions.
"""

import os
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "harness"))

from bridge import pipeline, report  # noqa: E402
from bridge.bob import BobError  # noqa: E402
from bridge.cli import BENIGN_GOAL, REGRESSION_GOAL  # noqa: E402

st.set_page_config(page_title="Legacy Bridge", layout="wide")
st.title("Legacy Bridge")
st.caption("IBM Bob modernizes legacy Java. Bob's own characterization tests decide what ships.")

default_mode = os.environ.get("BRIDGE_MODE") or ("cli" if os.environ.get("BOB_CMD") else "replay")
labels = {"replay": "Replay recorded Bob sessions", "cli": "Live Bob", "fixture": "Fixture (not Bob, dev only)"}
mode = st.radio("Bob", list(labels), index=list(labels).index(default_mode), format_func=labels.get, horizontal=True)

with st.expander("The legacy file"):
    st.code(pipeline.original_source(), language="java")

goal = st.text_area("Second modernization request (the risky one)", REGRESSION_GOAL, height=90)

if st.button("Run the pipeline", type="primary"):
    run = pipeline.Run()
    try:
        with st.status("Working...", expanded=True) as status:
            st.write("Bob is writing characterization tests for the legacy file...")
            pipeline.generate_tests(run, mode)
            st.write("Bob is modernizing (behaviour-preserving request)...")
            pipeline.modernize(run, BENIGN_GOAL, "modernize-benign", mode)
            st.write("Bob is modernizing (risky request)...")
            pipeline.modernize(run, goal, "modernize-regression", mode)
            report.write(run)
            status.update(label="Done", state="complete")
    except BobError as e:
        st.error(f"Bob call failed: {e}")
        st.stop()
    components.html(report.render(run.state), height=1900, scrolling=True)
    st.download_button("Download report", (run.dir / "report.html").read_bytes(), "legacy-bridge-report.html", "text/html")
