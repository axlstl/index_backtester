from __future__ import annotations
import numpy as np

class MarketImpactCostModel:
    """I tried to implement the Almgren-Chriss square-root market impact model, based on the course of Fabrizio Lillio from Scuola Normale Superiore, course found online as :
    "Market Impact models and optimal execution algorithms", i also used other sources online
    """
    
    def __init__(
        self,
        commission: float = 0.001,
        spread: float = 0.0005,
        slippage: float = 0.0002,
        impact_factor: float = 0.1
    ):
        """
        Args:
            commission: Fixed commission per trade (%). Ex: 0.001 = 0.1%
            spread: Bid-ask spread (%). Ex: 0.0005 = 0.05%
            slippage: Execution slippage (%). Ex: 0.0002 = 0.02%
            impact_factor: Market impact constant k (typically 0.1 to 0.5)
        """
        self._commission = commission
        self._spread = spread
        self._slippage = slippage
        self._impact_factor = impact_factor
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def commission(self) -> float:
        return self._commission
    
    @property
    def spread(self) -> float:
        return self._spread
    
    @property
    def slippage(self) -> float:
        return self._slippage
    
    @property
    def impact_factor(self) -> float:
        return self._impact_factor
    
    # ============================================================
    # COST CALCULATION METHODS
    # ============================================================
    
    def fixed_cost_pct(self) -> float:
        """Returns fixed costs as percentage.
        
        Fixed costs = commission + spread/2 + slippage
        """
        return self._commission + (self._spread / 2) + self._slippage
    
    def market_impact_pct(self, volatility: float, quantity: float, volume: float) -> float:
        """Calculates market impact cost as percentage, following the formula:
            Market Impact = impact_factor * volatility * sqrt(quantity / volume)

        Args:
            volatility (float): The daily volatility of the asset.
            quantity (float): Quantity traded in value.
            volume (float):  Average daily volume in value.

        Returns:
            float: Market impact cost as percentage.
        """
        return self._impact_factor * volatility * np.sqrt(quantity / volume)
    
    def total_cost_pct(self, volatility: float, quantity: float, volume: float) -> float:
        """ Computes total cost as percentage.

        Args:
            volatility (float): The daily volatility of the asset.
            quantity (float): Quantity traded in value.
            volume (float):  Average daily volume in value. 

        Returns:
            float: Total cost as percentage.
        """
        return self.fixed_cost_pct() + self.market_impact_pct(volatility, quantity, volume)

    
    def apply_to_trade(self, price: float, side: str, volatility: float, quantity: float, volume: float) -> float:
        """ Computes the effective price after applying transaction costs. Adds costs for buy trades and subtracts costs for sell trades.

        args:
            price (float): Current market price.
            side (str): 'buy' or 'sell'.
            volatility (float): The daily volatility of the asset.
            quantity (float): Quantity traded in value.
            volume (float):  Average daily volume in value.
        Returns:
            float: Effective execution price.
        """
        if side not in ["buy","sell"]:
            raise ValueError('side must be either "buy" or "sell"')
 
        if side == "buy":
            return price * (1 + self.total_cost_pct(volatility=volatility,quantity=quantity,volume=volume))
        else:
            return price * (1 - self.total_cost_pct(volatility=volatility,quantity=quantity,volume=volume))
    