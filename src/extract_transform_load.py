import os
import re

import pandas as pd

import src.data_validations as dv
from src.configs.get_config import get_config
from src.data_validations import ValidationException, ValidationExceptionCollector

config = get_config("input_data_config")

# Move this to the front end in final version
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path_educator_data = os.path.join(current_dir, "data", "EDUCATORS 2025.xlsx")
file_path_garden_data = os.path.join(current_dir, "data", "SCHOOL GARDENS 2025.xlsx")
file_path_school_data = os.path.join(current_dir, "data", "SCHOOLS 2025.xlsx")


def run_extract_transform_load(
    educator_data: bytes, garden_data: bytes, school_data: bytes
):

    if not educator_data:
        educator_data = file_path_educator_data
    if not garden_data:
        garden_data = file_path_garden_data
    if not school_data:
        school_data = file_path_school_data

    educator_df, garden_df, school_df = load_data(educator_data, garden_data, school_data)

    data, timeslots = run_transformation(educator_df, garden_df, school_df)

    # try:
    #     execute_validations(config["validations"], data)
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     raise e
    
    return data["educator_df"], data["garden_df"], data["school_df"], timeslots


def load_data(educator_data, garden_data, school_data):
    # Load the Excel files
    educator_df = pd.read_excel(educator_data)
    garden_df = pd.read_excel(garden_data)
    school_df = pd.read_excel(school_data)

    return educator_df, garden_df, school_df


def run_transformation(educator_df, garden_df, school_df):
    col_mapping_educator = {
        k: v for d in config["etl"]["educator"]["col_mapping"] for k, v in d.items()
    }
    col_mapping_school = {
        k: v for d in config["etl"]["school"]["col_mapping"] for k, v in d.items()
    }
    col_mapping_garden = {
        k: v for d in config["etl"]["garden"]["col_mapping"] for k, v in d.items()
    }

    educator_df.rename(columns=col_mapping_educator, inplace=True)
    school_df.rename(columns=col_mapping_school, inplace=True)
    garden_df.rename(columns=col_mapping_garden, inplace=True)

    timeslots = get_timeslots(
        educator_df, excluded_cols_timeslots=["garden_name", "educator"]
    )

    school_df = transform_school_file(school_df)
    educator_df = transform_educator_file(educator_df)
    garden_df = transform_garden_file(garden_df)

    school_df = clean_primary_keys(
        school_df, primary_keys=config["etl"]["school"]["primary_keys"]
    )
    educator_df = clean_primary_keys(
        educator_df, primary_keys=config["etl"]["educator"]["primary_keys"]
    )
    garden_df = clean_primary_keys(
        garden_df, primary_keys=config["etl"]["garden"]["primary_keys"]
    )


    output_data = {
        "educator_df": educator_df,
        "garden_df": garden_df,
        "school_df": school_df,
    }

    return output_data, timeslots


def clean_primary_keys(df: pd.DataFrame, primary_keys: list[str]) -> pd.DataFrame:
    """
    Clean the primary keys in a dataframe.
    """

    for key in primary_keys:
        df = df.dropna(subset=[key])
    return df


def get_timeslots(educator_data, excluded_cols_timeslots):
    timeslots = [
        col for col in educator_data.columns if col not in excluded_cols_timeslots
    ]
    return timeslots


def transform_school_file(school_df: pd.DataFrame):
    """
    Transform school DataFrame
    1. Transform time string to standard format
    2. Add a specific group id column
    """
    col_names_timeslots = config["etl"]["school"]["col_names_timeslots"]

    # Step 1: change the timeslot strings to a standard format
    for column in col_names_timeslots:
        school_df[column] = school_df[column].apply(standardize_time_string)

    # Step 2: Add 'group_id' column
    school_df["group_id"] = (
        str(school_df["period_id"]) + "_" + str(school_df["school_id"])
    )

    return school_df


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
    s = s.replace(".", ":")

    # 4) Sometimes there's a space around the dash. Let's remove that:
    s = re.sub(r"\s*-\s*", "-", s)

    # 5) We want a consistent day/time separator.
    #    Some entries have a comma, some don't. Let’s ensure day and time are separated by a comma+space.
    #    A quick approach is to insert a comma if there's no comma between the day and the time portion:
    #    But we must watch out if a comma is already there.

    #    We'll do something like: if there's "maandag" (or other day) followed by a space, then digit,
    #    place a comma in between.
    #    Note that day names can be: maandag, dinsdag, woensdag, donderdag, vrijdag.
    #    We'll use a small day-regex and see if there's no comma after it:

    day_pattern = r"(maandag|dinsdag|woensdag|donderdag|vrijdag)"
    s = re.sub(rf"^{day_pattern}\s+(?=\d)", r"\1, ", s)

    # 6) Some times have an extra space in the time range like "10:45- 12:15", so let's remove that:
    s = re.sub(r"(\d+:\d+)\s*-\s*(\d+:\d+)", r"\1-\2", s)

    # 7) Ensure that hours have leading zeros if it’s only one digit.
    #    For example '9:00' -> '09:00'. We'll capture hour:minute and reformat.
    #    We can do this by a small function that zero-pads the hour portion:
    def zero_pad(match):
        hour = match.group(1)
        minute = match.group(2)
        return f"{int(hour):02d}:{minute}"  # ensure hour is 2 digits

    # Zero-pad both times in the range:
    s = re.sub(r"(\d{1,2}):(\d{2})", zero_pad, s)

    # 8) Now we should have something like "woensdag, 09:00-10:30" consistently.
    #    But let's do a final trim in case there are leftover spaces:
    s = s.strip()

    return s


def transform_educator_file(educator_df):
    return educator_df


def transform_garden_file(garden_df):
    return garden_df


def execute_validations(validation_config: list[dict], data: dict):
    exceptions = []
    for validation in validation_config:
        for validation_name, validation_args in validation.items():
            validation_func = getattr(dv, validation_name)
            args = [data[arg_value] if 'df' in arg_key else arg_value for arg_key, arg_value in validation_args.items()]
            table: str = [arg_value for arg_key, arg_value in validation_args.items() if 'df' in arg_key][0]
            args += [table]
            failure, message = validation_func(*args)
            if failure:
                table_names = [arg_value for arg_key, arg_value in validation_args.items() if 'df' in arg_key]
                exceptions.append(ValidationException(message, table_names))
    if exceptions:
        raise ValidationExceptionCollector(exceptions)
