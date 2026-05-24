from __future__ import annotations
import pandas as pd
from .timeseries import TimeSeries


class Asset:
    
    REQUIRED_COLUMNS = {"close"}
    
    def __init__(self, ticker: str, data: pd.DataFrame):

        self._ticker = ticker

        self._validate(data=data)

        self._close= TimeSeries(data = data["close"], name = f"close_{ticker}")
        self._volume= TimeSeries(data = data["volume"], name = f"volume_{ticker}")

    def _validate(self, data: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLUMNS - set(data.columns)
        if missing:
            raise ValueError(f"the following columns are missing : {missing}")
        
        if not isinstance(data.index,pd.DatetimeIndex):
            raise TypeError("The DF index must be a DatetimeIndex")
        
        for col in self.REQUIRED_COLUMNS:
            if not pd.api.types.is_numeric_dtype(data[col]):
                raise TypeError(f"column {col} is not numeric")


    # ============================================================
    # BASE PROPERTIES
    # ============================================================
    @property 
    def ticker(self) -> str:
        return self._ticker
    
    @property 
    def close(self) -> "TimeSeries":
        return self._close

    @property
    def start_date(self) -> pd.Timestamp | None:
        return self._close.start_date

    @property
    def end_date(self) -> pd.Timestamp | None:
        return self._close.end_date

    @property
    def is_empty(self) -> bool:
        return self._close.is_empty
    


    # ============================================================
    # CALCULATED PROPERTIES
    # ============================================================

    @property
    def returns(self) -> TimeSeries:
        return self._close.returns

    @property
    def cumulative_returns(self) -> TimeSeries:
        return self._close.cumulative_returns

    @property
    def drawdown(self) -> TimeSeries:
        return self._close.drawdown

    @property
    def max_drawdown(self) -> float:
        return self._close.max_drawdown
    
    # ============================================================
    # PUBLIC METHODS 
    # ============================================================
    def first (self, period: int | str) -> Asset:
        """Gives the first n points or first period based on the given argument
        Args:
            period (int | str): first n elements (int) or first period (6M,1Y,...)
        Returns:
            Asset: an Asset with the corresponding filter
        """
        filtered_data = self._close.first(period)
        return self.between(str(filtered_data.start_date),str(filtered_data.end_date))
    
    def last (self, period: int | str) -> Asset:
        """Gives the last n points or filastrst period based on the given argument
        Args:
            period (int | str): last n elements (int) or last period (6M,1Y,...)
        Returns:
            Asset: an Asset with the corresponding filter
        """
        filtered_data = self._close.last(period)
        return self.between(str(filtered_data.start_date),str(filtered_data.end_date))
    

    def between(self, start: str, end: str) -> Asset:
        """ Transforms the asset class by filtering between the start and end date, just like in TimeSeries.between
        Args:
            start (str): start date
            end (str): end date
        Returns:
            Asset: The Asset class between the start and end date
        """

        df = self.to_dataframe().loc[start:end]

        return Asset(ticker = self._ticker,data = df)
        
    def to_dataframe(self) -> pd.DataFrame:
        """ Converts the Asset data to a dataframe
        Returns:
            pd.DataFrame: Asset data as a DataFrame
        """
        return pd.DataFrame({"open": self._open.data,})

    # ============================================================
    # DUNDER METHODS 
    # ============================================================
    def __repr__(self) -> str:
        return f"Asset(ticker={self._ticker}, start_date={self.start_date}, end_date={self.end_date})"

    def __len__(self) -> int:
        return len(self._close)

    # ============================================================
    # CLASS METHODS 
    # ============================================================

    @classmethod
    def from_csv(cls, ticker: str, path: str) -> Asset:
        """Create an Asset class from a CSV file.

        Args:
            ticker (str): asset ticker
            path (str): csv file path

        Returns:
            Asset: The corresponding asset class
        """
        data = pd.read_csv(path, index_col=0, parse_dates=True)
        return cls(ticker=ticker, data=data)