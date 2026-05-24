from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
from core.universe import Universe
import analytics.metrics as metrics

class WeightingScheme(ABC):
    """Abstract base class for weighting schemes."""
    
    @abstractmethod
    def compute_weights(self, universe: Universe, date: str) -> dict[str, float]:
        """Computes weights for the given universe at the specified date.
        Args:
            universe (Universe): The universe of assets.
            date (str): The date for which to compute weights
        Returns:
            dict[str, float]: A dictionary mapping asset symbols to their weights.
        """
        pass

class EqualWeight(WeightingScheme):
    """Class implementing equal weighting scheme.

    Args:
        WeightingScheme (abstract class): The base class for weighting schemes.
    """
    def compute_weights(self,universe: Universe, date: str) -> dict[str,float]:
        n = len(universe)
        if n == 0:
            return {}
        weight = 1/n
        return {symbol: weight for symbol in universe.symbols}
    
class EqualRiskContribution(WeightingScheme):
    """ Implements a basic ERC weighting scheme based on the following formula:
        **weight_i = (1 / volatility_i) / sum(1 / volatility_j for all j)**
    Args:
        WeightingScheme (abstract class): The base class for weighting schemes.
    """
    def __init__(self, lookback: int = 60):
        self._lookback = lookback
    
    def compute_weights(self, universe: Universe, date: str) -> dict[str, float]:
        """ Computes ERC weights for the given universe at the specified date. The weights are inversely proportional to the asset volatilities over the lookback period.
        Args:
            universe (Universe): given universe.
            date (str): date from which you calculate lookback.
        Returns:
            dict[str, float]: A dictionary with the symbol matched with the acorrespinding weight
        """
        if len(universe) == 0:
            return {}
        
        volatilities = dict()
        for asset in universe:
            asset_date_filtered = asset.between(start=str(asset.start_date), end=date)
            vol = metrics.volatility(ts=asset_date_filtered.close, window=self._lookback, timespan=252)
            volatilities[asset.symbol] = vol
        
        inv_vols = dict()
        for symbol, vol in volatilities.items():
            inv_vols[symbol] = 1 / vol if vol > 0 else 0.0
        
        total = sum(inv_vols.values())
        if total == 0:
            return {symbol: 0.0 for symbol in universe.symbols}
        
        return {symbol: inv_vol / total for symbol, inv_vol in inv_vols.items()}
        
    class MomentumWeight(WeightingScheme):
        """ Implements a momentum-based weighting scheme based on the following formula:
            weight_i = momentum_i / sum(momentum_j for all j)
        Args:
            WeightingScheme (abstract class): The base class for weighting schemes.
        """
        def __init__(self, lookback: int = 252):
            self._lookback = lookback
        
        def compute_weights(self, universe: Universe, date: str) -> dict[str, float]:
            momentums = dict()
            for asset in universe:
                asset_date_filtered = asset.between(start= str(asset.start_date),end=date)
                momentum = metrics.momentum(asset_date_filtered.close,window=self._lookback)
                momentums[asset.symbol] = momentum

            total = sum(list(map(abs,momentums.values())))
            if total == 0:
                return {symbol: 0.0 for symbol in universe.symbols}
            
            return {symbol : curr_mom / total for symbol, curr_mom in momentums.items()}

