import os
import pickle
from datetime import datetime

def get_latest_backup():
    backups = [f for f in os.listdir() if f.startswith('user_backup_') and f.endswith('.pkl')]
    if not backups:
        return None
    return sorted(backups)[-1]  # সর্বশেষ ফাইল

def restore():
    BACKUP_DB = get_latest_backup()
    CURRENT_DB = 'user_data.pkl'

    if not BACKUP_DB:
        print(f"[{datetime.now()}] ❌ Error: No backup file found!")
        return

    try:
        with open(BACKUP_DB, 'rb') as f:
            data = pickle.load(f)

        required_keys = {'users', 'referral_map', 'stats'}
        if not all(k in data for k in required_keys):
            print(f"[{datetime.now()}] ❌ Error: Invalid backup structure.")
            return

        with open(CURRENT_DB, 'wb') as f:
            pickle.dump(data, f)

        print(f"[{datetime.now()}] ✅ Restore successful from {BACKUP_DB}")
        print(f"Users restored: {len(data['users'])}")
        print(f"Active referrals: {len(data['referral_map'])}")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Restore failed: {e}")

if __name__ == '__main__':
    restore()
