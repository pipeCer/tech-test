import os
from http import HTTPStatus
from pathlib import Path

from celery import Celery
from common.decorators import handle_exceptions
from common.exceptions import InvalidParameterException
from common.exceptions import ResourceNotFoundException
from flasgger import swag_from
from flask import Blueprint
from flask import request
from flask import Response
from werkzeug.utils import secure_filename

blueprint = Blueprint('file_api', __name__, url_prefix='/api')
app = Celery(
    'tasks', broker=os.getenv('BROKER_URL'),
    backend=os.getenv('BROKER_URL'),
)


@blueprint.route('/upload_file', methods=['POST'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Upload the file to be processed',
        },
    },
})
@handle_exceptions
def upload_file():
    """
        function that upload a file to be processed. This function receives chunks of large files
        :return: Response({'message': 'File uploaded successfully',
                           'job_id': <uuid>
                           }, HTTPStatus.OK)
    """
    file = request.files['file']
    file_uuid = request.form['dzuuid']
    file_name = request.form['dzfilename'] if request.form.get(
        'dzfilename',
    ) else file.filename
    filename = f'{file_uuid[:8]}_{secure_filename(file_name)}'
    if '.csv' not in filename:
        raise InvalidParameterException('File must be a csv file')

    save_path = Path('static', 'files', 'input', filename)

    with open(save_path, 'ab') as f:
        f.seek(int(request.form['dzchunkbyteoffset']))
        f.write(file.stream.read())

    chunk_byte_offset = int(request.form['dzchunkbyteoffset'])
    chunk_size = int(request.form['dzchunksize'])
    total_size = int(request.form['dztotalfilesize'])
    if chunk_byte_offset + chunk_size >= total_size:  # if the last chunk is uploaded
        job = app.send_task('file_job.process_file', args=[filename])
        return {'message': 'File uploaded successfully', 'job_id': job.id}, HTTPStatus.OK
    return {'message': 'Chunk file uploaded successfully'}, HTTPStatus.OK


@blueprint.route('/download_file/<job_id>', methods=['GET'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Download the processed file by the job_id',
        },
    },
})
@handle_exceptions
def download_file(job_id):
    """
    function that download the processed file in chunks by job_id provided
    :param job_id:
    :return: Response(file, mimetype='application/octet-stream')
    """
    task = app.AsyncResult(job_id)
    filename = task.get()
    file_path = Path('static', 'files', 'output', filename)
    if not file_path.exists():
        raise ResourceNotFoundException('File not found')

    def generate():
        with open(file_path, 'rb') as f:
            f.seek(0)
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk

    response = Response(generate(), mimetype='application/octet-stream')
    response.headers.set(
        'Content-Disposition',
        'attachment', filename=filename,
    )
    return response


@blueprint.route('/file_status/<job_id>', methods=['GET'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Get the status of the file by the job_id',
        },
    },
})
@handle_exceptions
def file_status(job_id):
    """
    function that get the status of the file by the job_id
    :param job_id:
    :return: Response({'jod_id': <job_id>, 'job_status': <status>}, HTTPStatus.OK)
    """
    task = app.AsyncResult(job_id)
    return {'jod_id': job_id, 'job_status': task.status}, HTTPStatus.OK
