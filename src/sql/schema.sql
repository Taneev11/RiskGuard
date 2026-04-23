CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    avg_purchase_price NUMERIC(12, 4) NOT NULL,
    trade_type VARCHAR(4) CHECK (trade_type IN ('BUY', 'SELL')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE compliance_violations (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    ticker VARCHAR(10),
    sector VARCHAR(50),
    details JSONB,
    triggered_at TIMESTAMPTZ DEFAULT NOW()
);