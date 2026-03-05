import numpy as np
import pandas as pd
import pytest

from src.strategies import (
    calculate_rsi,
    rsi_multi_timeframe_signal,
    trend_following_signal,
)


def test_trend_following_signal_turns_long_on_uptrend() -> None:
    index = pd.date_range("2024-01-01", periods=120, freq="D")
    prices = pd.Series(np.linspace(100, 220, num=120), index=index)

    signals = trend_following_signal(prices, short_window=20, long_window=50)

    assert signals.iloc[-1] == 1
    assert set(signals.unique()).issubset({-1, 0, 1})


def test_trend_following_signal_turns_short_on_downtrend() -> None:
    index = pd.date_range("2024-01-01", periods=120, freq="D")
    prices = pd.Series(np.linspace(220, 100, num=120), index=index)

    signals = trend_following_signal(prices, short_window=20, long_window=50)

    assert signals.iloc[-1] == -1


def test_calculate_rsi_stays_in_valid_range() -> None:
    index = pd.date_range("2024-01-01", periods=80, freq="D")
    prices = pd.Series(np.linspace(100, 150, num=80), index=index)

    rsi = calculate_rsi(prices, window=14)

    assert ((rsi >= 0) & (rsi <= 100)).all()


def test_rsi_multi_timeframe_signal_returns_discrete_values() -> None:
    index = pd.date_range("2024-01-01", periods=220, freq="D")

    # Uptrend followed by local pullback to create oversold moments in lower timeframe.
    uptrend = np.linspace(100, 200, num=180)
    pullback = np.array([198, 194, 188, 183, 179, 176, 178, 181, 185, 190, 194, 198, 201, 205, 208, 210, 212, 214, 216, 218, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239])
    prices = pd.Series(np.concatenate([uptrend, pullback]), index=index)

    signals = rsi_multi_timeframe_signal(prices, rsi_window=14, higher_timeframe="W")

    assert set(signals.unique()).issubset({-1, 0, 1})
    assert (signals == 1).any()


def test_rsi_multi_timeframe_requires_datetime_index() -> None:
    prices = pd.Series([100, 101, 99, 102, 103])

    with pytest.raises(ValueError):
        rsi_multi_timeframe_signal(prices)
