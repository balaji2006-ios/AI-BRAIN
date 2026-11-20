import streamlit as st
import pandas as pd

from assistant.evaluation.performance import PerformanceMonitor
from assistant.evaluation.cost_tracker import CostTracker
from assistant.health_check import run_full_health_check


def show_dashboard():
    st.title("📊 AI Brain Performance Dashboard")
    st.caption("Monitor response speed, memory usage, AI provider latency, and system health.")

    # ----------------------------------------------------
    # SYSTEM HEALTH OVERVIEW
    # ----------------------------------------------------
    st.subheader("🏥 System Health")
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)

    health = run_full_health_check()
    gemini_h = health.get("gemini", {})
    ollama_h = health.get("ollama", {})
    db_h = health.get("database", {})
    sys_h = health.get("resources", {})

    with health_col1:
        g_status = gemini_h.get("status")
        icon = "🟢" if g_status == "healthy" else ("🟡" if g_status == "unconfigured" else "🔴")
        st.metric("Gemini Cloud", f"{icon} {g_status.title()}", gemini_h.get("model", "N/A"))

    with health_col2:
        o_status = ollama_h.get("status")
        icon = "🟢" if o_status == "healthy" else ("🟡" if o_status in ("warning", "offline") else "🔴")
        st.metric("Local Gemma", f"{icon} {o_status.title()}", ollama_h.get("configured_model", "N/A"))

    with health_col3:
        d_status = db_h.get("status")
        icon = "🟢" if d_status == "healthy" else "🔴"
        st.metric("SQLite Memory", f"{icon} {d_status.title()}", "Active")

    with health_col4:
        ram_pct = sys_h.get("ram_percent", 0)
        cpu_pct = sys_h.get("cpu_percent", 0)
        st.metric("System RAM", f"{ram_pct}%", f"CPU: {cpu_pct}%")

    st.divider()

    # ----------------------------------------------------
    # PERFORMANCE METRICS
    # ----------------------------------------------------
    monitor = PerformanceMonitor()
    records = monitor.get_all_records()

    if not records:
        st.info("No performance records recorded yet. Start chatting to generate latency and memory logs!")
        return

    df = pd.DataFrame(records)

    # Ensure numeric columns
    for col in ("response_time", "ram_change_mb", "ram_after_mb", "cost_usd", "total_tokens"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    st.subheader("📈 Operational Metrics")

    total_requests = len(df)
    successful_requests = int((df["status"] == "Success").sum()) if "status" in df.columns else total_requests
    failed_requests = int((df["status"] == "Failed").sum()) if "status" in df.columns else 0
    average_time = df["response_time"].mean() if "response_time" in df.columns else 0.0
    total_cost = CostTracker.calculate_total_cost(records)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Invocations", total_requests)
    c2.metric("Successful", successful_requests)
    c3.metric("Failed", failed_requests)
    c4.metric("Avg Response Time", f"{average_time:.2f}s" if pd.notnull(average_time) else "0.00s")
    c5.metric("Est. Cloud Cost", f"${total_cost:.5f}")

    st.divider()

    # ----------------------------------------------------
    # PROVIDER COMPARISON & RAM CHART
    # ----------------------------------------------------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Provider Latency (Avg)")
        if "provider" in df.columns and "response_time" in df.columns:
            provider_lat = df.groupby("provider")["response_time"].mean()
            if not provider_lat.empty:
                st.bar_chart(provider_lat)
            else:
                st.caption("No provider latency data.")
        else:
            st.caption("Provider data unavailable.")

    with chart_col2:
        st.subheader("Process RAM Footprint (MB)")
        if "ram_after_mb" in df.columns:
            ram_series = df["ram_after_mb"].dropna().reset_index(drop=True)
            if not ram_series.empty:
                st.line_chart(ram_series)
            else:
                st.caption("No RAM tracking data.")
        else:
            st.caption("RAM data unavailable.")

    st.divider()

    # ----------------------------------------------------
    # DETAILED AUDIT LOGS
    # ----------------------------------------------------
    st.subheader("📋 Interaction Log")

    display_cols = [
        "timestamp",
        "provider",
        "status",
        "response_time",
        "ram_change_mb",
        "total_tokens",
        "cost_usd",
        "session_id",
    ]
    available_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[available_cols].iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Logs recorded in {monitor.log_file}")


if __name__ == "__main__":
    show_dashboard()
