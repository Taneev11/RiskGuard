from pydantic import BaseModel
from typing import Optional

class PortfolioRow(BaseModel):
    ticker: str
    quantity: int
    avg_purchase_price: float
    trade_type: str = "BUY"

class PortfolioUpload(BaseModel):
    holdings: list[PortfolioRow]

class ViolationOut(BaseModel):
    rule_name: str
    ticker: Optional[str] = None
    sector: Optional[str] = None
    details: dict

class RiskReport(BaseModel):
    total_value: float
    volatility_by_ticker: dict
    sector_weights: dict
    violations: list[ViolationOut]