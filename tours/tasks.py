# tours/tasks.py
from celery import shared_task

@shared_task
def test_hello(name):
    print(f"Hello, {name}!")
    return f"Hello, {name}!"