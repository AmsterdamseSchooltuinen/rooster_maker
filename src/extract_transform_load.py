import pandas as pd
import re
import os
from src.configs.get_config import get_config
from src.data_validations import find_and_remove_duplicates

config = get_config("etl_config")

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
    timeslots = get_timeslots(educator_data)
    school_data = transform_school_file(school_data, config) 
    
    # check whether tuinlocatie and locatie are the same always 
    
    
    # validate_educator_file(educator_data, timeslots)
    # validate_garden_file(garden_data)

def get_timeslots(educator_data):
    breakpoint()
    return
    
def transform_school_file(school_df, config):
    """
    transform a school DataFrame by identifying and handling duplicate rows based on specific columns ('col1' and 'col2').

    Parameters:
        df (pd.DataFrame): The input DataFrame with a 'periodeid' column.

    Returns:
        pd.DataFrame: A DataFrame with duplicates handled.
        list: A list of timeslots or duplicate information.
    """
    # Put these in the config: 
    col_names_to_check_duplicates = ['schoolcode', 'naam', 'groep']
    col_names_timeslots = ['vrijveld2', 'vrijveld3', 'vrijveld4', 'vrijveld5', 'vrijveld6']
    
    # Step 1: find and remove any duplicate rows
    school_df = find_and_remove_duplicates(school_df, col_names_to_check_duplicates=col_names_to_check_duplicates) 
    
    # Step 2: change the timeslot strings to a standard format
    for column in col_names_timeslots:
        school_df[column] = school_df[column].apply(standardize_time_string)
    
    # # Create a list of all distinct timeslots found in the school data
    # timeslots = pd.unique(school_df[col_names_timeslots].values.ravel())

    return school_df

def validate_school_file(school_data):
    return

def validate_educator_file(educator_data: pd.DataFrame, timeslots):

    
        
    return

def validate_garden_file(garden_data: pd.DataFrame, timeslots):    
    return

def find_and_remove_duplicates(school_df, col_names_to_check_duplicates=None):
    """ 
    Check for and remove any duplicate rows in the school data.
    
    Return: deduplicated dataframe
    """
    # Check for duplicates based on column names
    duplicate_mask = school_df.duplicated(subset=col_names_to_check_duplicates, keep=False)
    duplicates = school_df[duplicate_mask]

    if not duplicates.empty:
        print("Duplicates detected:")  # TODO: Raise a warning here
        print(duplicates)

    # Ensure 'periodeid' column is treated as strings
    school_df['periodeid'] = school_df['periodeid'].astype(str)
    school_df['periodeid_length'] = school_df['periodeid'].str.len()

    # Sort by the specified columns and 'periodeid_length'
    df_sorted = school_df.sort_values(by=col_names_to_check_duplicates + ['periodeid_length'])

    # Drop duplicates, keeping the first occurrence (shortest 'periodeid')
    df_deduplicated = df_sorted.drop_duplicates(subset=col_names_to_check_duplicates, keep='first')
    
    # Identify and log removed duplicates
    removed_duplicates = duplicates[~duplicates.index.isin(df_deduplicated.index)]
    if not removed_duplicates.empty:
        print("Removed duplicates:")  # TODO: Print what duplicates were deleted if there were duplicates
        print(removed_duplicates)

    # Clean up the temporary column
    df_deduplicated = df_deduplicated.drop(columns=['periodeid_length'])
    df_deduplicated = df_deduplicated.reset_index(drop=True)
    
    return df_deduplicated

def standardize_time_string(s: str) -> str:
    """
    Takes a string describing a day/time (in various inconsistent formats)
    and normalizes it to the format: 'dag, HH:MM-HH:MM'.
    """
    if not isinstance(s, str):
        return s  # If it's NaN or None, just return it

    # 1) Convert to lowercase
    s = s.lower()

    # 2) Remove "uur" if present
    s = s.replace(" uur", "")

    # 3) Replace '.' with ':' (for times like 09.00 -> 09:00)
    s = s.replace('.', ':')

    # 4) Sometimes there's a space around the dash. Let's remove that:
    s = re.sub(r'\s*-\s*', '-', s)

    # 5) We want a consistent day/time separator. 
    #    Some entries have a comma, some don't. Let’s ensure day and time are separated by a comma+space.
    #    A quick approach is to insert a comma if there's no comma between the day and the time portion:
    #    But we must watch out if a comma is already there.

    #    We'll do something like: if there's "maandag" (or other day) followed by a space, then digit,
    #    place a comma in between.
    #    Note that day names can be: maandag, dinsdag, woensdag, donderdag, vrijdag.
    #    We'll use a small day-regex and see if there's no comma after it:

    day_pattern = r"(maandag|dinsdag|woensdag|donderdag|vrijdag)"
    s = re.sub(fr"^{day_pattern}\s+(?=\d)", r"\1, ", s)

    # 6) Some times have an extra space in the time range like "10:45- 12:15", so let's remove that:
    s = re.sub(r'(\d+:\d+)\s*-\s*(\d+:\d+)', r'\1-\2', s)

    # 7) Ensure that hours have leading zeros if it’s only one digit. 
    #    For example '9:00' -> '09:00'. We'll capture hour:minute and reformat.
    #    We can do this by a small function that zero-pads the hour portion:
    def zero_pad(match):
        hour = match.group(1)
        minute = match.group(2)
        return f"{int(hour):02d}:{minute}"  # ensure hour is 2 digits

    # Zero-pad both times in the range:
    s = re.sub(r'(\d{1,2}):(\d{2})', zero_pad, s)

    # 8) Now we should have something like "woensdag, 09:00-10:30" consistently.
    #    But let's do a final trim in case there are leftover spaces:
    s = s.strip()
 
    return s 
run_extract_transform_load(config)