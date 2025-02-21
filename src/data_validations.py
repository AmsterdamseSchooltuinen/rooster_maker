"""Module containing data validations"""
import pandas as pd
from src.configs.get_config import get_config

config = get_config("input_data_config")

class ValidationException(Exception):
    def __init__(self, message, input_name):
        super().__init__(message)
        self.message = message
        self.input_name = input_name
    
    def __str__(self):
        return f"{self.input_name}: {self.message}"
    
class ValidationExceptionCollector(Exception):
    def __init__(self, exceptions: list[ValidationException]):
        self.exceptions = exceptions

class ValidationWarning:
    def __init__(self, message, input_name):
        self.message = message
        self.input_name = input_name
        
    def __str__(self):
        return f"{self.input_name}: {self.message}"


def flatten_dicts(dicts: list[dict]) -> dict:
    """
    Flatten a list of dictionaries into a single dictionary.
    
    Parameters:
        dicts (list[dict]): The list of dictionaries to flatten.
        
    Returns:
        dict: The flattened dictionary.
    """
    return {k: v for d in dicts for k, v in d.items()}


def get_frontend_name(new_name, table_name, config):
    """
    Gets the front end column name for a given new name.
    Args:
        new_name (str): The new column name.
        mapping (dict): Mapping that was used to create the new column name
    Returns:
        str: The original column name, or None if not found.
    """
    if table_name == "educator_data":
        mapping = config["etl"]["educator"]["col_mapping"]
    elif table_name == "school_data":
        mapping = config["etl"]["school"]["col_mapping"]
    elif table_name == "garden_data":
        mapping = config["etl"]["garden"]["col_mapping"]
    else:
        raise ValueError("Invalid table name")
    
    mapping = flatten_dicts(mapping)

    reverse_mapping = {}
    for k, v in mapping.items():
        reverse_mapping[v] = k

    return reverse_mapping.get(new_name, None)


def check_duplicates(df: pd.DataFrame, col_names_to_check_duplicates: list[str] | str, df_name: str) -> tuple[bool, str]:
    """ 
    Check for and remove any duplicate rows in a dataframe.
    
    Returns:
        bool: True if duplicates were found, False otherwise.
    """
    duplicate_mask = df.duplicated(subset=col_names_to_check_duplicates, keep=False)
    duplicates = df[duplicate_mask]

    duplicate_values = duplicates[col_names_to_check_duplicates[0]].to_list()
    

    if not duplicates.empty:
        return True, f"Er staat een dubbele rij met dezelfde: {get_frontend_name(col_names_to_check_duplicates[0], df_name, config)}: {duplicate_values}"
    return False, "All good"

def confirm_key_exists_and_is_identical(key_col: str, df1: pd.DataFrame, df2: pd.DataFrame, df_name: str) -> tuple[bool, str]:
    """
    Check if the key column exists in both dataframes and if the values are identical.
    
    Parameters:
        key_col (str): The key column to check.
        df1 (pd.DataFrame): The first DataFrame to compare.
        df2 (pd.DataFrame): The second DataFrame to compare.
        
    Returns:
        bool: True if the key column does not exist in both dataframes or if the values are not identical, False otherwise.
    """
    if key_col not in df1.columns or key_col not in df2.columns:
        return True, f"Key column {get_frontend_name(key_col, df_name, config)} does not exist in both dataframes"

    unique_values_df1 = df1[key_col].to_list()
    unique_values_df2 = df2[key_col].to_list()

    if not (set(unique_values_df1) == set(unique_values_df2)):
        return True, f"Key column ({get_frontend_name(key_col, df_name, config)}) values are not identical \n{unique_values_df1} \n{unique_values_df2}"

    return False, "All good"

def check_key_cols(df: pd.DataFrame, key_cols: list[str], df_name: str) -> tuple[bool, str]:
    """
    Check if the key columns exist and are there any blank values.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to check.
        key_cols (list[str]): The key columns to check.
        
    Returns:
        bool: True if there are blank values in the key columns, False otherwise.
    """
    for col in key_cols:
        if col not in df.columns:
            return True, f"column naam: {col}, {get_frontend_name(col, df_name, config)} not available in file. Heb je het juiste bestand geüpload?"
        if df[col].isnull().values.any():
            return True, f"Blank values found in key column {get_frontend_name(col, df_name, config)}"
    return False, "All good"

def check_any_empty_cols(df: pd.DataFrame, df_name: str) -> tuple[bool, str]:
    """
    Check if the key columns exist and are there any blank values.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to check.
        
    Returns:
        bool: True if there are blank values, False otherwise.
    """
    cols = df.columns
    for col in cols:
        if df[col].isnull().values.any():
            return True, f"Blank values found in '{get_frontend_name(col, df_name, config)}'"
    return False, "All good"

def check_at_least_one_col_filled(df: pd.DataFrame, cols: list[str], group_id_col: str, df_name: str) -> tuple[bool, str]:
    """
    Check if at least one of the columns is filled per row.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to check.
        cols (list[str]): The columns to check.
        group_id_col (str): The group id column.
    Returns:
        bool: True if all columns are empty, False otherwise.
    """
    empty_rows = df[cols].isnull().all(axis=1)
    group_ids = df.loc[empty_rows, group_id_col].tolist()
    if empty_rows.any():
        return True, f"Groep(en): {group_ids} heeft geen voorkeurstijden opgegeven"
    return False, "All good"

def test_validation(df: pd.DataFrame, cols: list[str], df_name: str) -> tuple[bool, str]:
    """
    Test validation function.
    """
    return True, f"(test) Column {get_frontend_name(cols[0], df_name, config)} not available in {df_name}"