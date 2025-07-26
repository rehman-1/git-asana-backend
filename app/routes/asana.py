from fastapi import APIRouter
from app.asana.task_reporter import summarize_asana_tasks, estimate_time_per_task, developer_summary, fetch_tasks
from datetime import date

router = APIRouter(prefix="/asana", tags=["Asana"])

@router.get("/summary")
def get_asana_summary():
    return summarize_asana_tasks()

@router.post("/efforts")
def get_asana_efforts(start_date: date, end_date: date):
    return estimate_time_per_task(start_date, end_date)


@router.post("/developer_summary")
def get_developer_summary(start_date: date, end_date: date):
    return developer_summary(start_date, end_date)

@router.post("/reload")
def reload_asana_cache():
    tasks = fetch_tasks(force_refresh=True)
    return {"status": "reloaded", "tasks_cached": len(tasks)}