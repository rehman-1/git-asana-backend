#!/bin/bash

# Script to clone the required repositories into the Github directory
# Run this on your server to set up the proper Git repositories

echo "Setting up Git repositories..."

# Create Github directory if it doesn't exist
mkdir -p Github

# Repository configurations
declare -A REPOS=(
    ["x-core"]="https://github.com/XAION-Inc/x-core.git"
    ["esa-be"]="https://github.com/XAION-Inc/esa-be.git"
    ["eos-backend"]="https://github.com/XAION-Inc/eos-backend.git"
)

# Clone each repository
for repo_name in "${!REPOS[@]}"; do
    repo_url="${REPOS[$repo_name]}"
    repo_path="Github/$repo_name"
    
    echo ""
    echo "--- Setting up $repo_name ---"
    
    # Remove existing directory if it exists and is not a git repo
    if [ -d "$repo_path" ]; then
        if [ ! -d "$repo_path/.git" ]; then
            echo "Removing non-git directory: $repo_path"
            rm -rf "$repo_path"
        else
            echo "Git repository already exists at: $repo_path"
            continue
        fi
    fi
    
    # Clone the repository
    echo "Cloning $repo_url to $repo_path"
    if git clone "$repo_url" "$repo_path"; then
        echo "✅ Successfully cloned $repo_name"
        
        # Switch to prod branch if it exists
        cd "$repo_path"
        if git checkout prod 2>/dev/null; then
            echo "✅ Switched to prod branch for $repo_name"
        else
            echo "ℹ️  No prod branch found for $repo_name, staying on default branch"
        fi
        cd - > /dev/null
    else
        echo "❌ Failed to clone $repo_name"
    fi
done

echo ""
echo "--- Repository setup complete ---"

# Verify the setup
echo ""
echo "--- Verification ---"
for repo_name in "${!REPOS[@]}"; do
    repo_path="Github/$repo_name"
    if [ -d "$repo_path/.git" ]; then
        remote_url=$(cd "$repo_path" && git remote get-url origin)
        echo "✅ $repo_name: $remote_url"
    else
        echo "❌ $repo_name: Not a git repository"
    fi
done

echo ""
echo "Setup complete! You can now run your git reload API."