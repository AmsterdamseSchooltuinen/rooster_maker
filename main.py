import streamlit as st
from src.configs.get_config import get_config
from src.streamlit import ValidationException
from src.extract_transform_load import run_extract_transform_load
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def main():
    config = get_config("visual_config")
    title_label = config["labels"]["title_label"]
    subheader_label = config["labels"]["subheader_label"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]
    run_label = config["labels"]["run_label"]
    finished_run_label = config["labels"]['finished_run_label']
    
    st.title(title_label)
    st.subheader(subheader_label)
    inputs_needed = True

    educators_bytes = st.file_uploader(educators_label)
    school_bytes = st.file_uploader(school_label)
    garden_bytes = st.file_uploader(garden_label)

    inputs_needed = not (educators_bytes and school_bytes and garden_bytes)

    if "run_clicked" not in st.session_state:
        st.session_state.run_clicked = False
        
    run_override = st.button("Run even if inputs are missing")
    run = st.button(run_label, use_container_width=True, disabled=inputs_needed)
    
    # run = st.button(run_label, use_container_width=True, disabled=inputs_needed)
    st.divider()

    if run or run_override:
        st.session_state.run_clicked = True        
        try:
            # run_extract_transform_load(educators_bytes, garden_bytes, school_bytes)
            
            # RUN EVERYTHING HERE 
            
            final_output_df = pd.DataFrame(['test',2,3])
            summary_statistics_dict = {'Kalff Schooltuin': {
                'available_plots': 200,
                'reserve_plots': 20,
                'teachers': ['Nils', 'Floris'],
                'assigned_students': 180,
                'assigned_groups': 16,
                'unassigned_groups': 2,
                'unassigned_group_names': ['school a group a', 'school b group b'],
                'percentage_groups_first_choice': 70,
                'percentage_groups_second_choice': 12,
                'percentage_groups_third_choice': 8, 
                'percentage_groups_later_choice': 7,
                'percentage_groups_unallocated': 3
            }, 'Aemstel Schooltuin': {
            'available_plots': 100,
            'reserve_plots': 20,
            'teachers': ['Jacob', 'Amelia'],
            'assigned_students': 100,
            'assigned_groups': 16,
            'unassigned_groups': 2,
            'unassigned_group_names': ['school a group a', 'school b group b'],
            'percentage_groups_first_choice': 60,
            'percentage_groups_second_choice': 22,
            'percentage_groups_third_choice': 7, 
            'percentage_groups_later_choice': 8,
            'percentage_groups_unallocated': 3
            }}
            
            st.session_state.final_output_df = final_output_df
            st.session_state.summary_statistics_dict = summary_statistics_dict
            st.session_state.run_finished = True

        except ValidationException as e:
            st.error(f"{e.input_name}: {e}")
        except FileNotFoundError as e:
            st.error(f"File not found: {e}??")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
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
            st.subheader(f"Statistics for {schooltuin}")

            st.write(f"**Beschikare tuintjes:** {stats['available_plots']}")
            st.write(f"**Reserve tuintjes:** {stats['reserve_plots']}")
            st.write(f"**Aantal medewerkers:** {', '.join(stats['teachers'])}")
            st.write(f"**Aantal leerlingen ingedeeld:** {stats['assigned_students']}")
            st.write(f"**Aantal groepen ingedeeld:** {stats['assigned_groups']}")
            st.write(f"**Aantal groepen niet ingedeeld:** {stats['unassigned_groups']}")
            st.write(f"**Groepen die niet zijn ingedeeld:** {', '.join(stats['unassigned_group_names'])}")
    
    # mock_output = {
    #     'Alle tuinen': {
    #         'available_plots': 300,
    #         'reserve_plots': 40,
    #         'teachers': ['Nils', 'Floris', 'Jacob', 'Amelia'],
    #         'assigned_students': 280,
    #         'assigned_groups': 16,
    #         'unassigned_groups': 2,
    #         'unassigned_group_names': ['school a group a', 'school b group b'],
    #         'percentage_groups_first_choice': 60,
    #         'percentage_groups_second_choice': 10,
    #         'percentage_groups_third_choice': 10, 
    #         'percentage_groups_later_choice': 10,
    #         'percentage_groups_unallocated': 10
    #     },
    #     'Kalff Schooltuin': {
    #         'available_plots': 200,
    #         'reserve_plots': 20,
    #         'teachers': ['Nils', 'Floris'],
    #         'assigned_students': 180,
    #         'assigned_groups': 16,
    #         'unassigned_groups': 2,
    #         'unassigned_group_names': ['school a group a', 'school b group b'],
    #         'percentage_groups_first_choice': 70,
    #         'percentage_groups_second_choice': 12,
    #         'percentage_groups_third_choice': 8, 
    #         'percentage_groups_later_choice': 7,
    #         'percentage_groups_unallocated': 3
    #     },
    #     'Aemstel Schooltuin': {
    #         'available_plots': 100,
    #         'reserve_plots': 20,
    #         'teachers': ['Jacob', 'Amelia'],
    #         'assigned_students': 100,
    #         'assigned_groups': 16,
    #         'unassigned_groups': 2,
    #         'unassigned_group_names': ['school a group a', 'school b group b'],
    #         'percentage_groups_first_choice': 60,
    #         'percentage_groups_second_choice': 22,
    #         'percentage_groups_third_choice': 7, 
    #         'percentage_groups_later_choice': 8,
    #         'percentage_groups_unallocated': 3
    #     }
    # }
    
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