import requests
from openpyxl.reader.excel import load_workbook
from FormatReportProduction import FOR_TESTING_convert_to_JSON

url = 'http://localhost:5000/format'

data = FOR_TESTING_convert_to_JSON(load_workbook('[TESTING_EXCEL_FILE_TO_BE_PROCESSED]'))

response = requests.post(url, json=data)

# save the returned excel file
if response.ok:
    with open('Formatted_Report.xlsx', 'wb') as f:
        f.write(response.content)
    print("Excel file saved as 'Formatted_Report.xlsx'")
else:
    print("Error:", response.json())
