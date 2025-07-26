from fastapi import APIRouter, Query
from app.services.get_analytics import developer_performance
from typing import List
from datetime import date

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/")
def get_developer_performance(start_date: date = Query(...), end_date: date = Query(...)):
    return developer_performance(start_date, end_date)
