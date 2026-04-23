import io
import polars as pl
from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
import asyncpg

from models import PortfolioUpload, RiskReport
from risk_engine import enrich_portfolio, compute_weights, compute_volatility, run_all_checks
from db import get_connection, insert_trade, insert_violation, fetch_violations, check_wash_sale

app = FastAPI(title="RiskGuard API")

@app.post("/upload-portfolio", response_model=RiskReport)
async def upload_portfolio(file: UploadFile = File(...)):
    content = await file.read()

    if file.filename.endswith(".csv"):
        df = pl.read_csv(io.BytesIO(content))
    elif file.filename.endswith(".json"):
        df = pl.read_json(io.BytesIO(content))
    else:
        raise HTTPException(400, "Only CSV or JSON files are accepted")

    required = {"ticker", "quantity", "avg_purchase_price"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(400, f"File must contain columns: {required}")

    enriched = compute_weights(enrich_portfolio(df))
    violations = run_all_checks(enriched)
    volatility = compute_volatility(df["ticker"].to_list())

    conn = await get_connection()
    try:
        for row in df.to_dicts():
            await insert_trade(conn, row)
            if await check_wash_sale(conn, row["ticker"]):
                violations.append({
                    "rule_name": "wash_sale",
                    "ticker": row["ticker"],
                    "details": {"window_days": 30},
                })
        for v in violations:
            await insert_violation(conn, v)
    finally:
        await conn.close()

    sector_weights = (
        enriched.group_by("sector")
        .agg((pl.col("market_value").sum() / enriched["market_value"].sum()).alias("weight"))
        .to_dicts()
    )

    return RiskReport(
        total_value=enriched["market_value"].sum(),
        volatility_by_ticker=volatility,
        sector_weights={r["sector"]: round(r["weight"], 4) for r in sector_weights},
        violations=violations,
    )

@app.get("/violations")
async def get_violations():
    return await fetch_violations()