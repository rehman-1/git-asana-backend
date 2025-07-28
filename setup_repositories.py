#!/usr/bin/env python3
"""
Script to clone the required repositories into the Github directory
Run this on your server to set up the proper Git repositories
"""

import os
import subprocess
import shutil

# Repository configurations
REPOSITORIES = {
    "x-core": "https://github.com/XAION-Inc/x-core.git",
    "esa-be": "https://github.com/XAION-Inc/esa-be.git", 
    "eos-backend": "https://github.com/XAION-Inc/eos-backend.git"
}

def setup_repositories():
    """Clone repositories into the Github directory"""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    github_dir = os.path.join(project_root, "Github")
    
    # Create Github directory if it doesn't exist
    os.makedirs(github_dir, exist_ok=True)
    
    print(f"Setting up repositories in: {github_dir}")
    
    for repo_name, repo_url in REPOSITORIES.items():
        repo_path = os.path.join(github_dir, repo_name)
        
        print(f"\n--- Setting up {repo_name} ---")
        
        # Remove existing directory if it exists and is not a git repo
        if os.path.exists(repo_path):
            if not os.path.exists(os.path.join(repo_path, ".git")):
                print(f"Removing non-git directory: {repo_path}")
                shutil.rmtree(repo_path)
            else:
                print(f"Git repository already exists at: {repo_path}")
                continue
        
        # Clone the repository
        try:
            print(f"Cloning {repo_url} to {repo_path}")
            result = subprocess.run(
                ["git", "clone", repo_url, repo_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Successfully cloned {repo_name}")
            
            # Switch to prod branch if it exists
            try:
                subprocess.run(
                    ["git", "checkout", "prod"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ Switched to prod branch for {repo_name}")
            except subprocess.CalledProcessError:
                print(f"ℹ️  No prod branch found for {repo_name}, staying on default branch")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone {repo_name}: {e}")
            print(f"Error output: {e.stderr}")
        except Exception as e:
            print(f"❌ Unexpected error cloning {repo_name}: {e}")
    
    print("\n--- Repository setup complete ---")
    
    # Verify the setup
    print("\n--- Verification ---")
    for repo_name in REPOSITORIES.keys():
        repo_path = os.path.join(github_dir, repo_name)
        if os.path.exists(os.path.join(repo_path, ".git")):
            try:
                # Get remote info
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                print(f"✅ {repo_name}: {result.stdout.strip().split()[1]}")
            except Exception as e:
                print(f"❌ {repo_name}: Error getting remote info - {e}")
        else:
            print(f"❌ {repo_name}: Not a git repository")

if __name__ == "__main__":
    setup_repositories()