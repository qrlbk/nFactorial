# Vercel — обязательные настройки

## 1. Root Directory = `frontend` (рекомендуется)

**Project → Settings → General → Root Directory:** `frontend`

Тогда:
- один `node_modules` (без `../node_modules/next` из корня репо)
- `frontend/vercel.json` управляет сборкой
- корневой `vercel.json` можно игнорировать

**Install:** `npm install --include=optional`  
**Build:** `npm run build`

## 2. Если Root Directory пустой (корень репо)

Используется корневой `vercel.json` с `cd frontend && ...`.  
**Framework Preset:** Next.js (не Python).

## 3. Environment

| Variable | Value |
|----------|--------|
| `API_URL` | `https://your-api.onrender.com` |

## 4. Native deps (Tailwind v4)

На Linux CI npm может не поставить `@tailwindcss/oxide-linux-*` (npm/cli#4828).  
В проекте: `optionalDependencies` + `postinstall` → `scripts/install-linux-native-deps.mjs`.

## 5. Проверка лога

✅ `Detected Next.js version: 15.5.x`  
✅ `next build` (без `--webpack`)  
❌ `Using Python 3.12 from pyproject.toml`  
❌ `Cannot find native binding` / `oxide-linux`
