# Deployment Guide - Vercel + Render

This guide walks you through deploying your LeetCode Analyzer to production using Vercel (frontend) and Render (backend).

## 🔐 Security First: Environment Variables

**IMPORTANT:** Your API keys are stored securely in the hosting platform dashboards, NOT in your code or Git repository.

### What Gets Committed to Git:
✅ Configuration files (`vercel.json`, `render.yaml`)
✅ `.env.example` (template without real keys)
✅ Application code

### What NEVER Gets Committed:
❌ `.env` files with real API keys
❌ Any file containing actual secrets
❌ Database files

---

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended for easy deployment)

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Render will auto-detect the `render.yaml` configuration

### Step 3: Configure Environment Variables (CRITICAL)
In the Render dashboard, go to **Environment** tab and add:

```
AI_PROVIDER=claude
FALLBACK_PROVIDER=openai
CLAUDE_API_KEY=your-actual-claude-api-key-here
CLAUDE_MODEL=claude-sonnet-4.5-20250514
OPENAI_API_KEY=your-actual-openai-api-key-here
OPENAI_MODEL=gpt-5-mini
DATABASE_URL=sqlite:///./leetcode_analysis.db
HISTORY_RETENTION_DAYS=7
RATE_LIMIT_PER_MINUTE=10
```

**Where to get API keys:**
- **Claude API Key**: [console.anthropic.com](https://console.anthropic.com/)
- **OpenAI API Key**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Copy your backend URL (e.g., `https://leetcode-analyzer-backend.onrender.com`)

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Verify API Configuration
The frontend now uses a centralized API configuration in `frontend/src/config/api.ts`. The production environment file is already set up:

- `frontend/.env.production` contains your Render backend URL
- `frontend/.env.development` contains localhost for local development
- The app automatically uses the correct URL based on the environment

No code changes needed! The configuration is already set to use your Render backend.

### Step 2: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### Step 3: Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Vercel auto-detects it's a Vite project

### Step 4: Configure Build Settings
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 5: Add Environment Variables (if needed)
If your frontend needs any env vars:
1. Go to **Settings** → **Environment Variables**
2. Add variables (e.g., `VITE_API_URL`)

### Step 6: Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Your site is live! 🎉

---

## Part 3: Update CORS Settings

After deployment, update your backend CORS to allow your Vercel domain:

1. In Render dashboard, go to **Environment** tab
2. Add a new environment variable:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   ```

3. Update `backend/main.py` CORS configuration:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:5173",  # Local development
           os.getenv("FRONTEND_URL", "")  # Production
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. Commit and push - Render will auto-redeploy

---

## 🎯 Quick Checklist

### Before Deployment:
- [ ] `.env` is in `.gitignore`
- [ ] No API keys in code
- [ ] `render.yaml` and `vercel.json` are configured

### Render Setup:
- [ ] Web service created
- [ ] Environment variables added (API keys!)
- [ ] Backend deployed successfully
- [ ] Backend URL copied

### Vercel Setup:
- [ ] Frontend API URL updated to Render backend
- [ ] Project imported
- [ ] Build settings configured
- [ ] Frontend deployed successfully

### Post-Deployment:
- [ ] CORS updated with production URL
- [ ] Test all features work
- [ ] Check API calls succeed

---

## 💰 Cost Breakdown

### Free Tier Limits:
- **Render**: 750 hours/month (enough for 1 service running 24/7)
- **Vercel**: Unlimited bandwidth for personal projects

### Paid Options (if needed):
- **Render**: $7/month for always-on service
- **Vercel**: Free for most use cases

---

## 🔧 Troubleshooting

### Backend won't start:
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is correct

### Frontend can't reach backend:
- Check CORS settings
- Verify backend URL in frontend code
- Check browser console for errors

### API key errors:
- Verify keys are correct in Render dashboard
- Check key has sufficient credits/quota
- Ensure no extra spaces in environment variables

---

## 📝 Updating Your App

### Backend Updates:
1. Push changes to GitHub
2. Render auto-deploys (or click "Manual Deploy")

### Frontend Updates:
1. Push changes to GitHub
2. Vercel auto-deploys

### Environment Variable Changes:
1. Update in Render/Vercel dashboard
2. Trigger manual redeploy

---

## 🚀 Next Steps

1. Set up custom domain (optional)
2. Add monitoring/analytics
3. Set up error tracking (Sentry)
4. Configure CDN for better performance

---

## Need Help?

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **CORS Issues**: Check browser console and backend logs
