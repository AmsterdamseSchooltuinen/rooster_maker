import streamlit as st
import pandas as pd

def do_streamlit():

    title_label = "Goede morgen!"
    educators_label = "Leraren Beschikbaarheid Data"
    school_label = "Groep Beschikbaarheid Data"
    garden_label = "Schooltuinen Data"

    st.title(title_label)


    educators_bytes = st.file_uploader(educators_label)
    school_bytes = st.file_uploader(school_label)
    garden_bytes = st.file_uploader(garden_label)

    st.divider()
    status = st.button("Go!", use_container_width=True)
    st.divider()

    if status:
        st.write("Alright!")



do_streamlit()