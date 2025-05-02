import os, uuid, requests
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

@app.route('/image-download-test')
def image_test():
    payload = {'folderName': 'greenteksolutions'}
    filepath = os.getenv('TESTING_IMAGE')
    files = [
        ('image', ('imagetest.png', open(filepath, 'rb'), 'image/png'))
    ]
    headers = {}

    # Send request to external API
    response = requests.post(URL, headers=headers, data=payload, files=files)

    if response.status_code == 200: # indicates okay status
        image_url = response.json().get('image_url')
        if image_url:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:

                # Save image
                filename = 'downloaded_image.png'
                filepath = os.path.join(FILE_DIRECTORY, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_response.content)

                print('Image downloaded successfully.')

                output = {
                    'image url': image_url,
                    'secure url': response.json().get('secure_url'),
                    'status': response.json().get('status')
                }

                print(output)

                # Download file
                return send_from_directory(
                    FILE_DIRECTORY,
                    filename,
                    as_attachment=True,
                    download_name='downloaded_test_image.png',
                    mimetype='image/png'
                )
            else:
                return f'Failed to fetch image from URL: {image_response.status_code}', image_response.status_code
        else:
            return 'No image URL in response.', 400 # indicates error
    else:
        return f'API request failed: {response.status_code} - {response.text}', response.status_code


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
        response = requests.request('POST', URL, headers=headers, data=payload, files=files)

        # Block below does not currently work with smartimageserve api

        response_data = response.json()

        print(response_data)

        image_url = response_data.get('imageURL')
        secure_url = response_data.get('secureURL')
        status = response_data.get('status')

        output = {
            'image_url': image_url,
            'secure_url': secure_url,
            'status': status
        }
        print(output)

        # Return download url

        # Return download url for front end to process
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