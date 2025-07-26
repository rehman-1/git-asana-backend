from datetime import date
from app.asana.task_reporter import summarize_asana_tasks
from app.services.git_reporter import generate_git_report
from collections import defaultdict
from typing import List


def developer_performance(start_date: date, end_date: date):
    # Get Asana Task Summary
    asana_summary = summarize_asana_tasks()

    # Get Git Commits
    git_commits = generate_git_report(start_date.isoformat(), end_date.isoformat())

    # Developer Performance Mapping
    report = defaultdict(lambda: {
        "in_progress_tasks": [],
        "done_tasks": [],
        "commit_count": 0,
        "lines_added": 0,
        "lines_deleted": 0,
        "files_changed": 0
    })

    for dev, task_data in asana_summary['developers'].items():
        report[dev]["in_progress_tasks"] = task_data["in_progress"]
        report[dev]["done_tasks"] = task_data["done"]

    for commit in git_commits:
        dev_name = commit.get("developer", "Unknown")
        report[dev_name]["commit_count"] += 1
        report[dev_name]["lines_added"] += commit.get("added", 0)
        report[dev_name]["lines_deleted"] += commit.get("deleted", 0)
        report[dev_name]["files_changed"] += commit.get("files", 0)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "developer_summary": report
    }