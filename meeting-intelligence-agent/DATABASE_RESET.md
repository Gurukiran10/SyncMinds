# 🗑️ Database Reset Guide

## Quick Reset Command

To reset your database and remove all demo data:

```bash
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
python3 scripts/reset_db.py
```

This will:
- ❌ Delete all meetings
- ❌ Delete all action items  
- ❌ Delete all mentions
- ✅ Keep the admin user (username: admin, password: admin123)

## What You'll See

```
⚠️  This will delete ALL meetings and action items. Continue? (yes/no): 
```

Type `yes` and press Enter to confirm.

## After Reset

1. **Refresh your browser** at http://127.0.0.1:3001
2. You'll see:
   - Dashboard with 0 meetings
   - Empty meetings list
   - No action items
   - Clean slate to start fresh!

## Alternative: Complete Database Wipe

If you want to delete EVERYTHING including the admin user:

```bash
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
rm test.db
python3 -c "from app.core.database import init_db; init_db()"
python3 scripts/create_admin.py
```

This creates a brand new database from scratch.

## Manual Data Cleanup (Fine-Grained Control)

### Delete specific meetings:
Use the UI - click the trash icon next meetings

### Delete all action items only:
```python
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
python3 -c "
from app.core.database import SessionLocal
from app.models.action_item import ActionItem
db = SessionLocal()
db.query(ActionItem).delete()
db.commit()
print('Action items deleted')
db.close()
"
```

### Delete all mentions only:
```python
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
python3 -c "
from app.core.database import SessionLocal
from app.models.mention import Mention
db = SessionLocal()
db.query(Mention).delete()
db.commit()
print('Mentions deleted')
db.close()
"
```

## Backup Before Reset

To save your current database before resetting:

```bash
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
cp test.db test.db.backup.$(date +%Y%m%d)
```

To restore from backup:
```bash
cp test.db.backup.20260306 test.db
```
