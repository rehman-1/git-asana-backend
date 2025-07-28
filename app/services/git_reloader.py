import os
import subprocess

# Get the absolute path to the project root (where this script's parent directory is)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_PATHS = {
    "Frontend": os.path.join(PROJECT_ROOT, "Github", "x-core"),
    "ESA-Backend": os.path.join(PROJECT_ROOT, "Github", "esa-be"),
    "EOS-Backend": os.path.join(PROJECT_ROOT, "Github", "eos-backend")
}

def reload_git_repos():
    output = {}
    for name, path in REPO_PATHS.items():
        repo_path = os.path.abspath(path)
        if not os.path.isdir(repo_path):
            output[name] = "Directory does not exist"
            continue
        try:
            result = subprocess.run(["git", "pull"], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output[name] = result.stdout.strip()
        except Exception as e:
            output[name] = str(e)
    return output