# import io, uuid, requests
# from flask import Flask, request, jsonify
# from FormatReportProduction import format_JSON_data
#
# app = Flask(__name__)
#
# URL = 'https://api.smartimageserve.com/upload'
#
# @app.route('/format', methods=['POST'])
# def format_testing_report():
#
#     try:
#         json_data = request.get_json()
#
#         if not json_data:
#             return jsonify({'error':'No JSON data provided'})
#
#         # Format JSON data
#         processed_workbook = format_JSON_data(json_data)
#
#         # Generate unique file name
#         file_id = str(uuid.uuid4()) # unique identifier for file
#         file_name = f'{file_id}.xlsx'
#
#         file_stream = io.BytesIO()
#
#         # Save workbook to filestream
#         try:
#             processed_workbook.save(file_stream)
#             file_stream.seek(0) # go to beginning of stream before uploading
#             print(f'File generated')
#         except Exception as e:
#             print(f'Error saving file: {e}')
#
#         # Generate URL
#
#         payload = {'folderName': 'greenteksolutions'}
#         files = [
#             ('file', (file_name, file_stream,
#             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
#         ]
#         headers = {}
#
#         # Make POST request
#         response = requests.request('POST', URL, headers=headers, data=payload, files=files)
#         response_data = response.json()
#
#         image_url = response_data.get('image_url')
#         secure_url = response_data.get('secure_url')
#         status = response_data.get('status')
#
#         output = {
#             'image_url': image_url,
#             'secure_url': secure_url,
#             'status': status
#         }
#         print(output) # for debugging purposes
#
#
#         # Return download url for front end to process
#         return jsonify({
#             'download_url': secure_url,
#             'upload_status': response.status_code,
#             'upload_message': response.text
#         })
#
#     except Exception as e:
#         return jsonify({'error':str(e)})
#
# if __name__ == '__main__':
#     app.run(debug=True)