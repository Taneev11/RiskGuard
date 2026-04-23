import polars as pl
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_market_data() -> pl.DataFrame:
    return pl.read_csv(DATA_DIR / "market_data.csv")

def load_price_history() -> pl.DataFrame:
    return pl.read_csv(DATA_DIR / "price_history.csv", try_parse_dates=True)

def enrich_portfolio(portfolio_df: pl.DataFrame) -> pl.DataFrame:
    """Join portfolio with market data to get price + sector."""
    market = load_market_data()
    return portfolio_df.join(market, on="ticker", how="left").with_columns(
        (pl.col("quantity") * pl.col("current_price")).alias("market_value")
    )

def compute_weights(enriched: pl.DataFrame) -> pl.DataFrame:
    total = enriched["market_value"].sum()
    return enriched.with_columns(
        (pl.col("market_value") / total).alias("weight")
    )

def compute_volatility(tickers: list[str]) -> dict:
    """Returns annualised daily volatility per ticker."""
    history = load_price_history()
    result = {}
    for ticker in tickers:
        ticker_df = (
            history.filter(pl.col("ticker") == ticker)
            .sort("date")
            .with_columns(pl.col("close").pct_change().alias("daily_return"))
            .drop_nulls()
        )
        if ticker_df.is_empty():
            continue
        std = ticker_df.select(pl.col("daily_return").std()).item()
        result[ticker] = round(std * (252 ** 0.5), 4)  # annualised
    return result

def check_concentration(enriched: pl.DataFrame) -> list[dict]:
    total = enriched["market_value"].sum()
    sector_weights = (
        enriched.group_by("sector")
        .agg(pl.col("market_value").sum().alias("sector_value"))
        .with_columns((pl.col("sector_value") / total).alias("sector_weight"))
    )
    violations = []
    for row in sector_weights.filter(pl.col("sector_weight") > 0.25).to_dicts():
        violations.append({
            "rule_name": "concentration_risk",
            "sector": row["sector"],
            "details": {"weight": round(row["sector_weight"], 4), "limit": 0.25},
        })
    return violations

def check_liquidity(enriched: pl.DataFrame) -> list[dict]:
    over_limit = enriched.filter(pl.col("market_value") > 1_000_000)
    return [
        {
            "rule_name": "liquidity_check",
            "ticker": row["ticker"],
            "details": {"market_value": row["market_value"], "limit": 1_000_000},
        }
        for row in over_limit.to_dicts()
    ]

def run_all_checks(enriched: pl.DataFrame) -> list[dict]:
    return check_concentration(enriched) + check_liquidity(enriched)