from __future__ import annotations
import pandas as pd
from .asset import Asset
from .timeseries import TimeSeries


class Universe:

    def __init__(self, assets: list[Asset] | None = None):
        if assets is None:
            self._assets = {}
            return
        
        if not isinstance(assets, list):
            raise TypeError("assets must be a list of Asset")
        
        for asset in assets:
            if not isinstance(asset,Asset):
                raise TypeError(f"assets must be of type Asset, got {type(asset)}")
        
 
        if not len(assets) == len({asset.ticker for asset in assets}):
            raise ValueError("Duplicate asset tickers found in the assets list")
        
        self._assets = {asset.ticker : asset for asset in assets}


    # ============================================================
    # BASE PROPERTIES
    # ============================================================

    @property
    def tickers(self) -> list[str]:
        return list(self._assets.keys())

    @property
    def assets(self) -> dict[str, Asset]:
        return self._assets.copy()

    @property
    def is_empty(self) -> bool:
       return len(self._assets) == 0
    

    # ============================================================
    # CALCULATED PROPERTIES
    # ============================================================
    @property
    def start_date(self) -> pd.Timestamp | None:
        if self.is_empty:
            return None
        return max(asset.start_date for asset in self._assets.values())

    @property
    def end_date(self) -> pd.Timestamp | None:
        if self.is_empty:
            return None
        
        return min(asset.end_date for asset in self._assets.values())
    

    # ============================================================
    # PUBLIC METHODS 
    # ============================================================

    def get(self, ticker: str) -> Asset:

        if not(ticker in self._assets):
            raise KeyError("ticker not found in asset list")
        return self._assets[ticker]

    def add(self, asset: Asset) -> None:

        if not(asset.ticker in self._assets):
            self._assets[asset.ticker] = asset
        else:
            raise KeyError(f"Asset '{asset.ticker}' already exists")


    def remove(self, ticker: str) -> None:
        if  not(ticker in self._assets):  
            raise KeyError(f"Asset '{ticker}' not found")
        del self._assets[ticker]

    def between(self, start: str, end: str) -> Universe:
        """Filter all assets between two dates.
        Args:
            start (str): start date
            end (str): end date
        Returns:
            Universe: A new Universe with all assets filtered between start and end
        """
        filtered_assets = [asset.between(start, end) for asset in self._assets.values()]
        return Universe(assets=filtered_assets)


    def align(self) -> Universe:
        """ Align all assets in the universe to have the same date range.
        Returns:
            Universe: A new Universe with all assets aligned to the same date range.
        """
        return self.between(str(self.start_date), str(self.end_date))

    def to_dataframe(self, elem: str = "close") -> pd.DataFrame:
        """Export one field for all assets as DataFrame (columns = tickers).
        Args:
            elem (str): The element to export (open, high, low, close, volume)
        Returns:
            pd.DataFrame: DataFrame with dates as index and tickers as columns
        """
        valid_elems = {"open", "high", "low", "close", "volume"}
        if elem not in valid_elems:
            raise ValueError(f"elem must be one of {valid_elems}, got '{elem}'")

        if self.is_empty:
            return pd.DataFrame()

        data = {ticker: getattr(asset, elem).data for ticker, asset in self._assets.items()}
        return pd.DataFrame(data)

    def returns_df(self) -> pd.DataFrame:
        """DataFrame of returns for all assets.
        Returns:
            pd.DataFrame: DataFrame with dates as index and tickers as columns
        """
        if self.is_empty:
            return pd.DataFrame()
        data = {ticker: asset.returns.data for ticker, asset in self._assets.items()}
        return pd.DataFrame(data)

    # ============================================================
    # DUNDER METHODS 
    # ============================================================

    def __getitem__(self, ticker: str) -> Asset:
        return self.get(ticker)
    
    def __iter__(self):
        return iter(self._assets.values())

    def __len__(self) -> int:
        return len(self._assets)

    def __contains__(self, ticker: str) -> bool:
        return ticker in self._assets

    def __repr__(self) -> str:
        return f"Universe(assets={list(self._assets.keys())})"