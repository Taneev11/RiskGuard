import streamlit as st
import httpx
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RiskGuard", layout="wide")
st.title("RiskGuard — Compliance Scoreboard")

uploaded = st.file_uploader("Upload portfolio (CSV or JSON)", type=["csv", "json"])

if uploaded:
    with st.spinner("Running risk assessment..."):
        resp = httpx.post(
            f"{API_URL}/upload-portfolio",
            files={"file": (uploaded.name, uploaded.getvalue(), "multipart/form-data")},
        )

    if resp.status_code != 200:
        st.error(f"API error: {resp.text}")
    else:
        report = resp.json()

        col1, col2 = st.columns(2)
        col1.metric("Total Portfolio Value", f"${report['total_value']:,.2f}")
        col2.metric("Violations Found", len(report["violations"]))

        st.subheader("Sector Weights")
        for sector, weight in report["sector_weights"].items():
            pct = weight * 100
            if pct > 25:
                st.error(f"🔴 {sector}: {pct:.1f}%  (limit: 25%)")
            else:
                st.success(f"🟢 {sector}: {pct:.1f}%")

        st.subheader("Volatility by Ticker")
        st.bar_chart(report["volatility_by_ticker"])

        if report["violations"]:
            st.subheader("Compliance Violations")
            st.dataframe(pd.DataFrame(report["violations"]))

st.divider()
st.subheader("Audit Trail (last 50 violations)")
audit = httpx.get(f"{API_URL}/violations").json()
if audit:
    st.dataframe(pd.DataFrame(audit))
else:
    st.info("No violations on record.")