# finances

Simple experiments and tools for stock market analysis.

## What is in this repo

- `src/stock_performance.py`: reusable script/CLI to fetch close prices, compute variation, and plot price history.
- `stock_performance.ipynb`: notebook version of the same idea for interactive exploration.

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

Custom example:

```bash
python -m src.stock_performance --tickers AAPL,MSFT,NVDA --days 180 --save-summary summary.csv
```

## Notes

- Data source: `yfinance`
- This project is educational and not financial advice.
