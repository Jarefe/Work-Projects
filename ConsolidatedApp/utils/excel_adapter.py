import tempfile
from ExcelFormatAPI.FormatReportProduction import format_excel_file

def handle_excel_formatting(file_storage):

    # Save to temp file
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    file_storage.save(temp_input.name)

    # Call formatter
    output_path = format_excel_file(temp_input.name)

    return output_path