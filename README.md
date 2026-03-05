# finances

Simple experiments and tools for stock market analysis.

## What is in this repo

- `src/stock_performance.py`: reusable script/CLI to fetch close prices, compute performance/risk metrics, and plot price history.
- `src/strategies.py`: strategy signals (`trend_following_signal`, `rsi_multi_timeframe_signal`).
- `stock_performance.ipynb`: notebook version of the same idea for interactive exploration.
- `tests/test_stock_performance.py`: unit tests for metrics and report export.
- `tests/test_strategies.py`: unit tests for multiple strategy signal generators.
- `docs/ROADMAP.md`: planned evolution by phase.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run with defaults (`AAPL,GOOG,TSLA`, last 365 days):

```bash
python -m src.stock_performance
```

By default this also saves reports under `reports/`:

- `summary_<timestamp>.csv`
- `close_prices_<timestamp>.csv`
- `chart_<timestamp>.html`

Custom example:

```bash
python -m src.stock_performance --tickers AAPL,MSFT,NVDA --days 180 --output-dir reports/custom
```

Custom output paths:

```bash
python -m src.stock_performance \
  --summary-path reports/summary.csv \
  --prices-path reports/prices.csv \
  --chart-path reports/chart.html
```

Disable auto export:

```bash
python -m src.stock_performance --no-export
```

## Metrics included

- current price
- average price
- variation (% vs average price)
- total return
- annualized volatility (252 trading days)
- max drawdown

## Run tests

```bash
pytest -q
```

## Notes

- Data source: `yfinance`
- This project is educational and not financial advice.

## Roadmap

- See [docs/ROADMAP.md](docs/ROADMAP.md)
