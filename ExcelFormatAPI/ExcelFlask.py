import os, uuid, requests
from openpyxl import Workbook
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from FormatReportProduction import format_JSON_data

app = Flask(__name__)

URL = 'https://api.smartimageserve.com/upload'

load_dotenv()

# FIXME: edit to correct filepath for dash server
FILE_DIRECTORY = './static/downloads'
if not os.path.exists(FILE_DIRECTORY):
    os.makedirs(FILE_DIRECTORY, exist_ok=True)


@app.route('/format', methods=['POST'])
def format_testing_report():

    try:
        json_data = request.get_json()

        if not json_data:
            return jsonify({'error':'No JSON data provided'})

        # Format JSON data
        processed_workbook = format_JSON_data(json_data)

        # Generate unique file name
        file_id = str(uuid.uuid4()) # unique identifier for file
        file_name = f'{file_id}.xlsx'
        file_path = os.path.join(FILE_DIRECTORY, file_name)

        # Save to file under filepath
        try:
            processed_workbook.save(file_path)
            print(f'File saved to: {file_path}')
        except Exception as e:
            print(f'Error saving file: {e}')

        # Generate URL
        download_url = f'{request.url_root[:-1]}/static/downloads/{file_name}'

        payload = {'folderName': 'greenteksolutions'}
        files = [
            ('file', (file_name, open(file_path, 'rb'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        ]
        headers = {}

        # Make POST request
        response = requests.request('POST', URL, headers=headers, data=payload, files=files)
        response_data = response.json()

        image_url = response_data.get('image_url')
        secure_url = response_data.get('secure_url')
        status = response_data.get('status')

        output = {
            'image_url': image_url,
            'secure_url': secure_url,
            'status': status
        }
        print(output) # for debugging purposes

        # Return download url for front end to process
        return jsonify({
            'download_url': secure_url,
            'upload_status': response.status_code,
            'upload_message': response.text
        })

    except Exception as e:
        return jsonify({'error':str(e)})

if __name__ == '__main__':
    app.run(debug=True)