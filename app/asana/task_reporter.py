
from app.asana.task_fetcher import fetch_tasks
from collections import defaultdict
import pandas as pd
from app.services.git_reporter import generate_git_report
from app.utils.openai_client import analyze_commit
from datetime import date


def summarize_asana_tasks():
    tasks = fetch_tasks()
    summary = {
        "total_in_progress": 0,
        "total_done": 0,
        "developers": defaultdict(lambda: {"in_progress": [], "done": []})
    }

    for task in tasks:
        section = task['section'].lower()
        dev = task['assignee']

        if 'in progress' in section and (not task['completed'] and 'done' not in section):
            summary["total_in_progress"] += 1
            summary["developers"][dev]["in_progress"].append(task)
        elif task['completed'] or 'done' in section:
            summary["total_done"] += 1
            summary["developers"][dev]["done"].append(task)

    return summary

def estimate_time_per_task(start_date: date, end_date: date):
    tasks = fetch_tasks()
    time_summary = []

    # Get Git Commits
    all_commits = generate_git_report(start_date.isoformat(), end_date.isoformat(), use_cache=True)



    for task in tasks:
        task_name = str(task.get("name"))
        task_id = str(task.get("id"))
        # related_commits = [c for c in all_commits if task_name in c['message']]
        related_commits = [c for c in all_commits if task_id in c['message'] or task['name'].split(":")[0] in c['message']]


        if not related_commits:
            print(f"No commits found for task: {task_name}")
            continue

        df = pd.DataFrame(related_commits)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df.sort_values(by='datetime', inplace=True)

        first = df.iloc[0]['datetime']
        last = df.iloc[-1]['datetime']
        minutes_spent = int((last - first).total_seconds() / 60)

        total_added = df['added'].sum()
        total_deleted = df['deleted'].sum()

        diff_summary = "\n".join([f"- {row['message']}" for _, row in df.iterrows()])
        try:
            analysis = analyze_commit(diff_summary, task['name'])
        except Exception as e:
            analysis = f"Error analyzing commit: {e}"

        time_summary.append({
            "task_id": task["id"],
            "task_name": task['name'],
            "assignee": task['assignee'],
            "section": task['section'],
            "url": task['url'],
            "time_spent_minutes": minutes_spent,
            "commit_count": len(df),
            "first_commit": str(first),
            "last_commit": str(last),
            "lines_added": int(total_added),
            "lines_deleted": int(total_deleted),
            "analysis": analysis,
            "commits": df.to_dict(orient="records")
        })

    return time_summary


def developer_summary(start_date: date, end_date: date):
    detailed_tasks = estimate_time_per_task(start_date, end_date)
    summary_by_dev = defaultdict(lambda: {"tasks": [], "total_minutes": 0})

    for task in detailed_tasks:
        dev = task["assignee"]
        summary_by_dev[dev]["tasks"].append(task)
        summary_by_dev[dev]["total_minutes"] += task["time_spent_minutes"]

    return summary_by_dev