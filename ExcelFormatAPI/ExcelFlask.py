import io
from flask import Flask, request, jsonify, send_file
from FormatReportProduction import format_JSON_data

app = Flask(__name__)

@app.route('/format', methods=['POST'])
def format_testing_report():

    try:
        json_data = request.get_json()

        if not json_data:
            return jsonify({'error':'No JSON data provided'})

        # format JSON data
        processed_workbook = format_JSON_data(json_data)

        # save the processed workbook to a new in memory object
        output = io.BytesIO()
        processed_workbook.save(output)

        # go to the beginning of the BytesIO object before sending to client
        output.seek(0)

        formatted_filename = 'Formatted_Report.xlsx' # edit to append to filename output by dash

        # export as excel file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=formatted_filename)

    except Exception as e:
        return jsonify({'error':str(e)})

if __name__ == '__main__':
    app.run(debug=True)