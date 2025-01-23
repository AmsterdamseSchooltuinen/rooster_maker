import streamlit as st
from src.configs.get_config import get_config
from src.extract_transform_load import run_extract_transform_load
from src.data_validations import ValidationExceptionCollector


def main_test():
    run_extract_transform_load(None, None, None)

def main():
    config = get_config("visual_config")
    title_label = config["labels"]["title_label"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]
    run_label = config["labels"]["run_label"]

    st.title(title_label)
    inputs_needed = True

    educators_bytes = st.file_uploader(educators_label, type = "xlsx")
    school_bytes = st.file_uploader(school_label, type = "xlsx")
    garden_bytes = st.file_uploader(garden_label, type = "xlsx")

    if educators_bytes is not None and school_bytes is not None and garden_bytes is not None:
        inputs_needed = False

    run_override = st.button("Run even if inputs are missing")

    st.divider()
    run = st.button(run_label, use_container_width=True, disabled=inputs_needed)
    st.divider()

    if run or run_override:
        try:
            run_extract_transform_load(educators_bytes, garden_bytes, school_bytes)
        except ValidationExceptionCollector as e:
            st.header("❌ Er waren enkele problemen:", divider="red")
            for ex in e.exceptions:
                with st.error("Validatie Error"):
                    st.markdown(f"**{ex}**")


if __name__ == "__main__":
    main()