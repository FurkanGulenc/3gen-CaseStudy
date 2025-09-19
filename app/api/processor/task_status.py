from fastapi import APIRouter
from app.api.processor.tasks import celery_app

router = APIRouter()

@router.get("/processor/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task_result.status,   # PENDING, STARTED, SUCCESS, FAILURE
        "result": str(task_result.result) if task_result.result else None,
    }
