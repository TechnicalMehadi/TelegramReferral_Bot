import os
import pickle
import subprocess
from datetime import datetime

# ===== CONFIGURATION =====
GITHUB_USERNAME = "mdmehadihasanshuvo"
REPO_NAME = "TelegramReferral_Bot"
MAIN_DATA_FILE = "user_data.pkl"
GIT_BRANCH = "main"

# ===== STEP 1: Create backup filename with timestamp =====
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = f"user_backup_{timestamp}.pkl"
print(f"ℹ️ Starting backup process at {timestamp}")

# ===== STEP 2: Verify main data file exists =====
if not os.path.exists(MAIN_DATA_FILE):
    print(f"❌ Error: {MAIN_DATA_FILE} not found in current directory!")
    exit()

# ===== STEP 3: Create backup =====
try:
    with open(MAIN_DATA_FILE, "rb") as f:
        data = pickle.load(f)
    
    with open(backup_filename, "wb") as f:
        pickle.dump(data, f)
    print(f"✅ Backup created: {backup_filename}")
except Exception as e:
    print(f"❌ Failed to create backup: {str(e)}")
    exit()

# ===== STEP 4: Configure Git ignore =====
gitignore_content = f"{MAIN_DATA_FILE}\n*.env\n*.key\n__pycache__/\n"
if not os.path.exists(".gitignore"):
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")
else:
    with open(".gitignore", "r+") as f:
        content = f.read()
        if MAIN_DATA_FILE not in content:
            f.write(gitignore_content)
            print("✅ Updated .gitignore file")

# ===== STEP 5: Set Git identity =====
try:
    subprocess.run(["git", "config", "--global", "user.name", "Shuvo"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "mdmehadihasan0011@gmail.com"], check=True)
    print("✅ Git identity configured")
except subprocess.CalledProcessError:
    print("⚠️ Could not set Git identity (may already be set)")

# ===== STEP 6: Verify Git repository =====
try:
    # Check if we're in a Git repo
    subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
    
    # Verify remote exists
    remotes = subprocess.run(["git", "remote", "-v"], check=True, capture_output=True, text=True)
    if "origin" not in remotes.stdout:
        print("❌ No 'origin' remote configured!")
        print("Please run: git remote add origin git@github.com:{GITHUB_USERNAME}/{REPO_NAME}.git")
        exit()
except subprocess.CalledProcessError:
    print("❌ Not a Git repository or Git not installed")
    print(f"Initialize first with: git init && git remote add origin git@github.com:{GITHUB_USERNAME}/{REPO_NAME}.git")
    exit()

# ===== STEP 7: Push to GitHub =====
try:
    # Add and commit
    subprocess.run(["git", "add", backup_filename], check=True)
    commit_msg = f"🔖 Automated backup {timestamp}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    
    # Push using SSH
    subprocess.run(["git", "push", "origin", GIT_BRANCH], check=True)
    print("🚀 Backup successfully pushed to GitHub!")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Git operation failed: {e}")
    print("Possible solutions:")
    print("1. Ensure you have SSH keys set up for GitHub")
    print("2. Check your internet connection")
    print(f"3. Verify repository exists: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
    print("4. Try manually: git push origin main")
