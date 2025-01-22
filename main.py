from src.configs import get_config
import streamlit as st

def main():

    config = get_config("visual_config")
    title_label = config["labels"]["title_label"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]

    st.title(title_label)

    educators_bytes = st.file_uploader(educators_label)
    school_bytes = st.file_uploader(school_label)
    garden_bytes = st.file_uploader(garden_label)

    st.divider()
    status = st.button("Go!", use_container_width=True)
    st.divider()

    if status:
        st.write("Alright!")

if __name__ == "__main__":
    main()