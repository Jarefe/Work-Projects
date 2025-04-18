import io, os
from flask import Flask, request, jsonify, send_file
from FormatReportProduction import format_testing_report

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
def upload():
    if 'file' not in request.files:
        return jsonify({'error':'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error':'No selected file'})

    try:
        # get original filename
        original_filename = file.filename

        # create in memory file object to pass to function
        in_memory_file = io.BytesIO(file.read())

        # format in memory file object
        processed_workbook = format_testing_report(in_memory_file)

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