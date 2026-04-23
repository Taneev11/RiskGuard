import asyncpg
import os
from typing import Any

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rguser:riskguard@localhost/riskguard")

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)

async def insert_trade(conn, row: dict):
    await conn.execute(
        """INSERT INTO trades (ticker, quantity, avg_purchase_price, trade_type)
           VALUES ($1, $2, $3, $4)""",
        row["ticker"], row["quantity"], row["avg_purchase_price"], row.get("trade_type", "BUY")
    )

async def insert_violation(conn, v: dict):
    import json
    await conn.execute(
        """INSERT INTO compliance_violations (rule_name, ticker, sector, details)
           VALUES ($1, $2, $3, $4)""",
        v["rule_name"], v.get("ticker"), v.get("sector"), json.dumps(v.get("details", {}))
    )

async def fetch_violations(limit: int = 50) -> list[dict]:
    conn = await get_connection()
    rows = await conn.fetch(
        "SELECT * FROM compliance_violations ORDER BY triggered_at DESC LIMIT $1", limit
    )
    await conn.close()
    return [dict(r) for r in rows]

async def check_wash_sale(conn, ticker: str) -> bool:
    """Returns True if ticker was both bought and sold in the last 30 days."""
    rows = await conn.fetch(
        """SELECT trade_type FROM trades
           WHERE ticker = $1 AND created_at > NOW() - INTERVAL '30 days'""",
        ticker
    )
    types = {r["trade_type"] for r in rows}
    return "BUY" in types and "SELL" in types