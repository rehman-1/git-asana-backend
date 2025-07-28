import os
import subprocess
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the absolute path to the project root (where this script's parent directory is)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_PATHS = {
    "Frontend": os.path.join(PROJECT_ROOT, "Github", "x-core"),
    "ESA-Backend": os.path.join(PROJECT_ROOT, "Github", "esa-be"),
    "EOS-Backend": os.path.join(PROJECT_ROOT, "Github", "eos-backend")
}

# GitHub API configuration
GITHUB_PAT_TOKEN = os.getenv('GITHUB_PAT_TOKEN')
GITHUB_API_BASE = "https://api.github.com"

def get_github_repo_info(owner, repo):
    """Get repository information using GitHub API"""
    if not GITHUB_PAT_TOKEN:
        return {"error": "GitHub PAT token not configured"}
    
    headers = {
        "Authorization": f"token {GITHUB_PAT_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Get repository info
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        repo_response = requests.get(repo_url, headers=headers)
        
        if repo_response.status_code != 200:
            return {"error": f"Failed to fetch repo info: {repo_response.status_code}"}
        
        repo_data = repo_response.json()
        
        # Get latest commits
        commits_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
        commits_response = requests.get(commits_url, headers=headers, params={"per_page": 5})
        commits_data = commits_response.json() if commits_response.status_code == 200 else []
        
        return {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "default_branch": repo_data.get("default_branch"),
            "updated_at": repo_data.get("updated_at"),
            "pushed_at": repo_data.get("pushed_at"),
            "latest_commits": [
                {
                    "sha": commit["sha"][:7],
                    "message": commit["commit"]["message"].split('\n')[0],
                    "author": commit["commit"]["author"]["name"],
                    "date": commit["commit"]["author"]["date"]
                }
                for commit in commits_data[:3]
            ] if commits_data else []
        }
    except Exception as e:
        return {"error": str(e)}

def extract_github_info_from_remote(remote_url):
    """Extract owner and repo name from GitHub remote URL"""
    if "github.com" in remote_url:
        # Handle both SSH and HTTPS URLs
        if remote_url.startswith("git@github.com:"):
            # SSH format: git@github.com:owner/repo.git
            parts = remote_url.replace("git@github.com:", "").replace(".git", "").split("/")
        elif "github.com/" in remote_url:
            # HTTPS format: https://github.com/owner/repo.git
            parts = remote_url.split("github.com/")[1].replace(".git", "").split("/")
        else:
            return None, None
        
        if len(parts) >= 2:
            return parts[0], parts[1]
    return None, None

def reload_git_repos():
    output = {}
    for name, path in REPO_PATHS.items():
        repo_path = os.path.abspath(path)
        if not os.path.isdir(repo_path):
            output[name] = {"error": "Directory does not exist", "path_checked": repo_path}
            continue
        try:
            # Debug: Add path information
            debug_info = {
                "repo_path": repo_path,
                "path_exists": os.path.exists(repo_path),
                "is_git_repo": os.path.exists(os.path.join(repo_path, ".git"))
            }
            
            # Get remote info first
            remote_result = subprocess.run(["git", "remote", "-v"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Get current branch
            branch_result = subprocess.run(["git", "branch", "--show-current"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Perform git fetch first to get latest remote info
            fetch_result = subprocess.run(["git", "fetch"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Then perform git pull
            pull_result = subprocess.run(["git", "pull"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Get status after pull
            status_result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Get last commit info
            log_result = subprocess.run(["git", "log", "-1", "--oneline"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Extract GitHub info and get API data
            remote_lines = remote_result.stdout.strip().split('\n')
            github_info = {}
            if remote_lines:
                origin_line = next((line for line in remote_lines if line.startswith('origin') and '(fetch)' in line), None)
                if origin_line:
                    remote_url = origin_line.split()[1]
                    owner, repo = extract_github_info_from_remote(remote_url)
                    if owner and repo:
                        github_info = get_github_repo_info(owner, repo)
            
            # Combine all information
            output[name] = {
                "debug_info": debug_info,
                "remote": remote_result.stdout.strip(),
                "current_branch": branch_result.stdout.strip(),
                "fetch_result": fetch_result.stdout.strip(),
                "fetch_error": fetch_result.stderr.strip() if fetch_result.stderr.strip() else None,
                "pull_result": pull_result.stdout.strip(),
                "pull_error": pull_result.stderr.strip() if pull_result.stderr.strip() else None,
                "status": status_result.stdout.strip(),
                "last_commit": log_result.stdout.strip(),
                "github_api_data": github_info
            }
        except Exception as e:
            output[name] = {"error": str(e), "repo_path": repo_path}
    return output