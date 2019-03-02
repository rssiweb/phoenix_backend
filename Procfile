web: flask db upgrade; gunicorn run:app
worker: rq worker -u $REDISTOGO_URL high default low