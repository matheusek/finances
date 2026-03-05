"""Stock performance analysis with yfinance + Plotly.

This module can be imported or run as a CLI:
    python -m src.stock_performance --tickers AAPL,GOOG,TSLA --days 365
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf


DEFAULT_TICKERS = ("AAPL", "GOOG", "TSLA")


def parse_tickers(raw_tickers: str) -> list[str]:
    tickers = []
    for ticker in raw_tickers.split(","):
        clean = ticker.strip().upper()
        if clean and clean not in tickers:
            tickers.append(clean)
    if not tickers:
        raise ValueError("At least one ticker is required.")
    return tickers


def download_close_prices(
    tickers: Iterable[str], start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    tickers = list(tickers)
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=False,
    )

    if data.empty:
        raise ValueError("No data returned from yfinance for the provided inputs.")

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" not in data.columns.get_level_values(0):
            raise ValueError("Expected 'Close' prices in yfinance response.")
        close_prices = data["Close"].copy()
    else:
        if "Close" not in data.columns:
            raise ValueError("Expected 'Close' prices in yfinance response.")
        close_prices = data[["Close"]].copy()
        close_prices.columns = [tickers[0]]

    close_prices = close_prices.dropna(how="all")
    if close_prices.empty:
        raise ValueError("No non-empty close prices found after cleaning.")

    return close_prices


def summarize_performance(close_prices: pd.DataFrame) -> pd.DataFrame:
    mean_price = close_prices.mean()
    current_price = close_prices.ffill().iloc[-1]
    variation = (current_price - mean_price) / mean_price

    summary = pd.DataFrame(
        {
            "Stock": close_prices.columns,
            "Current Price": current_price.values,
            "Average Price": mean_price.values,
            "Variation": variation.values,
        }
    )
    summary["Variation %"] = summary["Variation"] * 100
    return summary.sort_values("Variation", ascending=False).reset_index(drop=True)


def build_price_chart(close_prices: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for ticker in close_prices.columns:
        fig.add_trace(
            go.Scatter(
                x=close_prices.index,
                y=close_prices[ticker],
                mode="lines",
                name=ticker,
            )
        )

    fig.update_layout(
        title="Stock Price History",
        xaxis_title="Date",
        yaxis_title="Close Price",
        template="plotly_white",
    )
    return fig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze stock performance over a date window.")
    parser.add_argument(
        "--tickers",
        default=",".join(DEFAULT_TICKERS),
        help="Comma-separated stock tickers (default: AAPL,GOOG,TSLA).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="How many days back from today to fetch prices (default: 365).",
    )
    parser.add_argument(
        "--save-summary",
        default="",
        help="Optional CSV output path for the summary table.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip interactive Plotly chart display.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tickers = parse_tickers(args.tickers)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=args.days)

    close_prices = download_close_prices(tickers, start_date, end_date)
    summary = summarize_performance(close_prices)

    display_cols = ["Stock", "Current Price", "Average Price", "Variation %"]
    print(summary[display_cols].to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    if args.save_summary:
        summary.to_csv(args.save_summary, index=False)
        print(f"\nSummary saved to: {args.save_summary}")

    if not args.no_plot:
        build_price_chart(close_prices).show()


if __name__ == "__main__":
    main()
