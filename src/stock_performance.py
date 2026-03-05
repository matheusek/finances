"""Stock performance analysis with yfinance + Plotly.

This module can be imported or run as a CLI:
    python -m src.stock_performance --tickers AAPL,GOOG,TSLA --days 365
"""

from __future__ import annotations

import argparse
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf


DEFAULT_TICKERS = ("AAPL", "GOOG", "TSLA")
TRADING_DAYS_PER_YEAR = 252


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
    close_prices = close_prices.dropna(axis=1, how="all")
    if close_prices.empty:
        raise ValueError("No non-empty close prices found after cleaning.")

    return close_prices


def summarize_performance(close_prices: pd.DataFrame) -> pd.DataFrame:
    normalized_prices = close_prices.ffill().dropna(how="all")
    if normalized_prices.empty:
        raise ValueError("Cannot summarize empty close prices.")

    first_price = normalized_prices.bfill().iloc[0]
    mean_price = normalized_prices.mean()
    current_price = normalized_prices.iloc[-1]
    variation = (current_price - mean_price) / mean_price
    total_return = (current_price / first_price) - 1.0

    daily_returns = normalized_prices.pct_change().dropna(how="all")
    if daily_returns.empty:
        annualized_volatility = pd.Series(0.0, index=normalized_prices.columns)
    else:
        annualized_volatility = (
            daily_returns.std().fillna(0.0) * math.sqrt(TRADING_DAYS_PER_YEAR)
        )

    drawdown = normalized_prices.divide(normalized_prices.cummax()) - 1.0
    max_drawdown = drawdown.min().fillna(0.0)

    summary = pd.DataFrame(
        {
            "Stock": normalized_prices.columns,
            "Current Price": current_price.values,
            "Average Price": mean_price.values,
            "Variation": variation.values,
            "Total Return": total_return.values,
            "Annualized Volatility": annualized_volatility.values,
            "Max Drawdown": max_drawdown.values,
        }
    )
    summary["Variation %"] = summary["Variation"] * 100
    summary["Total Return %"] = summary["Total Return"] * 100
    summary["Annualized Volatility %"] = summary["Annualized Volatility"] * 100
    summary["Max Drawdown %"] = summary["Max Drawdown"] * 100
    return summary.sort_values("Total Return", ascending=False).reset_index(drop=True)


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


def export_reports(
    summary: pd.DataFrame,
    close_prices: pd.DataFrame,
    figure: go.Figure,
    output_dir: str,
    summary_path: str = "",
    prices_path: str = "",
    chart_path: str = "",
    run_id: str = "",
) -> dict[str, Path]:
    export_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    resolved_summary_path = Path(summary_path) if summary_path else base_dir / f"summary_{export_id}.csv"
    resolved_prices_path = Path(prices_path) if prices_path else base_dir / f"close_prices_{export_id}.csv"
    resolved_chart_path = Path(chart_path) if chart_path else base_dir / f"chart_{export_id}.html"

    summary.to_csv(resolved_summary_path, index=False)
    close_prices.to_csv(resolved_prices_path)
    figure.write_html(resolved_chart_path, include_plotlyjs="cdn")

    return {
        "summary": resolved_summary_path,
        "prices": resolved_prices_path,
        "chart": resolved_chart_path,
    }


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
        help="Legacy alias for summary CSV output path.",
    )
    parser.add_argument(
        "--summary-path",
        default="",
        help="Optional CSV output path for summary metrics.",
    )
    parser.add_argument(
        "--prices-path",
        default="",
        help="Optional CSV output path for close prices history.",
    )
    parser.add_argument(
        "--chart-path",
        default="",
        help="Optional HTML output path for the interactive chart.",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory used for automatic exports (default: reports).",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Disable automatic export of CSV/HTML reports.",
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
    figure = build_price_chart(close_prices)

    display_cols = [
        "Stock",
        "Current Price",
        "Average Price",
        "Variation %",
        "Total Return %",
        "Annualized Volatility %",
        "Max Drawdown %",
    ]
    print(summary[display_cols].to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    if not args.no_export:
        exports = export_reports(
            summary=summary,
            close_prices=close_prices,
            figure=figure,
            output_dir=args.output_dir,
            summary_path=args.summary_path or args.save_summary,
            prices_path=args.prices_path,
            chart_path=args.chart_path,
        )
        print(f"\nSummary saved to: {exports['summary']}")
        print(f"Close prices saved to: {exports['prices']}")
        print(f"Chart saved to: {exports['chart']}")
    elif args.save_summary:
        summary.to_csv(args.save_summary, index=False)
        print(f"\nSummary saved to: {args.save_summary}")

    if not args.no_plot:
        figure.show()


if __name__ == "__main__":
    main()
