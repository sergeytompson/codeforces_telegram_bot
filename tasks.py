from celery import Celery
from celery.schedules import crontab
import redis

from app.database_updater import CodeforcesDatabaseUpdater

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

r = redis.Redis(host='localhost', port=6379, db=0)

updater = CodeforcesDatabaseUpdater()


@app.task
def run_updater():
    updater.update()


app.conf.beat_schedule = {
    'run-task-every-hour': {
        'task': 'tasks.my_task',
        'schedule': crontab(minute=0, hour='*'),
    },
}

if __name__ == '__main__':
    app.worker_main()
