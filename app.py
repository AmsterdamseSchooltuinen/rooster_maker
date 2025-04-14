import pandas as pd
import streamlit as st
import os

st.set_page_config(page_title="Rooster planner")

from src.configs.get_config import get_config
from src.extract_transform_load import run_extract_transform_load
from src.data_validations import ValidationExceptionCollector
from src.runner import run_program
from src.excel_output_formatter import create_excel_output


def main_test():
    run_extract_transform_load(None, None, None)

def main():
    config = get_config("input_data_config")
    title_label = config["labels"]["title_label"]
    sub_title = config["labels"]["sub_title"]
    instructions = config["labels"]["instructions"]
    Beschikbaarheid_educatief_medewerkers = config["labels"]["Beschikbaarheid_educatief_medewerkers"]
    Beschikbaarheid_educatief_medewerkers_tekst = config["labels"]["Beschikbaarheid_educatief_medewerkers_tekst"]
    Beschikbaarheid_groepen = config["labels"]["Beschikbaarheid_groepen"]
    Beschikbaarheid_groepen_tekst = config["labels"]["Beschikbaarheid_groepen_tekst"]
    Schooltuinen_informatie = config["labels"]["Schooltuinen_informatie"]
    Schooltuinen_informatie_tekst = config["labels"]["Schooltuinen_informatie_tekst"]
    educators_label = config["labels"]["educators_label"]
    school_label = config["labels"]["school_label"]
    garden_label = config["labels"]["garden_label"]
    run_label = config["labels"]["run_label"]
    finished_run_label = config["labels"]['finished_run_label']
    educators_template_name = config["template_file_names"]["educators_template"]
    school_template_name = config["template_file_names"]["school_template"]
    garden_template_name = config["template_file_names"]["garden_template"]
    Upload_files = config["labels"]["Upload_files"]

    # Tab title
    

    css_styles = config['Styles']['css']
    st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)

    #Title
    st.markdown(f"<div class='header'>{title_label}</div>", unsafe_allow_html=True)

    #Sub Title 
    st.markdown(f"<div class='subheader'>{sub_title}</div>", unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)

    st.markdown(f"<div class='title'>{instructions}</div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='subtitle'>{Beschikbaarheid_educatief_medewerkers}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='text'>{Beschikbaarheid_educatief_medewerkers_tekst}</div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    inputs_needed = True
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    educators_template_path = os.path.join(current_dir, "data", educators_template_name)
    school_template_path = os.path.join(current_dir, "data", school_template_name)
    garden_template_path = os.path.join(current_dir, "data", garden_template_name)



    st.download_button(
    label="Download template beschikbaarheid educatief medewerkers",
    data=open(educators_template_path, "rb").read(),
    file_name="Template_beschikbaarheid_medewerkers.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True  # Makes the button as wide as the text
    )

    st.write("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='subtitle'>{Schooltuinen_informatie}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='text'>{Schooltuinen_informatie_tekst}</div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    st.download_button(
    label="Download template schooltuinen informatie",
    data=open(garden_template_path, "rb").read(),
    file_name="Template_schooltuinen_informatie.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True  # Makes the button as wide as the text
    )

    st.write("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='subtitle'>{Beschikbaarheid_groepen}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='text'>{Beschikbaarheid_groepen_tekst}</div>", unsafe_allow_html=True)

    st.download_button(
    label="Download template beschikbaarheid groepen",
    data=open(school_template_path, "rb").read(),
    file_name="Template_beschikbaarheid_groepen.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True  # Makes the button as wide as the text
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    # with col1:
    #     st.download_button(
    #         label="Download template beschikbaarheid educatief medewerkers",
    #         data=open(educators_template_path, "rb").read(),
    #         file_name="educators_template.xlsx",
    #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #     )        
    # with col2:
    #     st.download_button(
    #     label="Download template beschikbaarheid groepen",
    #     data=open(school_template_path, "rb").read(),
    #     file_name="school_template.xlsx",
    #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #     )
    # with col3:
    #     st.download_button(
    #         label="Download template schooltuinen informatie",
    #         data=open(garden_template_path, "rb").read(),
    #         file_name="garden_template.xlsx",
    #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #     )
    
    st.divider()

    st.markdown(f"<div class='title'>{Upload_files}</div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    educators_bytes = st.file_uploader(educators_label, type = "xlsx")
    school_bytes = st.file_uploader(school_label, type = "xlsx")
    garden_bytes = st.file_uploader(garden_label, type = "xlsx")
            
    # Create buttons to download templates

    inputs_needed = not (educators_bytes and school_bytes and garden_bytes)

    if "run_clicked" not in st.session_state:
        st.session_state.run_clicked = False

    st.divider()

        
   # run_override = st.button("Run even if inputs are missing")
    run = st.button(run_label, use_container_width=True, disabled=inputs_needed)
    
    
    if run: #or run_override:
        st.session_state.run_clicked = True        
        try:
            educator_data, garden_data, school_data, timeslots, warnings = run_extract_transform_load(educators_bytes, garden_bytes, school_bytes)
            if warnings:
                st.header("⚠️ Mogelijk is er een probleem", divider="orange")
                for warning in warnings:
                    with st.warning("Misschien is er een problem?"):
                        st.markdown(f"**{warning}**")
            # RUN EVERYTHING HERE
            with st.spinner("Rooster optimaliseren..."):
                summary_statistics_dict = run_program(school_data=school_data,
                                                      educator_data=educator_data,
                                                      garden_data=garden_data,
                                                      time_slots=timeslots)

            # st.session_state.final_output_df = create_excel_output(summary_statistics_dict)

            # Set session state variables
            #st.session_state.final_output_df = convert_df_to_excel(pd.DataFrame()) # final_output_df
            st.session_state.summary_statistics_dict = summary_statistics_dict
            st.session_state.run_finished = True

        except ValidationExceptionCollector as e:
            st.header("❌ Er waren enkele problemen:", divider="red")
            for ex in e.exceptions:
                with st.error("Validatie Error"):
                    st.markdown(f"**{ex}**")
    
    if st.session_state.get("run_finished", False):
        st.success(finished_run_label)

        # Download button for Excel
        st.download_button(
            label="Download Resultaten",
            data=st.session_state.final_output_df,
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
                st.markdown(f"<div class='title'> Resultaten voor {schooltuin}</div>", unsafe_allow_html=True)

                st.write("<br>", unsafe_allow_html=True)


                st.markdown(f"<div class='text'><b>Beschikbare tuintjes:</b> {stats['available_plots']}</div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='text'><b>Reserve tuintjes:</b> {stats['reserved_plots']}</div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='text'><b>Medewerkers:</b> {', '.join(stats['teachers'])}</div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='text'><b>Aantal leerlingen ingedeeld:</b> {stats['assigned_students']}</div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='text'><b>Aantal leerlingen niet ingedeeld:</b> {stats['unassigned_students']}</div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='text'><b>Aantal groepen ingedeeld:</b> {len(stats['assigned_groups'])}</div>", unsafe_allow_html=True)

                st.write("<br>", unsafe_allow_html=True)

                if len(stats['unassigned_groups']) > 0:

                    st.markdown(f"<div class='text_red'><b>Aantal groepen niet ingedeeld:</b> {len(stats['unassigned_groups'])}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='text_red'><b>Groepen die niet zijn ingedeeld:</b> {', '.join(map(str, stats['unassigned_groups']))}</span>", unsafe_allow_html=True)

               
                

            st.write("<br>", unsafe_allow_html=True)

            st.markdown(f"<div class='text'><b>Rooster voor docenten:</b></div>", unsafe_allow_html=True)
            st.dataframe(data=stats['schedule'])
            st.write("<br>", unsafe_allow_html=True)
            st.markdown(f"<div class='text'><b>Beschikbaarheid docenten:</b></div>", unsafe_allow_html=True)
            st.dataframe(data=stats['current_educator_data'])
           
            if len(stats['unassigned_groups']) > 0:

                    #st.markdown(f"<div class='text_red'><b>Aantal groepen niet ingedeeld:</b> {len(stats['unassigned_groups'])}</span>", unsafe_allow_html=True)

                    st.write("<br>", unsafe_allow_html=True)
                    #st.markdown(f"<div class='text_red'><b>Groepen die niet zijn ingedeeld:</b> {', '.join(map(str, stats['unassigned_groups']))}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='text_red'><b>Voorkeuren groepen die niet zijn ingedeeld:</b>", unsafe_allow_html=True)

                    st.dataframe(data=stats['unassigned_groups_preference'])
            else:
                    st.markdown(f"<div class='text'><b>Aantal groepen niet ingedeeld:</b> Iedereen ingedeeld ✅</span>", unsafe_allow_html=True)

   
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



if __name__ == "__main__":
    

    with st.sidebar:
        st.markdown("<h3 style='font-size: 22px;'>📂 Kies een sectie</h3>", unsafe_allow_html=True)

        page = st.radio(
            label="",
            options=["📊 Roostermaker", "📄 Documentatie"]
        )

    if "Roostermaker" in page:
        main()

    elif "Documentatie" in page:
        st.title("📄 Documentatie")
        st.markdown("""
        Welkom bij de Schooltuinen Roostermaker!
        """)
