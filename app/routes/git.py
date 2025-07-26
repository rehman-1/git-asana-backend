
from fastapi import APIRouter, Query
from app.services.git_reporter import generate_git_report
from app.services.git_reloader import reload_git_repos
from typing import List
from datetime import date

router = APIRouter(prefix="/git", tags=["Git"])

@router.post("/report")
def generate_report(start_date: date = Query(...), end_date: date = Query(...)):
    data = generate_git_report(start_date.isoformat(), end_date.isoformat())
    return {"commits": data, "count": len(data)}

@router.post("/reload")
def reload_repos():
    result = reload_git_repos()
    return {"status": "ok", "details": result}


