import io, os
from flask import Flask, request, jsonify, send_file
from openpyxl import load_workbook # remove when done testing JSON function
from FormatReportProduction import temporary_convert_to_JSON, format_JSON_data

app = Flask(__name__)

@app.route('/')
def index():
    return """<title>Upload the excel file to be formatted</title>
    <h1>Upload excel file</h1>
    <form action="/format" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>"""

@app.route('/format', methods=['POST'])
def format_testing_report():

    # TODO: accept JSON data as input


    if 'file' not in request.files:
        return jsonify({'error':'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error':'No selected file'})

    try:
        # TODO: change input type to list/dictionary instead of file object
        # json_data = request.get_json()
        #
        # if not json_data:
        #     return jsonify({'error':'No JSON data provided'})

        # get original filename
        original_filename = file.filename

        # create in memory file object to pass to function
        in_memory_file = io.BytesIO(file.read())

        # format in memory file object
        # FIXME: remove temporary_convert_to_JSON when done with testing
        processed_workbook = format_JSON_data(temporary_convert_to_JSON(load_workbook(in_memory_file)))

        # save the processed workbook to a new in memory object
        output = io.BytesIO()
        processed_workbook.save(output)

        # go to the beginning of in memory file before sending to client
        output.seek(0)

        # append "formatted report" to original filename
        filename, file_extension = os.path.splitext(original_filename)
        formatted_filename = f'{filename}_Formatted{file_extension}'

        # export as excel file
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=formatted_filename)

    except Exception as e:
        return jsonify({'error':str(e)})

if __name__ == '__main__':
    app.run(debug=True)