# data/loader.py
from __future__ import annotations
import pandas as pd
from pathlib import Path
from core.asset import Asset
from core.universe import Universe


class DataLoader:

    @staticmethod
    def from_csv(ticker: str, path: str) -> Asset:
        """Load an Asset from a csv file

        Args:
            ticker (str): ticker
            path (str): path of the csv data

        Returns:
            Asset: Asset with ticker name and csv data as OHLCV
        """
        return Asset(ticker = ticker,data = pd.read_csv(path,index_col=0,parse_dates=True))
    
    @staticmethod
    def from_csv_folder(folder_path: str) -> Universe:
        folder = Path(folder_path)
        lst_assets = []
        for file in folder.glob("*.csv"):
            ticker = file.stem
            asset = DataLoader.from_csv(ticker, str(file))
            lst_assets.append(asset)
        return Universe(assets=lst_assets)
    
    @staticmethod
    def from_dataframe(ticker: str, df: pd.DataFrame) -> Asset:
        return Asset(ticker = ticker, data = df)
    
    #@staticmethod
    # def from_bbg(ticker: str) -> Universe:
    #     pass

