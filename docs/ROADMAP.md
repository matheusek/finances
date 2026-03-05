# Roadmap

## Product positioning

`finances` is an open-source quant playground focused on:

- practical market analysis
- strategy research and backtesting
- clear visual storytelling for public viewers and contributors

## Target audiences

- solo builder: wants fast iteration and simple reproducibility
- quant/python developer: wants strategy modules and reliable metrics
- data/AI contributor: wants clean data/model experimentation surfaces
- public visitor: wants clear charts, demo artifacts, and understandable outcomes

## Team model (1 to 4 developers)

- 1 dev: sequential execution by phase
- 2 devs: split into `analytics/backtesting` and `visualization/docs`
- 3-4 devs: split into 4 tracks:
  - track A: data + metrics
  - track B: backtesting + strategies
  - track C: visualization + report UX
  - track D: AI + automation + contributor workflow

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

## Phase 5: Visualization and AI

Goal: make outputs compelling for public viewers while adding intelligence for deeper interpretation.

- interactive strategy dashboard
- strategy comparison matrix
- candlestick trade replay
- baseline regime model
- AI-generated narrative summaries
