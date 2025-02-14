from celery import Celery

# startup: poetry run celery -A ori_v2 worker -l INFO
app = Celery(
    'ori_v2',
    broker='pyamqp://root:mysecretpassword@localhost//',
    backend="redis://localhost:6379/0",
    include=[
        'ori_v2.notubiz.tasks',
    ]
)

app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()