# Roadmap

## Phase 1: Core Analytics (current)

Goal: make the stock analysis flow reliable and easy to reuse.

- benchmark comparison in CLI output
- better handling for missing ticker data
- clearer export naming and metadata
- improve notebook to mirror the Python module

## Phase 2: Portfolio Analytics

Goal: analyze a multi-asset portfolio instead of isolated tickers.

- weighted portfolio return
- weighted volatility and drawdown
- allocation input via CLI and CSV
- portfolio summary export

## Phase 3: Backtesting

Goal: evaluate simple strategies with reproducible results.

- basic backtest engine
- first strategy template (moving-average crossover)
- transaction cost and slippage parameters
- performance report (return, Sharpe, drawdown)

## Phase 4: Automation and Quality

Goal: improve maintainability and delivery speed.

- GitHub Actions for tests on push/PR
- code style tooling and checks
- more unit tests for edge cases
- release notes and version tags
