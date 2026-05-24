from __future__ import annotations
import pandas as pd
import numpy as np


class TimeSeries:

    # ============================================================
    # CLASS BUILDER
    # ============================================================
    def __init__(self,data : pd.Series,name:str | None = None):
        
        if not isinstance(data,pd.Series):
            raise TypeError("Data type must be a pandas Series")
        
        self._data = data.copy()
        self._name = name
        self._validate()


    # ============================================================
    # PRIVATE METHODS
    # ============================================================
    def _validate(self):
        """Checks if the data fits the expected format

        Raises:

            TypeError: If index type is not DateTimeIndex.
            TypeError: If data values are not numeric.
            IndexError: If index dates have duplicates.
        """

        if not isinstance(self._data.index, pd.DatetimeIndex):
            raise TypeError("Index type must be a DateTimeIndex")

        if not(pd.api.types.is_numeric_dtype(self._data)):
            raise TypeError("Data values must be numeric")
        
        if not (self._data.index.is_monotonic_increasing):
            self._data = self._data.sort_index()

        if self._data.index.has_duplicates:
            raise ValueError("Index contains duplicate dates")
        
    def _empty_copy(self, name: str | None = None) -> "TimeSeries":
        """Returns a time series with empty data.

        Args:
            name (str | None, optional): Name of the new empty TimeSeries. Defaults to None.

        Returns:
            TimeSeries: an empty timeseries
        """
        empty_data = pd.Series(dtype=float, index=pd.DatetimeIndex([]))
        return TimeSeries(data=empty_data, name=name)

    def _derived_name(self, prefix: str) -> str | None:
        """Generates the derived name when using functions that returns a TimeSeries class

        Args:
            prefix (str): prefix name for the functions (such as returns, cumreturns...)

        Returns:
            str | None: Derived name
        """
        return f"{prefix}_{self._name}" if self._name else None
    
    
    # ============================================================
    # BASE PROPERTIES
    # ============================================================

    @property
    def index(self) -> pd.DatetimeIndex:
        return self._data.index.copy()
    
    @property
    def values(self) -> np.ndarray:
        return self._data.values.copy()
    
    @property
    def data(self) -> pd.Series:
        return self._data.copy()
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def start_date(self) -> pd.Timestamp | None:
        return None if self.is_empty else self._data.index[0]
    
    @property
    def end_date(self) -> pd.Timestamp | None:
        return None if self.is_empty else self._data.index[-1]
    
    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    # ============================================================
    # CALCULATED PROPERTIES
    # ============================================================

    @property
    def returns(self) -> "TimeSeries":
        """Calculate relative returns of the time series.

        Returns:
            TimeSeries: A TimeSeries class with the returns data and the corresponding name
        """
    
        name = self._derived_name("returns")
        if self.is_empty:
            return self._empty_copy(name=name)
        
        returns_data = self._data.pct_change().iloc[1:]
        return TimeSeries(data=returns_data, name=name)

    @property
    def cumulative_returns(self) -> "TimeSeries":
        """Computes cumulative returns of the time series.

        Returns:
            TimeSeries: A TimeSeries class with the cumulative returns data and the same name
        """
        name = self._derived_name("cumreturns")
        if self.is_empty:
            return self._empty_copy(name=name)
        
        cumreturns_data = (self._data.pct_change()+1).cumprod()
        cumreturns_data.iloc[0] = 1
        return TimeSeries(data=cumreturns_data, name=name)
    
    @property
    def drawdown(self) -> "TimeSeries":
        """ Computes current drawdown (X_t / max_{s <= t}(X_s) - 1)  of the time series.

        Returns:
            TimeSeries: A TimeSeries class with the drawdown data and the same name
        """
        name = self._derived_name("drawdown")
        if self.is_empty:
            return self._empty_copy(name=name)
        
        drawdown_data = (self._data / self._data.cummax()) - 1
        return TimeSeries(data=drawdown_data,name=name)
    
    @property
    def max_drawdown(self) -> float:
        """ Computes max drawdown of the time series \n
            self.drawdown.data.min() \n
            Def of drawdown : "Computes current drawdown (X_t / max_{s <= t}(X_s) - 1)  of the time series."
        Returns:
            float: Max Drawdown of the time series
        """

        if self.is_empty:
            return 0.0
        
        return self.drawdown.data.min()

    # ============================================================
    # PUBLIC METHODS
    # ============================================================

    # %%%%%%%%%%%%%%%%%%%%%%%%%%
    # NaN management
    # %%%%%%%%%%%%%%%%%%%%%%%%%%
    def dropna(self) -> TimeSeries:
        """dropna like in pandas
        Returns:
            TimeSeries: a TimeSeries class with NA dropped
        """
        return TimeSeries(data=self._data.dropna(), name=self._name)
    
    def ffill(self, limit: int | None = None) -> TimeSeries:
        """Fill NA/NaN values by propagating the last valid observation to next valid.
        Args:
            limit (int): maximum amount of propagation for a single value.
        Returns:
            TimeSeries: a TimeSeries class with NA dropped
        """
        return TimeSeries(data=self._data.ffill(limit=limit), name=self._name)
    
    def bfill(self, limit: int | None = None) -> TimeSeries:
        """Fill NA/NaN values by using the next valid observation to fill the gap
        Args:
            limit (int): maximum amount of propagation for a single value.
        Returns:
            TimeSeries: a TimeSeries class with NA dropped
        """
        return TimeSeries(data=self._data.bfill(limit=limit), name=self._name)
    



    def align_with(self, other: TimeSeries, how: str = "inner",fill_method: str | None = None) -> tuple[TimeSeries, TimeSeries]:
        """Align two TimeSeries on the same dates, just like in pandas
        Args:
            other (TimeSeries class): The other TimeSeries to align with.
            how (str): Alignment method (inner, outer, left)
            fill_method (str | None): How to fill NAN values (ffill,bfill or none
        Returns:
            A tuple with two aligned time series
        """
        if self.is_empty or other.is_empty:
            return self._empty_copy(self._name), other._empty_copy(other._name)
        
        valid_how = {"inner", "outer", "left"}
        if how not in valid_how:
            raise ValueError(f"how must be one of {valid_how}, got '{how}'")
        
        aligned_self, aligned_other = self._data.align(other._data, join=how)
        
        if fill_method == "ffill":
            aligned_self = aligned_self.ffill()
            aligned_other = aligned_other.ffill()
        elif fill_method == "bfill":
            aligned_self = aligned_self.bfill()
            aligned_other = aligned_other.bfill()
        elif fill_method is not None:
            raise ValueError(f"fill_method must be 'ffill', 'bfill', or None, got '{fill_method}'")
        
        return (TimeSeries(aligned_self, name=self._name),TimeSeries(aligned_other, name=other._name))
    
    def resample(self, freq: str, method: str = "last") -> TimeSeries:
        """Resample the time series to a different frequency just like in Pandas
           It will either compute the sum or the mean of the values for the corresponding frequency.
        Args:
            freq: Target frequency (W (week), M (month), Q (quarter), Y (year) (like in pandas)
            method: Aggregation method (last,first,sum mean)
        Returns:
            The corresponding TimeSeries resampled.
        """

        if self.is_empty:
            return self._empty_copy(name=self._name)

        if method == "last":
            resampled_data = self._data.resample(freq).last()
        elif method == "first":
            resampled_data = self._data.resample(freq).first()
        elif method == "sum":
            resampled_data = self._data.resample(freq).sum()
        elif method == "mean":
            resampled_data = self._data.resample(freq).mean()
        else:
            raise ValueError(f"method must be 'last', 'first', 'sum', or 'mean', got '{method}'")
        
        resampled_data = resampled_data.dropna() #if resample recreates nan values?
        
        return TimeSeries(resampled_data, name=self._name)

    
        
    def at(self, index: str) -> float:
        """Equivalent to loc in pandas. Here you should enter a date for the TimeSeries index.
        Args:
            index (str): date timestamp
        Returns:
            float: corresponding line of the loc operation
        """
        return float(self._data.loc[index])

    def index_at(self, index: int) -> float:
        """Equivalent to iloc in pandas. Here you should enter an integer for the TimeSeries index.
        Args:
            index (int): index position of the line
        Returns:
            float: corresponding line
        """
        return float(self._data.iloc[index])
    
    def rename(self, new_name:str) -> "TimeSeries":
        """Returns a new TimeSeries class with the corresponding new name
        Args:
            new_name (str): new name of the timeseries.
        """
        return TimeSeries(data = self._data, name = new_name)  
    def between(self, start: str, end: str) -> TimeSeries:
        """Inclusively filters data between two dates
        Args:
            start (str): start date
            end (str): end date
        Returns:
            TimeSeries:  A new TimeSeries with the data between start and end (bounds are inclusive)
        """
        return self[start:end] 
    
    def first(self, period: int | str) -> TimeSeries:
        """Gives the first n points or first period based on the given argument
        Args:
            period (int | str): first n elements (int) or first period (6M,1Y,...)
        Returns:
            TimeSeries: a TimeSeries with the corresponding filter
        """
        if self.is_empty:
            return self._empty_copy(name=self._name)
    
        if isinstance(period, int):
            return TimeSeries(self._data.iloc[:period], name=self._name)

        elif isinstance(period, str):
            end_date = self.start_date + pd.tseries.frequencies.to_offset(period)
            return self.between(str(self.start_date), str(end_date))

        else:
            return NotImplemented

    def last(self, period: int | str) -> TimeSeries:
        """Gives the last n points or last period based on the given argument
        Args:
            period (int | str): last n elements (int) or last period (6M,1Y,...)
        Returns:
            TimeSeries: a TimeSeries with the corresponding filter
        """
        if self.is_empty:
            return self._empty_copy(name=self._name)
        
        if isinstance(period, int):
            return TimeSeries(self._data.iloc[-period:], name=self._name)
        elif isinstance(period, str):
            start_date = self.end_date - pd.tseries.frequencies.to_offset(period)
            return self.between(str(start_date), str(self.end_date))
        else:
            return NotImplemented




    # ============================================================
    # ARITHMETIC OPERATORS
    # ============================================================

    def __add__(self,elem_op: TimeSeries | int | float ) -> "TimeSeries":
        if isinstance(elem_op, (int,float)):
            result_data = self._data + elem_op
        elif isinstance(elem_op,TimeSeries):
            aligned_self, aligned_elem_op = self._data.align(other=elem_op._data,join="inner")
            result_data = aligned_self+aligned_elem_op
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data,name=None)
        
    def __radd__(self,elem_op: TimeSeries | int | float) -> "TimeSeries":
        return self.__add__(elem_op)
    
    def __sub__(self,elem_op: TimeSeries | int | float ) -> "TimeSeries":
        if isinstance(elem_op, (int,float)):
            result_data = self._data - elem_op
        elif isinstance(elem_op,TimeSeries):
            aligned_self, aligned_elem_op = self._data.align(other=elem_op._data,join="inner")
            result_data = aligned_self-aligned_elem_op
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data,name=None)   

    def __rsub__(self, elem_op: int | float) -> "TimeSeries":
        if isinstance(elem_op, (int, float)):
            result_data = elem_op - self._data
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data, name=None)

    def __mul__(self,elem_op: TimeSeries | int | float ) -> "TimeSeries":
        if isinstance(elem_op, (int,float)):
            result_data = self._data * elem_op
        elif isinstance(elem_op,TimeSeries):
            aligned_self, aligned_elem_op = self._data.align(other=elem_op._data,join="inner")
            result_data = aligned_self*aligned_elem_op
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data,name=None)   
    
    def __rmul__(self,elem_op: TimeSeries | int | float) -> "TimeSeries":
        return self.__mul__(elem_op)    

    def __truediv__(self,elem_op: TimeSeries | int | float ) -> "TimeSeries":
        if isinstance(elem_op, (int,float)):
            result_data = self._data / elem_op
        elif isinstance(elem_op,TimeSeries):
            aligned_self, aligned_elem_op = self._data.align(other=elem_op._data,join="inner")
            result_data = aligned_self/aligned_elem_op
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data,name=None)   
    
    def __rtruediv__(self, elem_op: int | float) -> "TimeSeries":
        if isinstance(elem_op, (int, float)):
            result_data = elem_op / self._data
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data, name=None)
    
    def __pow__(self,elem_op: TimeSeries | int | float ) -> "TimeSeries":
        if isinstance(elem_op, (int,float)):
            result_data = self._data ** elem_op
        elif isinstance(elem_op,TimeSeries):
            aligned_self, aligned_elem_op = self._data.align(other=elem_op._data,join="inner")
            result_data = aligned_self**aligned_elem_op
        else:
            return NotImplemented
        
        return TimeSeries(data=result_data,name=None)   

    def __neg__(self) -> "TimeSeries":
        return TimeSeries(data=  -self._data, name = self._name)
    

    # ============================================================
    # OTHER CLASSIC DUNDER METHODS
    # ============================================================

    def __getitem__(self, key:  slice | str | int | pd.Series) -> "TimeSeries" :
        """Acces data like in pandas but directly with the class based on a boolean mask, a date string, a date interval or an integer.

        Returns:
            TimeSeries: a TimeSeries with the corresponding filter

        """
        if isinstance(key,slice):
            filtered_data = self._data.loc[key.start:key.stop]
        elif isinstance(key,str):
            filtered_data = self._data.loc[key]
            if not isinstance(filtered_data,pd.Series):
                filtered_data = pd.Series(data=[filtered_data],index=[pd.Timestamp(key)])
                
        elif isinstance(key,int):
            filtered_data = pd.Series(data=[self._data.iloc[key]],index=[self._data.index[key]])
        elif isinstance(key,pd.Series):

            if key.dtype != bool: #otherwise if the user enters a pd.Series that isnt a boolean mask it will not raise an error
                raise TypeError("Mask must be a pd.Series of dtype bool")
            key_masque = key.reindex(self._data.index,fill_value = False)
            filtered_data = self._data.loc[key_masque]
        else:
            return NotImplemented       

        return TimeSeries(data=filtered_data, name = self._name)

        

    

    def __repr__(self) -> str:
        name_str = self._name if self._name else "unnamed_series"

        if self.is_empty:
            return (f"TimeSeries({name_str}, empty)")
        
        start_date = self.start_date.date()
        end_date = self.end_date.date()

        return (f"TimeSeries({name_str}, {start_date} to {end_date}, {len(self)} values)")

    def __len__(self) -> int:
        return self._data.size


if __name__ == "__main__":
    print(2)