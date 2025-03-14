import pandas as pd


class Utils:
    @staticmethod
    def get_name_or_columns(obj):
        """
        Get name or column of pandas Series / DataFrame
        """
        if isinstance(obj, pd.Series):
            return [obj.name]
        elif isinstance(obj, pd.DataFrame):
            return obj.columns.to_list()
        else:
            raise ValueError("Expected a pd.Series or pd.DataFrame object.")

    @staticmethod
    def get_vector_name(obj, default_name="x"):
        """
        Get vector name and return a default name if no name.
        """
        if isinstance(obj, pd.Series):
            return obj.name
        elif isinstance(obj, pd.DataFrame):
            return obj.columns[0]
        else:
            return default_name
