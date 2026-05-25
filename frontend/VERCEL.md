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

## Checklist

1. **Root Directory:** `frontend` (best) or repo root + root `vercel.json`
2. **Environment → Production:** `API_URL` = Render API URL (no trailing slash)
3. **Redeploy** with clear cache
4. Test: `https://YOUR_APP.vercel.app/en`
