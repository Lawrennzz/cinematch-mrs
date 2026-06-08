# Streamlit Cloud deployment — READ THIS

## Why the app fails

Your logs show:

```text
Using Python 3.14.5 environment
```

**Python 3.14 is the problem.** Streamlit Cloud ignores `.python-version`.
Pushing code changes will NOT fix this. You must redeploy with Python 3.12.

## Fix (5 minutes)

1. Open https://share.streamlit.io
2. Find your app → click **⋮** → **Delete app** → confirm delete
3. Click **Create app**
4. Select **Deploy a public app from GitHub**
5. Choose:
   - Repository: `Lawrennzz/cinematch-mrs`
   - Branch: `main`
   - Main file path: `app.py`
6. Click **Advanced settings**
7. Change **Python version** from 3.14 → **3.12**
8. Click **Save**
9. Click **Deploy**
10. Wait 2–3 minutes. Logs must show `Using Python 3.12.x` (NOT 3.14)

## How to confirm it worked

- Login page shows **CineMatch**
- Demo login: `alice` / `alice123`
- Admin key: `ADMIN-2026-MRS`

## If it still fails after Python 3.12 redeploy

Copy the **red error text** from Manage app → Logs and send it.
