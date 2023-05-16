import os
from http import HTTPStatus
from pathlib import Path

from celery import Celery
from common.decorators import handle_exceptions
from flasgger import swag_from
from flask import Blueprint
from flask import request
from werkzeug.utils import secure_filename

blueprint = Blueprint('file_api', __name__, url_prefix='/file')
celery = Celery('tasks', broker=os.getenv('BROKER_URL'))


@blueprint.route('/upload', methods=['POST'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Upload the file to be processed',
        },
    },
})
@handle_exceptions
def upload_file():
    file = request.files['file']
    file_uuid = request.form['dzuuid']
    filename = f'{file_uuid[:8]}_{secure_filename(file.filename)}'
    save_path = Path('static', 'files', 'input', filename)

    with open(save_path, 'ab') as f:
        f.seek(int(request.form['dzchunkbyteoffset']))
        f.write(file.stream.read())

    # Check if upload is complete
    chunk_byte_offset = int(request.form['dzchunkbyteoffset'])
    chunk_size = int(request.form['dzchunksize'])
    total_size = int(request.form['dztotalfilesize'])
    if chunk_byte_offset + chunk_size >= total_size:
        job = celery.send_task('file_job.process_file', args=[filename])
        return {'message': 'File uploaded successfully', 'job_id': job.id}, HTTPStatus.OK
    return {'message': 'Chunk file uploaded successfully'}, HTTPStatus.OK


@blueprint.route('/download_file/<int:job_id>', methods=['GET'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Download the processed file by job_id provided',
        },
    },
})
@handle_exceptions
def download_file():
    return {'message': 'File downloaded successfully'}, HTTPStatus.OK


@blueprint.route('/file_status/<int:job_id>', methods=['GET'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Get the status of the file by job_id provided',
        },
    },
})
@handle_exceptions
def file_status():
    return {'message': 'File status obtained successfully'}, HTTPStatus.OK
