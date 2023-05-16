# Tech test

Flask API to upload, process and download large csv files.

# Getting started

## Clone the repository

To clone this repository:

Open your favorite terminal and navigate to the folder where you want to clone the project. Copy and paste the following
command:

```bash
git clone https://github.com/pipeCer/tech-test.git flask-api
cd flask-api
```

## Open the project

Use your preferred IDE to open the project.

* Go to `File` > `Open`
* Navigate to the folder where you cloned the project and select the folder `flask-api`
* Click on `Open`
* Wait for the IDE to load the project

## Project structure

The project is structured as follows:

```
├───server
│   ├───common
│   │   └───decorators.py
│   │   └───exceptions.py
│   ├───routes
│   │   └───file_route.py
│   ├───static
│   │   └───files
│   │       ├───input
│   │       └───output
│   ├───Dockerfile
│   ├───requirements.txt
│   ├───main.py
├───worker
│   ├───file_job.py
│   ├───Dockerfile
│   ├───requirements.txt
├───.pre-commit-config.yaml
├───docker-compose.yml
└───test_api.py
```

### Structure description

* `server`: Contains the flask API
    * `common`: Contains the decorators and exceptions used in the API
    * `routes`: Contains the routes of the API
    * `static`: Contains the files that are uploaded and processed
* `worker`: Contains the worker that processes the files
* `test_api.py`: Contains the test for the API
* `sample_input_file.csv`: Contains a sample file to test the API
* `docker-compose.yml`: Contains the configuration to run the containers

## Pre-requisites

* `Docker` && `Docker-compose`
* `Python 3`
* `requests` library installed in your machine in case you want to run the `test_api.py` file

## Run the project

To run the project, open your favorite terminal and navigate to the folder where you cloned the project. Run the
following command:

```bash
docker-compose up
```

* Wait for the containers to be running
* Once the containers are running, open your browser and go to `http://localhost:8000/`
* Optional:
    * Open a new terminal and navigate to the folder where you cloned the project
    * Download the sample file to test the API:
      [sample_input_file.csv](https://drive.google.com/file/d/13dfOxPLTZxyY211VEqGcxSYUeq1Hhwcl/view?usp=share_link)
    * If the path of the file is different from the current folder, move it to the current folder.
    * Run the following command to test the API:
  ```bash
    python test_api.py
    ```
    * Check the input file in the `server/static/files/input` folder
    * Check the output file in the `server/static/files/output` folder
    * As part of the test, the output file is downloaded in the current folder with the
      name `sample_downloaded_file.csv`

## API documentation

The API has the following endpoints:

* `/api/upload_file`: POST method. Uploads a file to the server. The file must be a csv file and must be sent as chunks.
    * Request body: `file` (csv file)
        - data:
      ```json
          {
            "dzuuid": <file_uuid>,
            "dzchunkbyteoffset": <chunk_offset>,
            "dzchunksize": <chunk_size>,
            "dztotalfilesize": <total_file_size>,
            "dzfilename": <file_name>
          }
      ```
        - Response:
      ```json
              {
                "message": "File uploaded successfully",
                "job_id": <job_uuid>
              }
      ```
* `/api/file_status/<job_id>`: GET method to retrieve the current job status.
    * Response:
  ```json
        {
          "job_status": "SUCCESS",
          "jod_id": <job_uuid>
        }
  ```

* `/api/download_file/<job_id>`: GET method to download the processed file.
    * Response: The file is downloaded in the browser by chunks.

  **Note**: you must implement a download manager in the front-end to download the file and join the chunks.

# Test questions

## 1. Large CSV Processing

### Explanation

The `file_job.py` script processes a CSV file containing data about song plays and outputs a new CSV file with the total
number of plays per song and date. It does this by reading the input file line by line, parsing the data, and
incrementing counters in a nested dictionary for each song and date. Then it writes the output file by iterating over
the nested dictionary and writing each row with the song name, date, and total number of plays.

The script uses the `built-in` csv module to read and write CSV files, which is suitable for this task because it
efficiently handles large files without loading them entirely into memory. The `csv.reader` and `csv.writer` objects
allow for easy iteration over the input and output files, respectively, without the need for manual parsing or
formatting.

The computational complexity of this processing is `O(n)`, where n is the number of rows in the input file. This is
because the script reads and processes each row once, and the nested dictionary operations are constant time.

### Additional notes

To improve the performance of this script for even larger input files, it could be modified to use a parallel processing
library.

## 2. API and Asynchronous Task Processing

### Explanation

The API was built with Flask framework. It consists of 3 endpoints:
* `/api/upload_file`: POST method. Uploads a file to the server. When the file is uploaded, it automatically sends the
job to the worker to be processed.
* `/api/file_status/<job_id>`: GET method to retrieve the current job status.
* `/api/download_file/<job_id>`: GET method to download the processed file if the status of the job is `SUCCESS`.

Besides, the `file_job.py` script was refactored to implement Celery + redis to manage the async task.

So, the recommended steps are:

1. Upload a file to the server using the `/api/upload_file` endpoint.
2. Check the status of the job using the `/api/file_status/<job_id>` endpoint.
3. If the status of the job is `SUCCESS`, download the file using the `/api/download_file/<job_id>` endpoint.
