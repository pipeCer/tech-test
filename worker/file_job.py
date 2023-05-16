import csv
import datetime
import os

from celery import Celery

app = Celery(
    'tasks', broker=os.environ.get(
        'BROKER_URL', 'redis://localhost:6379/0',
    ),
)


@app.task
def process_file(file_name):
    """
        function that process a file and store the result in a new file in the output folder
        :param file_name:
    """
    total_plays = {}
    input_file_path = os.path.join('server/static/files/input/' + file_name)
    with open(input_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            song, date, num_plays = row
            total_plays.setdefault(song, {})
            total_plays[song].setdefault(date, 0)
            total_plays[song][date] += int(num_plays)

    input_filename = file_name.split('.')[0]
    output_filename = f'{input_filename}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
    output_file_path = os.path.join(
        'server/static/files/output/' + output_filename,
    )
    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Song', 'Date', 'Total Number of Plays for Date'])
        for song in total_plays:
            for date in sorted(total_plays[song]):
                total_num_plays = total_plays[song][date]
                writer.writerow([song, date, total_num_plays])
