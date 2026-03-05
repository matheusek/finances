"""Trading strategy signal generators.

Each strategy is isolated as a dedicated function for easier testing and extension.
Signals use:
    1  -> long
    0  -> neutral
   -1  -> short
"""

from __future__ import annotations

import pandas as pd


def calculate_rsi(close_prices: pd.Series, window: int = 14) -> pd.Series:
    if window <= 0:
        raise ValueError("window must be > 0")

    delta = close_prices.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)

    avg_gain = gains.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def trend_following_signal(
    close_prices: pd.Series,
    short_window: int = 20,
    long_window: int = 50,
) -> pd.Series:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("short_window and long_window must be > 0")
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")

    short_ma = close_prices.rolling(window=short_window, min_periods=short_window).mean()
    long_ma = close_prices.rolling(window=long_window, min_periods=long_window).mean()

    signal = pd.Series(0, index=close_prices.index, dtype="int64")
    signal[short_ma > long_ma] = 1
    signal[short_ma < long_ma] = -1
    return signal


def rsi_multi_timeframe_signal(
    close_prices: pd.Series,
    rsi_window: int = 14,
    higher_timeframe: str = "W",
    lower_threshold: float = 30.0,
    upper_threshold: float = 70.0,
) -> pd.Series:
    if not isinstance(close_prices.index, pd.DatetimeIndex):
        raise ValueError("rsi_multi_timeframe_signal requires a DatetimeIndex.")
    if lower_threshold >= upper_threshold:
        raise ValueError("lower_threshold must be smaller than upper_threshold")

    lower_rsi = calculate_rsi(close_prices, window=rsi_window)
    higher_close = close_prices.resample(higher_timeframe).last().dropna()
    higher_rsi = calculate_rsi(higher_close, window=rsi_window).reindex(
        close_prices.index, method="ffill"
    )

    signal = pd.Series(0, index=close_prices.index, dtype="int64")
    signal[(lower_rsi < lower_threshold) & (higher_rsi > 50)] = 1
    signal[(lower_rsi > upper_threshold) & (higher_rsi < 50)] = -1
    return signal
