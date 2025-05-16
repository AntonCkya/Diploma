import uuid
import asyncio
from datetime import datetime

TTL = 30

class Task:
    status: str
    updated_at: datetime

    def __init__(self, status: str, updated_at: datetime):
        self.status = status
        self.updated_at = updated_at

tasks = {}
def make_task(status: str):
    task = Task(status=status, updated_at=datetime.now())
    id = str(uuid.uuid4())
    tasks[id] = task
    return id

def change_task_status(task_id, status):
    task = tasks.get(task_id)
    if task:
        task.status = status
        task.updated_at = datetime.now()
        return task_id
    else:
        return None

def get_task(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return None
    return task

def remove_tasks():
    for task_id, task in tasks.items():
        if datetime.now() - task.updated_at > datetime.timedelta(minutes=TTL):
            tasks.pop(task_id)

async def cron_remove_tasks():
    while True:
        await asyncio.sleep(TTL * 60)
        remove_tasks()
