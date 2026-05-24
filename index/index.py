from __future__ import annotations
import pandas as pd
from core.timeseries import TimeSeries
from index.rebalance import RebalanceSchedule
from index.weighting import WeightingScheme
from simulation.costs import MarketImpactCostModel
from core.universe import Universe
from analytics.metrics import volatility


class Index:
    def __init__(self,universe: Universe, weighting_scheme : WeightingScheme, rebalance_schedule: RebalanceSchedule, cost_model: MarketImpactCostModel | None = None, name : str | None = None):
        self._universe = universe
        self._weighting_scheme = weighting_scheme
        self._rebalance_schedule = rebalance_schedule
        self._cost_model = cost_model   
        self._name = name
        self._nav = None
        self._weights_history = dict()



    def compute(self, start: str, end: str) -> None:
        """ Computes the index NAV between start and end dates, following this method :
            - For each date in the returns dataframe of the universe :
                - If the date is a rebalance date, compute new weights with the weighting scheme, apply costs and update weights history
                - Update NAV based on the returns of the current weights
            - Store the NAV as a TimeSeries object
            thats it

        Args:
            start (str): Start date.
            end (str): start date
        Returns:
            None because nav is simply stored in self._nav
        """
        rebalance_dates = set(self._rebalance_schedule.get_rebalance_dates(start, end))
        returns_df = self._universe.between(start, end).returns_df()
        
        nav = 100.0
        weights = {}
        self._weights_history = {}
        nav_history = {}
        
        for date, row in returns_df.iterrows():
            date_str = str(date.date())
            
            if date_str in rebalance_dates:
                new_weights = self._weighting_scheme.compute_weights(self._universe, date_str)
                nav *= (1 - self._get_cost_pct(weights, new_weights, nav, date_str))
                weights = new_weights
                self._weights_history[date] = weights
            
            if weights:
                nav *= 1 + sum(weights.get(c, 0) * row[c] for c in row.index)
                nav_history[date] = nav
        
        self._nav = TimeSeries(pd.Series(nav_history), name=self._name)


    def _get_cost_pct(self, old: dict, new: dict, nav: float, date: str) -> float:
        """Calcule le coût total en % de la NAV, asset par asset."""
        if not self._cost_model or not old:
            return 0.0

        total_cost = 0.0

        for symbol in set(old) | set(new):
            delta = abs(new.get(symbol, 0) - old.get(symbol, 0))
            if delta == 0:
                continue

            quantity = delta * nav
            asset = self._universe.get(symbol)

            asset_filtered = asset.between(str(asset.start_date), date)
            vol = volatility(asset_filtered.close.last(60), timespan=1)

            vol_data = asset_filtered.volume.last(20).data
            volume = vol_data.mean() if len(vol_data) > 0 else nav * 10

            if vol == 0:
                vol = 0.01
            if volume == 0:
                volume = nav * 10

            cost = self._cost_model.total_cost_pct(vol, quantity, volume)
            total_cost += cost * quantity

        return total_cost / nav if nav > 0 else 0.0
    


    @property
    def returns(self) -> TimeSeries | None:
        if not self.is_computed:
            return None
        return self._nav.returns
    
    @property
    def cumulative_returns(self) -> TimeSeries | None:
        if not self.is_computed:
            return None
        return self._nav.cumulative_returns
    
    @property
    def drawdown(self) -> TimeSeries | None:
        if not self.is_computed:
            return None
        return self._nav.drawdown
    
    @property
    def max_drawdown(self) -> float | None:
        if not self.is_computed:
            return None
        return self._nav.max_drawdown
    
    @property
    def name(self) -> str | None:
        return self._name

    @property
    def universe(self) -> Universe:
        return self._universe

    @property
    def weighting_scheme(self) -> WeightingScheme:
        return self._weighting_scheme

    @property
    def rebalance_schedule(self) -> RebalanceSchedule:
        return self._rebalance_schedule

    @property
    def nav(self) -> TimeSeries | None:
        return self._nav

    @property
    def weights_history(self) -> dict[str, dict[str, float]] | None:
        return self._weights_history

    @property
    def is_computed(self) -> bool:
        return self._nav is not None