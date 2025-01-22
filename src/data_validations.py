"""Module containing data validations"""


def find_and_remove_duplicates(school_df, col_names_to_check_duplicates=None):
    """ 
    Check for and remove any duplicate rows in the school data 
    
    Return: deduplicated dataframe
    """
    
    # Check for duplicates based on column names
    duplicate_mask = school_df.duplicated(subset=col_names_to_check_duplicates, keep=False)
    duplicates = school_df[duplicate_mask]

    if not duplicates.empty:
        print("Duplicates detected:") # TODO: Raise a warning here
        print(duplicates)

    school_df['periodeid_length'] = school_df['periodeid'].str.len()
    df_sorted = school_df.sort_values(by=col_names_to_check_duplicates+['periodeid_length'])

    # Drop duplicates, keeping the first occurrence (shortest 'periodeid')
    df_deduplicated = df_sorted.drop_duplicates(subset=col_names_to_check_duplicates, keep='first')
    
    # Identify and log removed duplicates
    removed_duplicates = duplicates[~duplicates.index.isin(df_deduplicated.index)]
    if not removed_duplicates.empty:
        print("Removed duplicates:") # TODO: Print what duplicates were deleted if there were duplicates
        print(removed_duplicates)

    # Clean up the temporary column
    df_deduplicated = df_deduplicated.drop(columns=['periodeid_length'])
    df_deduplicated = df_deduplicated.reset_index(drop=True)
    
    return df_deduplicated

def confirm_key_exists_and_is_identical(key)