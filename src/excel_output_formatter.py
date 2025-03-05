import pandas as pd
import xlsxwriter
from io import BytesIO


def create_excel_output(stats_per_garden: dict):

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book

    # Add formats to use
    workbook_title = workbook.add_format({'bold': True, 'font_size': 24})
    black_fill = workbook.add_format({'bg_color': 'black'})
    sub_title = workbook.add_format({'bold': True, 'font_size': 14})
    c_sub_title = workbook.add_format({'bold': True, 'font_size': 14})
    c_sub_title.set_align('center')
    table_cells = workbook.add_format()
    table_cells.set_align('center')


    # Initialize worksheets
    worksheet = workbook.add_worksheet("Rooster")
    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 15, 21)
    worksheet.write("A1", "Voorgesteld schooltuinrooster per tuin", workbook_title)

    sheet_unassigned = workbook.add_worksheet("Niet ingedeelde groepen")
    sheet_unassigned.set_column(0, 0, 28)
    sheet_unassigned.set_column(1, 1, 36)
    sheet_unassigned.write("A1", "Niet ingedeelde groepen", workbook_title)
    unassigned_col_names = ["Tuin", "Som niet-ingedeelde leerlingen", "Inschrijfcode(s)"]
    sheet_unassigned.merge_range("C4:D4", "", c_sub_title)
    sheet_unassigned.write_row("A4", unassigned_col_names, c_sub_title)


    # For each garden, add the schedule
    row_n = 4
    row_n_sheet2 = 4
    for g in stats_per_garden.keys():
        # Set up divider between gardens
        worksheet.set_row(row_n, cell_format=black_fill)
        row_n += 3
        cell = "A" + str(row_n)
        # Write the name of the garden
        worksheet.write(cell, g, sub_title)
        row_n += 1
        # Write the schedule of the garden
        stats_per_garden[g]['schedule'].to_excel(writer, startrow=row_n, sheet_name="Rooster")
        row_n = row_n + len(stats_per_garden[g]['schedule']) + 2

        # Write to sheet with unassigned information
        row_n_sheet2 += 1
        cell = "A" + str(row_n_sheet2)
        g_info = [g, stats_per_garden[g]['unassigned_students']]
        g_info.extend(stats_per_garden[g]['unassigned_groups'])
        sheet_unassigned.write_row(cell, g_info, cell_format=table_cells)


    # Save and return the formatted excel dataframe
    writer.close()
    processed_data = output.getvalue()

    return processed_data

