from config import REDISTOGO_URL
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

conn = redis.from_url(REDISTOGO_URL)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
