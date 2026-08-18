"""
GitHub Auto-Publisher Script
Creates a new repository named 'beta-model' on your GitHub account and uploads all files.
Requires a GitHub Personal Access Token (PAT) with 'repo' scope.
"""

import os
import sys
import base64
import requests

# Force utf-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

GITHUB_API = "https://api.github.com"
REPO_NAME = "beta-model"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

IGNORE_DIRS = {"venv", ".git", "__pycache__", ".pytest_cache", ".idea", ".vscode"}
IGNORE_FILES = {".DS_Store", "Thumbs.db"}

def publish_repository(token: str):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Get authenticated user info
    user_res = requests.get(f"{GITHUB_API}/user", headers=headers)
    if user_res.status_code != 200:
        print(f"[ERROR] Invalid GitHub Token or authentication error: {user_res.status_code} - {user_res.json().get('message')}")
        return
    
    username = user_res.json()["login"]
    print(f"[OK] Authenticated as GitHub user: {username}")

    # 2. Check if repository exists or create it
    repo_res = requests.get(f"{GITHUB_API}/repos/{username}/{REPO_NAME}", headers=headers)
    if repo_res.status_code == 404:
        print(f"Creating repository '{REPO_NAME}' on GitHub...")
        create_res = requests.post(
            f"{GITHUB_API}/user/repos",
            headers=headers,
            json={
                "name": REPO_NAME,
                "description": "Automated Indian Stocks Beta Tracker & Live Streamlit Dashboard",
                "private": False,
                "auto_init": False
            }
        )
        if create_res.status_code == 201:
            print(f"[CREATED] Repository URL: https://github.com/{username}/{REPO_NAME}")
        else:
            print(f"[ERROR] Creating repository: {create_res.json()}")
            return
    else:
        print(f"[INFO] Repository '{REPO_NAME}' already exists on GitHub.")

    # 3. Upload files to repository
    print("Uploading project files to GitHub...")
    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f in IGNORE_FILES or f.endswith(".pyc"):
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, PROJECT_DIR).replace("\\", "/")
            
            with open(full_path, "rb") as file_obj:
                content_bytes = file_obj.read()
                content_b64 = base64.b64encode(content_bytes).decode("utf-8")

            url = f"{GITHUB_API}/repos/{username}/{REPO_NAME}/contents/{rel_path}"
            
            # Check if file exists to get SHA
            get_f = requests.get(url, headers=headers)
            sha = get_f.json().get("sha") if get_f.status_code == 200 else None

            payload = {
                "message": f"Add {rel_path}",
                "content": content_b64
            }
            if sha:
                payload["sha"] = sha

            put_res = requests.put(url, headers=headers, json=payload)
            if put_res.status_code in (200, 201):
                print(f"  + Uploaded {rel_path}")
            else:
                print(f"  - Error uploading {rel_path}: {put_res.json().get('message')}")

    print("\n[SUCCESS] Your repository is live at:")
    print(f"https://github.com/{username}/{REPO_NAME}")
    print("\nNext step: Connect your repo at https://share.streamlit.io to deploy the live web dashboard!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token_input = sys.argv[1].strip()
    else:
        token_input = input("Enter your GitHub Personal Access Token (PAT): ").strip()
    
    if token_input:
        publish_repository(token_input)
    else:
        print("Token is required to authenticate with GitHub.")

