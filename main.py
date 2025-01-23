import streamlit as st
from src.configs.get_config import get_config
from src.streamlit import ValidationException

def main():
    config = get_config("visual_config")
    title_label = config["labels"]["title_label"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]

    st.title(title_label)
    inputs_needed = True

    educators_bytes = st.file_uploader(educators_label)
    school_bytes = st.file_uploader(school_label)
    garden_bytes = st.file_uploader(garden_label)

    if educators_bytes and school_bytes and garden_bytes:
        inputs_needed = False

    inputs_needed = not st.button("pretend files are uploaded")

    st.divider()
    run = st.button("Run!", use_container_width=True, disabled=inputs_needed)
    st.divider()

    if run:
        try:
            print("hi")
        except ValidationException as e:
            st.error(f"{e.input_name}: {e}")
        except FileNotFoundError as e:
            st.error(f"File not found: {e}??")


if __name__ == "__main__":
    main()