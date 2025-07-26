import os
import subprocess
from datetime import datetime
import pandas as pd
import re
from dotenv import load_dotenv
import json
from app.asana.config import CACHE_DIR


# Load environment variables
load_dotenv()

# Get repository paths from environment variables
REPO_PATHS = {
    "Frontend": os.getenv("FRONTEND_REPO_PATH", "./Github/x-core"),
    "ESA-Backend": os.getenv("ESA_REPO_PATH", "./Github/esa-be"),
    "EOS-Backend": os.getenv("EOS_REPO_PATH", "./Github/eos-backend")
}

# Base URLs for the repositories
REPO_URLS = {
    "Frontend": "https://github.com/XAION-Inc/x-core",
    "ESA-Backend": "https://github.com/XAION-Inc/esa-be",
    "EOS-Backend": "https://github.com/XAION-Inc/eos-backend"
}
DEVELOPERS = {
    "ksh": {"en": "Kim Seong-hoon", "kr": "김성훈", "git_id": "@ksh"},
    "mjtak": {"en": "Tak Min-ju", "kr": "탁민주", "git_id": "@mjtak"},
    "KCH": {"en": "Kim Chang-ho", "kr": "김창호", "git_id": "@KCH"},
    "ekkim": {"en": "Kim Eung-guk", "kr": "김응국", "git_id": "@ekkim"},
    "gsyang": {"en": "Yang Jin Sheng", "kr": "양금성", "git_id": "@gsyang"},
    "bhsong": {"en": "Song Bin-ho", "kr": "송빈호", "git_id": "@bhsong"},
    "htseo": {"en": "Seo Hyuk-taek", "kr": "서혁택", "git_id": "@htseo"},
    "jmlim": {"en": "Lim Jeong-min", "kr": "임정민", "git_id": "@xaion-jmlim"},
    "chokim": {"en": "Kim Chang-ho", "kr": "김창호", "git_id": "@xaion-chokim"},
    "intra.infra": {"en": "Administrator account", "kr": "관리자 계정", "git_id": "@xaion-infra"},
    "sghong": {"en": "Hong Seung-gi", "kr": "홍승기", "git_id": "@xaion-sghong"},
    "kspark": {"en": "Park Kyung-seok", "kr": "박경석", "git_id": "@xaion-kspark"},
    "github-actions[bot]": {"en": "github-actions[bot]", "kr": "", "git_id": "@github-actions[bot]"},
    "jyunkim": {"en": "Kim Jong-yoon", "kr": "김종윤", "git_id": "@xaion-jykim"},
    "saokhueyang": {"en": "sahayana", "kr": "", "git_id": "@Sahayana"},
    "takminjoo": {"en": "minju.tak", "kr": "", "git_id": "@min-99"},
}
KNOWN_USERNAMES = set(DEVELOPERS.keys())

def run_git_log(repo_name, repo_path, since, until):
    result = subprocess.run(
        ['git', 'log', '--all', f'--since={since}', f'--until={until}',
         '--pretty=format:%H|%ae|%ct|%s'],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw_log = result.stdout.decode('utf-8', errors='replace').strip()
    if not raw_log:
        return []

    commits = []
    for line in raw_log.split('\n'):
        if '|' not in line:
            continue
        try:
            commit_hash, author_email, timestamp, message = line.split('|', 3)
        except ValueError:
            continue
        username = author_email.split('@')[0]
        display_dev = f"{username} (unknown)"
        if username in KNOWN_USERNAMES:
            dev = DEVELOPERS[username]
            display_dev = f"{dev['en']} ({username}, {dev['kr']}, {dev['git_id']})"

        # Get code changes
        show_result = subprocess.run(
            ['git', 'show', '--numstat', '--pretty=format:', commit_hash],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        added, deleted, files = 0, 0, 0
        for l in show_result.stdout.decode('utf-8').split('\n'):
            if re.match(r'^\d+\s+\d+', l):
                a, d = l.split('\t')[:2]
                added += int(a)
                deleted += int(d)
                files += 1

        commits.append({
            "repo": repo_name,
            "developer": display_dev,
            "timestamp": int(timestamp),
            "message": message,
            "added": added,
            "deleted": deleted,
            "files": files,
            "link": f"{REPO_URLS[repo_name]}/commit/{commit_hash}"
        })
    return commits

def generate_git_report(start_date: str, end_date: str, use_cache: bool = False):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"git_report_{start_date}_{end_date}.json")

    if use_cache and os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # Check if file is not empty
                    return json.loads(content)
                else:
                    # File is empty, remove it and continue with fresh data
                    os.remove(cache_file)
        except (json.JSONDecodeError, IOError) as e:
            # Cache file is corrupted, remove it and continue with fresh data
            print(f"Cache file corrupted, removing: {cache_file}")
            if os.path.exists(cache_file):
                os.remove(cache_file)

    since = f"{start_date}T00:00:00"
    until = f"{end_date}T23:59:59"

    all_commits = []
    for repo_name, repo_path in REPO_PATHS.items():
        repo_abs_path = os.path.abspath(repo_path)
        if not os.path.isdir(repo_abs_path):
            continue
        all_commits += run_git_log(repo_name, repo_abs_path, since, until)

    df = pd.DataFrame(all_commits)
    if df.empty:
        return []

    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df.sort_values(by="datetime", ascending=False, inplace=True)
    
    # Convert back to list of dictionaries for consistent return format
    processed_commits = df.to_dict(orient="records")

    # Cache the processed and sorted data
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(processed_commits, f, indent=2, default=str)

    return processed_commits