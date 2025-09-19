# run_task_locally.py
import asyncio
from app.api.processor.tasks import _process_project

if __name__ == "__main__":
    # Burada istediğin project_id'yi ver (ör: 4)
    _process_project(5)
