from flask import Flask, render_template, request, jsonify, send_file
import tempfile
from ExcelFormatAPI.FormatReportProduction import format_excel_file

# Initialize Flask app
app = Flask(__name__)

# Store dictionary of temporarily generated file links
# Keys are filenames, and values are their corresponding file paths
TEMP_FILES = {}


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


@app.route('/')
def home():
    """
    Serve the homepage of the app, which provides links to pricing, Excel formatting, and eBay tracking.

    :return: Rendered homepage template (HTML).
    """
    return render_template('index.html')

if __name__ == '__main__':
    """
    Run the Flask application in debug mode.
    """
    app.run(debug=True)