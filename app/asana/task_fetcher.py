from app.asana.asana_client import get
from app.asana.config import ASANA_PROJECT_ID, CACHE_DIR
import os
import json

TARGET_SECTIONS = ['🏃 In Progress', '👏 Done']

def fetch_tasks(force_refresh=False):

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, "asana_tasks.json")

    if not force_refresh and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    tasks = []

    # Step 1: Get all sections in the project
    sections_response = get(f"projects/{ASANA_PROJECT_ID}/sections")
    sections = sections_response.get('data', [])

    # Step 2: Filter sections of interest
    target_section_ids = {
        section['name']: section['gid']
        for section in sections
            if section['name'] in TARGET_SECTIONS
    }

    # Step 3: Fetch tasks directly from each section
    for section_name, section_gid in target_section_ids.items():
        response = get(f"sections/{section_gid}/tasks", params={
            "opt_fields": "name,completed,assignee.name,assignee.email,permalink_url"
        })

        for task in response.get('data', []):
            assignee_name = 'Unassigned'
            assignee_email = ''
            if task.get('assignee') and isinstance(task['assignee'], dict):
                assignee_name = task['assignee'].get('name', 'Unassigned')
                assignee_email = task['assignee'].get('email', '')

            task_data = {
                'id': task.get('gid'),
                'name': task.get('name', 'No name'),
                'completed': task.get('completed', False),
                'assignee': assignee_name,
                'assignee_email': assignee_email,
                'url': task.get('permalink_url', 'No URL'),
                'section': section_name
            }
            tasks.append(task_data)
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    return tasks
