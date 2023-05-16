import os
import time
import uuid

import requests

chunk_size = 1024 * 1024
url = os.getenv('API_URL', 'http://localhost:8000/api')


def upload_file_by_chunks(file_path):
    file_uuid = uuid.uuid4()
    total_file_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f:
        f.seek(0)
        while True:
            file_chunk = f.read(chunk_size)
            data = {
                'dzuuid': file_uuid,
                'dzchunkbyteoffset': f.tell() - chunk_size,
                'dzchunksize': chunk_size,
                'dztotalfilesize': total_file_size,
                'dzfilename': f.name,
            }
            resp = requests.post(
                f'{url}/upload_file',
                files={
                    'file': file_chunk,
                },
                data=data,
            )
            resp = resp.json()
            # console output % of file uploaded
            print(
                f'\rUploading file: {round((f.tell() / total_file_size) * 100, 2)}%', end='',
            )
            if 'job_id' in resp:
                job_id = resp['job_id']
                print()
                break
    return job_id


def get_job_status(task_id):
    resp = requests.get(f'{url}/file_status/{task_id}')
    return resp.json()


def download_file(task_id):
    resp = requests.get(f'{url}/download_file/{task_id}', stream=True)
    output_file_name = 'sample_downloaded_file.csv'
    if resp.status_code == 200:
        with open(output_file_name, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                f.write(chunk)
    else:
        print('Error:', resp.status_code)


if __name__ == '__main__':
    job_id = upload_file_by_chunks('sample_input_file.csv')
    print(f'Job ID: {job_id}')
    while True:
        job_status = get_job_status(job_id)
        print(f'Job Status: {job_status["job_status"]}')
        if job_status['job_status'] == 'SUCCESS':
            break
        time.sleep(1)
    download_file(job_id)
    print('File downloaded successfully')
