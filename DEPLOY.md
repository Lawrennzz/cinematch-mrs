# Streamlit Cloud deployment fix

Your logs show:

```text
Using Python 3.14.5 environment at /home/adminuser/venv
```

**Streamlit Cloud ignores `.python-version`.** Python must be chosen in the
deploy UI. Python 3.14 is too new and often breaks apps.

## Fix (required) — redeploy with Python 3.12

1. Go to https://share.streamlit.io
2. Open your app dashboard
3. Click **⋮** (three dots) → **Delete app** → confirm
4. Click **Create app** → **Deploy a public app from GitHub**
5. Set:
   - Repository: `Lawrennzz/cinematch-mrs`
   - Branch: `main`
   - Main file: `app.py`
6. Click **Advanced settings**
7. Set **Python version** to **3.12** (NOT 3.14)
8. Click **Save** → **Deploy**
9. Wait until logs show `Using Python 3.12.x` and the app loads

## Verify

Open your new URL in an incognito window. You should see the CineMatch login
page with demo accounts: `alice / alice123`.

## Admin key

`ADMIN-2026-MRS`
