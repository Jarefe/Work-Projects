import requests
from openpyxl.reader.excel import load_workbook
from FormatReportProduction import FOR_TESTING_convert_to_JSON

url = 'http://localhost:5000/format'

data = FOR_TESTING_convert_to_JSON(load_workbook('[TESTING_EXCEL_FILE_TO_BE_PROCESSED]'))

response = requests.post(url, json=data)

if response.ok:
    download_url = response.json().get('download_url')
    print("Download URL:", download_url)
else:
    print("Error:", response.json())
