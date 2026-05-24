from __future__ import annotations
import numpy as np
from core.timeseries import TimeSeries


def volatility(time_series: TimeSeries, window: int | None = None, timespan : int | None = None) -> float:
    """Computes the volatility of a TimeSeries.
    Args:
        ts (TimeSeries): The time series data.
        window (int | None, optional): The window size for volatility calculation. Defaults to None.
        timespan (int | None, optional): The timespan for annualizing volatility. Defaults to None.
    Returns:
        float: The volatility value.
    """
    returns = time_series.returns
    if window:
        returns = returns.last(window)

    if returns.is_empty or len(returns) < 2:
        return 0.0
    
    vol = returns.data.std()
    if timespan:
        vol *= np.sqrt(timespan)
    return vol


def sharpe_ratio(time_series: TimeSeries, risk_free: float = 0.0) -> float:
    """ Computes the Sharpe Ratio of a TimeSeries.
    Args:
        time_series (TimeSeries): The time series data.
        risk_free (float, optional): The risk-free rate. Defaults to 0.0.
    Returns:
        float: The Sharpe Ratio.
    """
    avg_return = time_series.returns.data.mean() * 252
    vol = volatility(time_series, timespan=252)
    if vol == 0:
        return 0
    return (avg_return - risk_free) / vol


def momentum(time_series: TimeSeries, window: int = 252) -> float:
    """Computes the return of a TimeSeries over a given window.
    Args:
        time_series (TimeSeries): The time series data.
        window (int, optional): The window size for momentum calculation. Defaults to 252.
    Returns:
        float: The momentum value.
    """
    filtered_ts = time_series.last(window) 
    if filtered_ts.is_empty: 
        return 0.0
    
    start_price = filtered_ts.data.iloc[0] 
    end_price = filtered_ts.data.iloc[-1]

    if start_price == 0:
        return 0.0
    
    momentum_value = (end_price - start_price) / start_price

    return momentum_value

def sortino_ratio(time_series: TimeSeries, risk_free: float = 0.0) -> float:
    """ Computes the Sortino Ratio of a TimeSeries.
    Args:
        time_series (TimeSeries): The time series data.
        risk_free (float, optional): The risk-free rate. Defaults to 0.0.
    Returns:
        float: The Sortino Ratio.
    """

    returns = time_series.returns.data
    neg_returns = returns[returns < 0]

    if len(neg_returns) < 2:
        return 0.0
    
    downside_vol = volatility(time_series = TimeSeries(neg_returns),timespan = 252)
    avg_return = returns.mean() * 252

    return (avg_return - risk_free) / downside_vol if downside_vol != 0 else 0.0


def calmar_ratio(time_series: TimeSeries) -> float:
    """ Computes the Calmar Ratio of a TimeSeries.
    Args:
        time_series (TimeSeries): The time series data.
        window (int, optional): The window size for maximum drawdown calculation. Defaults to 252.
    Returns:
        float: The Calmar Ratio.
    """
    avg_return = time_series.returns.data.mean() * 252
    mdd = time_series.max_drawdown

    return avg_return / abs(mdd) if mdd != 0 else 0.0

def var(time_series: TimeSeries, alpha: float = 0.95) -> float:
    """ Computes the Value at Risk (VaR) of a TimeSeries at a given confidence level.

    Args:
        time_series (TimeSeries): The time series data.
        alpha (float, optional): The confidence level for VaR calculation. Defaults to 0.95.

    Returns:
        float: The Value at Risk (VaR) value.
    """
    returns = time_series.returns.data

    if len (returns) < 2:
        return 0.0
    
    return np.percentile(returns, (1 - alpha) / 100)

def cvar(time_series: TimeSeries, alpha: float = 0.95) -> float:

    returns = time_series.returns.data

    if len (returns) < 2:
        return 0.0
    
    var_threshold = var(time_series, alpha)
    cvar_value = returns[returns <= var_threshold].mean()

    if len(cvar_value) == 0:
        return 0.0
    
    return cvar_value

def beta(ts: TimeSeries, benchmark: TimeSeries) -> float:
    """ Computes the Beta of a TimeSeries relative to a benchmark TimeSeries.
    Args:
        ts (TimeSeries): The time series data.
        benchmark (TimeSeries): The benchmark time series data.
    Returns:
        float: The Beta value.
    """
    ts_aligned, bench_aligned = ts.returns.align_with(benchmark.returns, how="inner")
    
    ts_returns = ts_aligned.data
    bench_returns = bench_aligned.data
    
    if len(ts_returns) < 2 or len(bench_returns) < 2:
        return 0.0
    
    covariance = np.cov(ts_returns, bench_returns)[0][1]
    benchmark_var = np.var(bench_returns)
    
    return covariance / benchmark_var if benchmark_var != 0 else 0.0


def alpha(ts: TimeSeries, benchmark: TimeSeries, risk_free: float = 0.0) -> float:
    """Computes the Alpha of a TimeSeries relative to a benchmark TimeSeries.
    Args:
        ts (TimeSeries): The time series data.
        benchmark (TimeSeries): The benchmark time series data.
        risk_free (float, optional): The risk-free rate. Defaults to 0.0.
    Returns:
        float: The Alpha value.
    """
    beta_market = beta(ts=ts,benchmark = benchmark)
    returns_market = benchmark.returns.data.mean() * 252
    returns_ts = ts.returns.data.mean() * 252
    
    return returns_ts - (risk_free + beta_market * (returns_market - risk_free))

def information_ratio(ts: TimeSeries, benchmark: TimeSeries) -> float:
    """Computes the Information Ratio of a TimeSeries relative to a benchmark TimeSeries with the following formula : (R_portfolio - R_benchmark) / Tracking Error
    
    Args:
        ts (TimeSeries): The time series data.
        benchmark (TimeSeries): The benchmark time series data.
    Returns:
        float: The Information Ratio value.
    """
    
    ts_returns, benchmark_returns = ts.returns.align_with(benchmark.returns, how="inner")

    if len(ts_returns) < 2:
        return 0.0
    
    excess_returns = ts_returns.data - benchmark_returns.data
    tracking_error = excess_returns.std() * np.sqrt(252)
    return excess_returns.mean() / tracking_error if tracking_error != 0 else 0.0