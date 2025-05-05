import os, requests
from dotenv import load_dotenv
from openpyxl.reader.excel import load_workbook
from FormatReportProduction import FOR_TESTING_convert_to_JSON

url = 'http://localhost:5000/format'

load_dotenv()

testing_data = FOR_TESTING_convert_to_JSON(load_workbook(os.getenv('TESTING_FILE')))

response = requests.post(url, json=testing_data)

if response.ok:
    download_url = response.json().get('download_url')
    print("Download URL:", download_url)

    # Automatically download the file
    download_response = requests.get(download_url)

    if download_response.ok:
        file_name = 'Formatted_Report.xlsx'
        with open(file_name, 'wb') as f:
            f.write(download_response.content)
        print(f"File downloaded and saved as: {file_name}")
    else:
        print(f"Failed to download the file. Status code: {download_response.status_code}")
else:
    print(f"Upload failed. Status code: {response.status_code}")
    print(response.text)
