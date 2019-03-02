import os
import redis
from rq import Worker, Queue, Connection
from app import create_app

app = create_app()
app.app_context().push()

listen = ['high', 'default', 'low']

conn = redis.from_url(os.getenv('REDISTOGO_URL'))

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()