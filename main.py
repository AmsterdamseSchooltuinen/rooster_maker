import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import os

from src.configs.get_config import get_config
from src.extract_transform_load import run_extract_transform_load
from src.data_validations import ValidationExceptionCollector
from src.runner import run_program


def main_test():
    run_extract_transform_load(None, None, None)

def main():
    config = get_config("input_data_config")
    title_label = config["labels"]["title_label"]
    sub_title = config["labels"]["sub_title"]
    subheader_label = config["labels"]["subheader_label"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]
    run_label = config["labels"]["run_label"]
    finished_run_label = config["labels"]['finished_run_label']
    educators_template_name = config["template_file_names"]["educators_template"]
    school_template_name = config["template_file_names"]["school_template"]
    garden_template_name = config["template_file_names"]["garden_template"]


    css_styles = config['Styles']['css']
    st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)
    

    #Title
    st.markdown(f"<div class='header'>{title_label}</div>", unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)

    #Sub Title 
    st.markdown(f"<div class='subheader'>{sub_title}</div>", unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)

    st.subheader(subheader_label)
    inputs_needed = True

    current_dir = os.path.dirname(os.path.abspath(__file__))
    educators_template_path = os.path.join(current_dir, "data", educators_template_name)
    school_template_path = os.path.join(current_dir, "data", school_template_name)
    garden_template_path = os.path.join(current_dir, "data", garden_template_name)
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.download_button(
            label="Download beschikbaarheid groepen",
            data=open(educators_template_path, "rb").read(),
            file_name="educators_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )        
    with col2:
        st.download_button(
        label="Download beschikbaarheid groepen template",
        data=open(school_template_path, "rb").read(),
        file_name="school_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col3:
        st.download_button(
            label="Download schooltuinen informatie template",
            data=open(garden_template_path, "rb").read(),
            file_name="garden_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.divider()
    
    educators_bytes = st.file_uploader(educators_label, type = "xlsx")
    school_bytes = st.file_uploader(school_label, type = "xlsx")
    garden_bytes = st.file_uploader(garden_label, type = "xlsx")


            
    # Create buttons to download templates






    inputs_needed = not (educators_bytes and school_bytes and garden_bytes)

    if "run_clicked" not in st.session_state:
        st.session_state.run_clicked = False
        
    run_override = st.button("Run even if inputs are missing")
    run = st.button(run_label, use_container_width=True, disabled=inputs_needed)
    
    st.divider()

    if run or run_override:
        st.session_state.run_clicked = True        
        try:
            educator_data, garden_data, school_data, timeslots, warnings = run_extract_transform_load(educators_bytes, garden_bytes, school_bytes)
            if warnings:
                st.header("⚠️ Mogelijk is er een probleem", divider="orange")
                for warning in warnings:
                    with st.warning("Mischien een problem?"):
                        st.markdown(f"**{warning}**")
            # RUN EVERYTHING HERE
            # TODO: update the output function because it doesn't work at the moment
            summary_statistics_dict, final_output_df = run_program(school_data=school_data,
                                                                   educator_data=educator_data,
                                                                   garden_data=garden_data,
                                                                   time_slots=timeslots)
            
            st.session_state.final_output_df = final_output_df
            st.session_state.summary_statistics_dict = summary_statistics_dict
            st.session_state.run_finished = True

        except ValidationExceptionCollector as e:
            st.header("❌ Er waren enkele problemen:", divider="red")
            for ex in e.exceptions:
                with st.error("Validatie Error"):
                    st.markdown(f"**{ex}**")
    
    if st.session_state.get("run_finished", False):
        st.write(finished_run_label)

        # Download button for Excel
        excel_output_data = convert_df_to_excel(st.session_state.final_output_df)
        st.download_button(
            label="Download Resultaten",
            data=excel_output_data,
            file_name="resultaten_schooltuinen_optimalisatie.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.divider()

        # Dropdown menu to select a schooltuin
        schooltuin = st.selectbox("Selecteer een Schooltuin", options=st.session_state.summary_statistics_dict.keys())

        if schooltuin:
            stats = st.session_state.summary_statistics_dict[schooltuin]
            if isinstance(stats, str):
                st.markdown(
                    f"<span style='color: red; font-weight: bold;'>{stats}</span>",
                    unsafe_allow_html=True
                )
            else:
                st.subheader(f"Resultaten voor {schooltuin}")

                st.write(f"**Beschikare tuintjes:** {stats['available_plots']}")
                st.write(f"**Reserve tuintjes:** {stats['reserved_plots']}")
                st.write(f"**Medewerkers:** {', '.join(stats['teachers'])}")
                st.write(f"**Aantal leerlingen ingedeeld:** {stats['assigned_students']}")
                st.write(f"**Aantal leerlingen niet ingedeeld:** {stats['unassigned_students']}")
                st.write(f"**Aantal groepen ingedeeld:** {len(stats['assigned_groups'])}")
                
                if len(stats['unassigned_groups']) > 0:
                    st.markdown(
                        f"<span style='color: red; font-weight: bold;'>Aantal groepen niet ingedeeld: {len(stats['unassigned_groups'])}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<span style='color: red; font-weight: bold;'>Groepen die niet zijn ingedeeld: {', '.join(map(str, stats['unassigned_groups']))}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write(f"**Aantal groepen niet ingedeeld:** Iedereen ingedeeld ✅")

            st.table(data=stats['schedule'])
            st.table(data=stats['current_educator_data'])
                
    
    # # Streamlit app
    # st.title("Distributie keuzes")

    # # Select location
    # location = st.selectbox("Select a location", options=list(mock_output.keys()))

    # # 
    # # et data for the selected location
    # data = mock_output[location]

    # # Prepare pie chart data
    # labels = [
    #     "1e Keus", 
    #     "2e Keus", 
    #     "3e Keus", 
    #     "4e Keus", 
    #     "Geen Oplossing"
    # ]
    # percentages = [
    #     data['percentage_groups_first_choice'], 
    #     data['percentage_groups_second_choice'], 
    #     data['percentage_groups_third_choice'], 
    #     data['percentage_groups_later_choice'], 
    #     data['percentage_groups_unallocated']
    # ]

    # # Create pie chart
    # fig, ax = plt.subplots()
    # ax.pie(
    #     percentages, 
    #     labels=labels, 
    #     autopct='%1.1f%%', 
    #     startangle=90
    # )
    # ax.set_title(f"Keuze distributie op basis van hoeveel klassen voor {location}")

    # # Display pie chart in Streamlit
    # st.pyplot(fig)

# Function to convert DataFrame to Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

if __name__ == "__main__":
    main()
