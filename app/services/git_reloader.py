import os
import subprocess

REPO_PATHS = {
    "Frontend": "../Github/x-core",
    "ESA-Backend": "../Github/esa-be",
    "EOS-Backend": "../Github/eos-backend"
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