# GitHub Repository Setup Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in the repository details:
   - **Repository name**: `artifact-retrieval-service-v1` (or your preferred name)
   - **Description**: `A well-tested Python service for retrieving artifacts from GitLab`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click **"Create repository"**

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```powershell
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/artifact-retrieval-service-v1.git

# Rename branch to 'main' (GitHub's default)
git branch -M main

# Push your code
git push -u origin main
```

## Alternative: Using SSH (if you have SSH keys set up)

```powershell
git remote add origin git@github.com:YOUR_USERNAME/artifact-retrieval-service-v1.git
git branch -M main
git push -u origin main
```

## Step 3: Verify

After pushing, refresh your GitHub repository page. You should see all your files!

## Troubleshooting

### If you get authentication errors:
- Use a Personal Access Token instead of password
- Generate one at: https://github.com/settings/tokens
- Use token as password when prompted

### If you need to change the remote URL:
```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/artifact-retrieval-service-v1.git
```


