import streamlit as st
from src.configs.get_config import get_config
from src.streamlit import ValidationException
from src.extract_transform_load import run_extract_transform_load


def main_test():
    run_extract_transform_load(None, None, None)


def main():
    config = get_config("input_data_config")
    title_label = config["labels"]["title_label"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]
    run_label = config["labels"]["run_label"]

    st.title(title_label)
    inputs_needed = True

    educators_bytes = st.file_uploader(educators_label)
    school_bytes = st.file_uploader(school_label)
    garden_bytes = st.file_uploader(garden_label)

    if (
        educators_bytes is not None
        and school_bytes is not None
        and garden_bytes is not None
    ):
        inputs_needed = False

    run_override = st.button("Run even if inputs are missing")

    st.divider()
    run = st.button(run_label, use_container_width=True, disabled=inputs_needed)
    st.divider()

    if run or run_override:
        try:
            run_extract_transform_load(educators_bytes, garden_bytes, school_bytes)
        except ValidationException as e:
            st.error(f"{e.input_name}: {e}")
        except FileNotFoundError as e:
            st.error(f"File not found: {e}??")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
