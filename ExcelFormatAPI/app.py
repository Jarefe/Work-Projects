import io
import uuid
import requests
from flask import Flask, render_template, request, jsonify, send_file
import tempfile
from ExcelFormatAPI.FormatReportProduction import format_excel_file, format_JSON_data

# Initialize Flask app
app = Flask(__name__)

# Endpoint
URL = 'https://api.smartimageserve.com/upload'
endpoint = 'https://itaderp.com/luisha/reportToJson.php'

# Store dictionary of temporarily generated file links
# Keys are filenames, and values are their corresponding file paths
TEMP_FILES = {}

def generate_download_link(workbook):
    """
    Given an excel workbook, uploads to smartimageserve api and provides download link

    :return: Jsonified string with download urls
    """
    # Generate unique file name
    file_id = str(uuid.uuid4())  # unique identifier for file
    file_name = f'{file_id}.xlsx'

    file_stream = io.BytesIO()

    # Save workbook to filestream
    try:
        workbook.save(file_stream)
        file_stream.seek(0)  # go to beginning of stream before uploading
        print(f'File generated')
    except Exception as e:
        print(f'Error saving file: {e}')

    # Generate URL
    payload = {'folderName': 'greenteksolutions'}
    files = [
        ('file', (file_name, file_stream,
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
    print(output)  # for debugging purposes

    # Return download url for front end to process
    return jsonify({
        'download_url': secure_url,
        'upload_status': response.status_code,
        'upload_message': response.text
    })

@app.route('/format-excel', methods=['POST'])
def format_excel():
    """
    Process an uploaded raw Excel file, apply formatting, and provide it as a downloadable file.

    :return: Downloadable formatted Excel file or error JSON.
    """
    file_storage = request.files['file']
    try:
        # Process the uploaded file and return a formatted Excel workbook
        workbook = format_excel_file(file_storage)

        # Save the workbook to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        workbook.save(temp_file.name)

        # Save the file path in the TEMP_FILES dictionary
        filename = temp_file.name.split('/')[-1]
        TEMP_FILES[filename] = temp_file.name

        # Return the file as a downloadable attachment
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name="formatted_excel.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        # Return a JSON error message in case of failure
        return jsonify({'error': str(e)}), 500

@app.route('/fetch-data-debugging')
def fetch_data():
    payload = {
        "vendor": 6467,
        "filter": "pos",
        "categories": ['desktop', 'laptop'],
        "types": ["inventory"],
        "pos": 13093
    }

    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)  # return the raw JSON for now
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}"}), 500

@app.route('/')
def home():
    """
    Serve the homepage of the app, which provides links to pricing, Excel formatting, and eBay tracking.

    :return: Rendered homepage template (HTML).
    """
    return render_template('index.html')

@app.route('/format')
def format_data():
    try:
        # FIXME: make payload dynamic by obtaining data from statistics form

        payload = {
            "vendor": 754,
            "filter": "pos",
            "categories": ['desktop', 'laptop'],
            "types": ["inventory"],
            "pos": 13257
        }

        # Send POST request to endpoint
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()

        # Format JSON data
        processed_workbook = format_JSON_data(data)

        output = generate_download_link(processed_workbook)
        print(output)  # for debugging purposes

        # Return download url for front end to process
        return output

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

if __name__ == '__main__':
    """
    Run the Flask application in debug mode.
    """
    app.run(debug=True)