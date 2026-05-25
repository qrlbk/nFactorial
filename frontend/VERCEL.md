# Vercel setup (required)

## Wrong build (Python instead of Next.js)

If deploy logs show:

```
Using Python 3.12 from pyproject.toml
runtime: python3.12  path: /
```

Vercel is deploying the **FastAPI backend**, not the UI. Fix:

1. **Settings → General → Framework Preset:** **Next.js**
2. **Root Directory:** `frontend` (recommended), **or** use repo-root `vercel.json` (already in repo)
3. **Redeploy** with **Clear build cache**

Correct log should mention `npm run build` and Next.js, not Python.

If you see `No Next.js version detected`: root `package.json` must list `next` in `dependencies` (already in repo), or set **Root Directory** to `frontend` only.

## Checklist

1. **Root Directory:** leave **empty** (repo root uses `package.json` workspaces) **or** set `frontend` and remove root `vercel.json` overrides
2. **Environment → Production:** `API_URL` = Render API URL (no trailing slash)
3. **Redeploy** with clear cache
4. Test: `https://YOUR_APP.vercel.app/en`
