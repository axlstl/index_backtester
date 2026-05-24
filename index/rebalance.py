from __future__ import annotations
import pandas as pd


class RebalanceSchedule:
    """Class representing a rebalance schedule for the index weights. 
        Frequency can take the following values :
            - 'D' : Daily
            - 'B' : Business days
            - 'W' : Weekly
            - 'W-MON' : Weekly on Mondays
            - 'MS' : Month start
            - 'ME' : Month end
            - 'QS' : Quarter start
            - 'QE' : Quarter end
            - 'YS' : Year start
            - 'YE' : Year end
        """
    def __init__(self, freq: str | None = None, dates: list[str] | None = None):
        """

        Args:
            freq (str | None, optional): Frequency string. Defaults to None.

            dates (list[str] | None, optional): List of specific rebalance dates. Defaults to None.

        Raises:
            ValueError: If neither freq nor dates are provided.
            ValueError: If both freq and dates are provided.
        """
        if freq is None and dates is None:
            raise ValueError("Either freq or dates must be provided")
        if freq is not None and dates is not None:
            raise ValueError("Cannot provide both freq and dates")

        self._freq = freq
        self._dates = sorted(dates) if dates else None
    
    @property
    def freq(self) -> str | None:
        return self._freq
    
    def get_rebalance_dates(self, start: str, end: str) -> list[str]:
        """Gets the rebalance dates between start and end.

        Args:
            start (str): Start date.
            end (str): End date.

        Returns:
            list[str]: A list of rebalance dates between start and end.
        """
        if self._freq:
            dates = pd.date_range(start=start, end=end, freq=self._freq)
            return [str(d.date()) for d in dates]
        else:
            return [d for d in self._dates if start <= d <= end]
    