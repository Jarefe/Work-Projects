import os, uuid, requests
from flask import Flask, request, jsonify, send_from_directory
from FormatReportProduction import format_JSON_data

app = Flask(__name__)

URL = "https://api.smartimageserve.com/upload"

# FIXME: edit to correct filepath for dash server
# TODO: remove print lines when finalizing
FILE_DIRECTORY = './static/downloads'
if not os.path.exists(FILE_DIRECTORY):
    os.makedirs(FILE_DIRECTORY, exist_ok=True)

@app.route('/format', methods=['POST'])
def format_testing_report():

    try:
        json_data = request.get_json()

        if not json_data:
            return jsonify({'error':'No JSON data provided'})

        # format JSON data
        processed_workbook = format_JSON_data(json_data)
        print('JSON data formatted')

        # generate unique file name
        file_id = str(uuid.uuid4()) # unique identifier for file
        print(f'File ID: {file_id}')
        file_name = f'{file_id}.xlsx'
        print(f'File name: {file_name}')
        file_path = os.path.join(FILE_DIRECTORY, file_name)
        print(f'File path: {file_path}')

        # save to file under filepath
        try:
            processed_workbook.save(file_path)
            print(f'File saved to: {file_path}')
        except Exception as e:
            print(f'Error saving file: {e}')
        # generate URL
        download_url = f'/static/downloads/{file_name}'
        download_url = request.url_root[:-1] + download_url

        payload = {'folderName': 'greenteksolutions'}
        files = [
            ('file', (file_name, open(file_path, 'rb'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        ]
        headers = {}

        response = requests.request("POST", URL, headers=headers, data=payload, files=files)

        print(download_url)
        print(response.text)
        print(response.status_code)

        # return download url
        return jsonify({
            'download_url':download_url,
            'upload_status': response.status_code,
            'upload_message': response.text
        })

    except Exception as e:
        return jsonify({'error':str(e)})

@app.route('/static/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(
        FILE_DIRECTORY,
        filename,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=True)