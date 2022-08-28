web: gunicorn Blog.wsgi
worker: celery -A Blog worker --without-gossip --without-mingle --without-heartbeat
