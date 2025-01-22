import pandas as pd
import os
import warnings

config = [] 

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path_educator_data = os.path.join(current_dir, 'data', 'EDUCATORS 2025.xlsx')
file_path_garden_data = os.path.join(current_dir, 'data', 'SCHOOL GARDENS 2025.xlsx')
file_path_school_data = os.path.join(current_dir, 'data', 'SCHOOLS 2025.xlsx')

class ValidationException(Exception):
    def __init__(self, message, input_name):
        super().__init__(message)
        self.input_name = input_name
    
def run_extract_transform_load(config):
    path_educator_data = file_path_educator_data # change to config 
    path_garden_data = file_path_garden_data # change to config
    path_school_data = file_path_school_data # change to config

    educator_df, garden_df,school_df = load_data(path_educator_data, path_garden_data, path_school_data)
    run_data_validation(educator_df, garden_df, school_df)
    
    return
    
def load_data(path_educator_data, path_garden_data, path_school_data):
    # Check if each file exists
    if not os.path.isfile(path_educator_data):
        raise FileNotFoundError(f"File not found: {path_educator_data}") #TODO: change so error is handled in front end
    if not os.path.isfile(path_garden_data):
        raise FileNotFoundError(f"File not found: {path_garden_data}") #TODO: change so error is handled in front end
    if not os.path.isfile(path_school_data):
        raise FileNotFoundError(f"File not found: {path_school_data}") #TODO: change so error is handled in front end

    # Load the Excel files
    educator_df = pd.read_excel(path_educator_data)
    garden_df = pd.read_excel(path_garden_data)
    school_df = pd.read_excel(path_school_data)
    
    return educator_df, garden_df, school_df

def run_data_validation(educator_data, garden_data, school_data):
    school_data, timeslots = validate_school_file(school_data, config) 
    validate_educator_file(educator_data, timeslots)
    validate_garden_file(garden_data)

def validate_school_file(school_df, config):
    """
    Validates a school DataFrame by identifying and handling duplicate rows based on specific columns ('col1' and 'col2').

    Parameters:
        df (pd.DataFrame): The input DataFrame with a 'periodeid' column.

    Returns:
        pd.DataFrame: A DataFrame with duplicates handled.
        list: A list of timeslots or duplicate information.
    """
    # Put these in the config: 
    col_names_to_check_duplicates = ['schoolcode', 'naam', 'groep']
    col_names_timeslots = ['vrijveld 2', 'vrijveld 3', 'vrijveld 4', 'vrijveld 5', 'vrijveld 6']
    
    school_df = find_and_remove_duplicates(school_df, col_names_to_check_duplicates=col_names_to_check_duplicates) 
    
    # Create a list of all distinct timeslots found in the school data
    timeslots = pd.unique(school_df[col_names_timeslots].values.ravel())
    print(timeslots)
    breakpoint()

    return school_df, timeslots

def validate_educator_file(educator_data, timeslots):
        
    return

def validate_garden_file(garden_data, timeslots):
    
    return

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

run_extract_transform_load(config)