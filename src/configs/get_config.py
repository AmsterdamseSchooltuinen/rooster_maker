"""Utils to read yaml files and add dev suffix to permissions"""

from pathlib import Path

import yaml


def get_config(config_name: str) -> dict:
    """Get the solver config from the yaml file.

    Returns:
        dict: dictionary of the solver config vars
    """
    if config_name not in ["solver_config", "input_data_config", "constraints_config"]:
        print(f"Invalid config name: {config_name}")
        # raise Exception(f"Invalid config name: {config_name}")
    file_path = Path(__file__).parent / f"{config_name}.yaml"
    return _open_yaml_file(file_path)


def _open_yaml_file(file_path: str) -> dict:
    """Util to read yaml files with error handling.

    Parameters:
        file_path (str): path to yaml file

    Returns:
        dict: dictionary of the yaml file vars
    """
    with open(file_path, "r") as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            raise Exception(f"Error reading {file_path}: {e}")
