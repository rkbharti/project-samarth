# 🚀 Deployment (Free tier)

## Backend on Railway
1. Install Railway CLI
```bash
npm i -g @railway/cli
```
2. Login and initialize
```bash
railway login
railway init
```
3. Set environment variables (optional)
```bash
railway variables set PYTHONPATH=/app
railway variables set USE_OPENAI_EMBEDDINGS=false
```
4. Deploy
```bash
railway up
```
Your backend will be available at a URL like:
```
https://<your-app>.railway.app
```

## Frontend on Vercel
1. Install Vercel CLI
```bash
npm i -g vercel
```
2. Build & deploy from frontend directory
```bash
cd frontend
# Use your Railway backend URL below
setx REACT_APP_API_URL https://<your-app>.railway.app
npm run build
vercel --prod
```
Your frontend will be available at a URL like:
```
https://project-samarth.vercel.app (example)
```

## Update frontend API URL (dev & prod)
- We added `frontend/src/config/api.js` which reads `REACT_APP_API_URL`.
- For local dev it falls back to `http://localhost:8000`.
- On Vercel, set the env var in dashboard or via CLI before build:
```bash
vercel env add REACT_APP_API_URL
# then provide https://<your-app>.railway.app
```

## Verify
- Backend health: `https://<your-app>.railway.app/health`
- API docs: `https://<your-app>.railway.app/docs`
- Frontend loads and queries succeed.
