# Vercel setup (required)

1. **Project → Settings → General → Root Directory:** `frontend`
2. **Environment → Production:** `API_URL` = your Render API URL (no trailing slash)
3. After git push: **Deployments → Redeploy** → enable **Clear build cache**
4. Test: `https://YOUR_APP.vercel.app/en` (not only `/`)

If Root Directory is empty, the deploy will crash with `FUNCTION_INVOCATION_FAILED`.
