from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.stock_performance import export_reports, parse_tickers, summarize_performance


def sample_close_prices() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=3, freq="D")
    return pd.DataFrame(
        {
            "AAA": [100.0, 110.0, 120.0],
            "BBB": [100.0, 80.0, 90.0],
        },
        index=index,
    )


def test_parse_tickers_normalizes_and_deduplicates() -> None:
    assert parse_tickers(" aapl, GOOG, aapl , tsla ") == ["AAPL", "GOOG", "TSLA"]


def test_summarize_performance_has_expected_metrics() -> None:
    summary = summarize_performance(sample_close_prices()).set_index("Stock")

    assert "Total Return %" in summary.columns
    assert "Annualized Volatility %" in summary.columns
    assert "Max Drawdown %" in summary.columns

    assert summary.loc["AAA", "Total Return %"] == pytest.approx(20.0, abs=1e-9)
    assert summary.loc["AAA", "Max Drawdown %"] == pytest.approx(0.0, abs=1e-9)
    assert summary.loc["BBB", "Max Drawdown %"] == pytest.approx(-20.0, abs=1e-9)
    assert summary.loc["AAA", "Annualized Volatility %"] > 0.0


def test_export_reports_writes_csv_and_html(tmp_path: Path) -> None:
    close_prices = sample_close_prices()
    summary = summarize_performance(close_prices)
    figure = go.Figure()

    paths = export_reports(
        summary=summary,
        close_prices=close_prices,
        figure=figure,
        output_dir=str(tmp_path),
        run_id="testrun",
    )

    assert paths["summary"].exists()
    assert paths["prices"].exists()
    assert paths["chart"].exists()

    assert paths["summary"].name == "summary_testrun.csv"
    assert paths["prices"].name == "close_prices_testrun.csv"
    assert paths["chart"].name == "chart_testrun.html"
