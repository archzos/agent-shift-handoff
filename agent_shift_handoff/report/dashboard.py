"""Streamlit dashboard for handoff history."""

from __future__ import annotations

import argparse

import plotly.express as px
import streamlit as st

from agent_shift_handoff.report.store import fetch_dashboard_payload, fetch_latest_handoff


def render(db_path: str) -> None:
    st.set_page_config(page_title="agent-shift-handoff", layout="wide")
    st.title("agent-shift-handoff dashboard")

    payload = fetch_dashboard_payload(db_path)
    latest = fetch_latest_handoff(db_path)
    if latest is None:
        st.info("No handoffs found. Run `agent-shift-handoff generate` first.")
        return

    st.subheader(f"Latest session: {latest['session_id']}")
    st.caption(f"Agent: {latest['agent_id']} · Continuity: {latest['continuity_score']}")
    st.dataframe(payload["handoffs"], use_container_width=True)

    if payload["handoffs"]:
        fig = px.line(
            x=[row["produced_at"] for row in payload["handoffs"]],
            y=[row["continuity_score"] for row in payload["handoffs"]],
            labels={"x": "produced_at", "y": "continuity_score"},
            title="Continuity over time",
        )
        st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="state/sessions.sqlite")
    args = parser.parse_args()
    render(args.db)


if __name__ == "__main__":
    main()
