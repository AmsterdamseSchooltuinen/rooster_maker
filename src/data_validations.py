"""Module containing data validations"""
import pandas as pd

class ValidationException(Exception):
    def __init__(self, message, input_name):
        super().__init__(message)
        self.input_name = input_name
    

def check_duplicates(df: pd.DataFrame, col_names_to_check_duplicates: list[str] | str, sort_by_col: str) -> tuple[bool, str]:
    """ 
    Check for and remove any duplicate rows in a dataframe, given a  
    
    Returns:
        bool: True if duplicates were found, False otherwise.
    """
    
    # Check for duplicates based on column names
    duplicate_mask = df.duplicated(subset=col_names_to_check_duplicates, keep=False)
    duplicates = df[duplicate_mask]

    if not duplicates.empty:
        return True, "Duplicates found"
    return False, "All good"
    # sort_by_col_len = f"{sort_by_col}_len"
    # df[sort_by_col_len] = df[sort_by_col].str.len()
    # df_sorted = df.sort_values(by=col_names_to_check_duplicates+[sort_by_col_len])

    # # Drop duplicates, keeping the first occurrence (shortest 'periodeid')
    # df_deduplicated = df_sorted.drop_duplicates(subset=col_names_to_check_duplicates, keep='first')
    
    # # Identify and log removed duplicates
    # removed_duplicates = duplicates[~duplicates.index.isin(df_deduplicated.index)]
    # if not removed_duplicates.empty:
    #     print("Removed duplicates:") # TODO: Print what duplicates were deleted if there were duplicates
    #     print(removed_duplicates)

    # # Clean up the temporary column
    # df_deduplicated = df_deduplicated.drop(columns=[sort_by_col_len])
    # df_deduplicated = df_deduplicated.reset_index(drop=True)
    
    # return df_deduplicated

def confirm_key_exists_and_is_identical(key_col: str, df1: pd.DataFrame, df2: pd.DataFrame) -> tuple[bool, str]:
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
        return True, f"Key column {key_col} does not exist in both dataframes"

    if not df1[key_col].equals(df2[key_col]):
        return True, f"Key column ({key_col}) values are not identical"

    return False, "All good"