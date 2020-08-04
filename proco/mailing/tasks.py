from celery.task import task


@task(ignore_result=True)
def send_email(backend, *args, **kwargs):
    backend.send(*args, **kwargs)
