CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS trades (
    time           TIMESTAMPTZ       NOT NULL,
    symbol         TEXT              NOT NULL,
    trade_id       BIGINT            NOT NULL,
    price          DOUBLE PRECISION  NOT NULL,
    quantity       DOUBLE PRECISION  NOT NULL,
    is_buyer_maker BOOLEAN           NOT NULL,
    PRIMARY KEY (symbol, trade_id, time)
);

SELECT create_hypertable(
    'trades', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists       => TRUE
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol_time
    ON trades (symbol, time DESC);