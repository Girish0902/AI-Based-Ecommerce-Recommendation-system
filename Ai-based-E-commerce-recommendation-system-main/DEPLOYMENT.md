# 🚀 Deployment Guide - AI-Store

Complete guide for deploying with **Reflex (`reflex deploy`)** ensuring backend, frontend, and environment variables work correctly.

---

## ⚠️ Critical Issues & Solutions

### Issue 1: `.env` File Not Deployed
**Why**: `.env` files are intentionally in `.gitignore` for security (never commit secrets).
**Solution**: Set environment variables directly on your deployment platform (see instructions below).

### Issue 2: Backend Files Not Included
**Why**: Without proper `rxconfig.py` configuration, backend might not be deployed.
**Solution**: ✅ **FIXED** - `rxconfig.py` now includes `include_directories=["backend", "components", "pages", "state"]`

---

## 📋 Pre-Deployment Checklist

### ✅ 1. Local Testing
Before deploying, test everything locally:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
reflex run
```

Test all features:
- [ ] Frontend pages load
- [ ] Backend imports work (no ModuleNotFoundError)
- [ ] Recommendations appear
- [ ] User authentication works
- [ ] Cart/Wishlist functionality works
- [ ] Checkout process completes

### ✅ 2. Backend File Verification

Ensure these backend files exist and are properly imported:
- [ ] `backend/__init__.py` - ✓ Exists
- [ ] `backend/recommender.py` - ✓ Exists
- [ ] `backend/collaborative_filtering.py` - ✓ Exists
- [ ] `backend/content_filtering.py` - ✓ Exists
- [ ] `backend/rating_based.py` - ✓ Exists
- [ ] `backend/cleaning_data.py` - ✓ Exists

### ✅ 3. Data Files

Ensure these files exist for recommendations to work:
- [ ] `cleaned_data.csv` - Required for backend
- [ ] Place in root directory of your app

---

## 🌍 Deployment Platform Instructions

### **Option A: Render.com (Recommended for Reflex)**

#### Step 1: Prepare Repository
```bash
git add .
git commit -m "Pre-deployment: add backend and env config"
git push
```

#### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: ai-store
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `reflex export && reflex db upgrade && reflex deploy`

#### Step 3: Set Environment Variables
In Render dashboard → Environment:
```
FIREBASE_API_KEY=your_actual_key
FIREBASE_AUTH_DOMAIN=your_actual_domain
FIREBASE_PROJECT_ID=your_actual_project_id
FIREBASE_STORAGE_BUCKET=your_actual_bucket
FIREBASE_SENDER_ID=your_actual_sender_id
FIREBASE_APP_ID=your_actual_app_id
GROQ_API_KEY=your_actual_groq_key
RAZORPAY_KEY_ID=your_actual_razorpay_key
RAZORPAY_KEY_SECRET=your_actual_razorpay_secret
```

#### Step 4: Deploy
Render will automatically deploy when you push to main branch.

---

### **Option B: Vercel (Frontend only - NOT recommended for Reflex backend)**

⚠️ **Note**: Vercel is primarily for frontend. For full-stack, use Render, Railway, or Heroku.

---

### **Option C: Railway.app**

#### Step 1: Prepare
```bash
git add .
git commit -m "Pre-deployment setup"
git push
```

#### Step 2: Deploy
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Set variables in Railway dashboard
5. Railway auto-detects `requirements.txt` and deploys

---

### **Option D: Heroku (Legacy)**

```bash
heroku create your-app-name
heroku add-buildpack heroku/python
heroku config:set FIREBASE_API_KEY=your_key
heroku config:set GROQ_API_KEY=your_key
# ... set other variables
git push heroku main
```

---

---

## 🎯 Pre-Deployment Validation

**IMPORTANT**: Run this script BEFORE deploying to verify everything is configured correctly:

```bash
python validate_reflex_deploy.py
```

This checks:
- ✓ All backend files exist
- ✓ Frontend files exist
- ✓ `rxconfig.py` includes backend directories
- ✓ Data files are present
- ✓ Backend imports work
- ✓ `.gitignore` is properly configured
- ✓ Environment variables are set

---

## ⚡ Quick Start: Local Testing (Before Deployment)

### 1. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` File Locally
Copy `.env.example` to `.env` and fill in your actual API keys:
```bash
cp .env.example .env
```

Then edit `.env` and add your actual keys:
```
FIREBASE_API_KEY=your_actual_firebase_key
FIREBASE_AUTH_DOMAIN=your_actual_domain
FIREBASE_PROJECT_ID=your_actual_project_id
GROQ_API_KEY=your_actual_groq_key
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### 4. Run Locally
```bash
reflex run
```

Visit `http://localhost:3000` and test:
- Frontend pages load
- Recommendations work (backend functions called)
- User authentication
- Cart/Wishlist functionality
- Checkout process

### 5. Verify Backend Works
```bash
python -c "from backend.recommender import get_combined_recommendations; print('✓ Backend imports work!')"
```

---

## 🚀 Deploy with `reflex deploy`

### Reflex Cloud Deployment (Easiest)

```bash
# Make sure you're logged in
reflex login

# Deploy
reflex deploy
```

**During deployment, Reflex will:**
1. ✓ Export your frontend (Reflex/React)
2. ✓ Include backend files (via `include_directories` in rxconfig.py)
3. ✓ Build and deploy to Reflex Cloud
4. ✓ Create a public URL

**After deployment, set environment variables:**
1. Go to Reflex Dashboard
2. Select your app
3. Go to "Settings" → "Environment Variables"
4. Add all variables from `.env.example`:
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_STORAGE_BUCKET`
   - `FIREBASE_SENDER_ID`
   - `FIREBASE_APP_ID`
   - `GROQ_API_KEY`
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`

5. Click "Deploy" to apply changes

---

## 🌍 Alternative: Custom Hosting (Render, Railway, Heroku)

### Render.com (Recommended Alternative)

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push
```

#### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Service Name**: ai-store
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && reflex export`
   - **Start Command**: `reflex db upgrade && reflex start`

#### Step 3: Set Environment Variables
In Render dashboard → Environment:
```
FIREBASE_API_KEY=your_key
FIREBASE_AUTH_DOMAIN=your_domain
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_bucket
FIREBASE_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
GROQ_API_KEY=your_groq_key
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_secret
```

#### Step 4: Deploy
Render auto-deploys on git push

---

### Railway.app (Fast Alternative)

```bash
# Install railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set variables
railway variables set FIREBASE_API_KEY=your_key
railway variables set GROQ_API_KEY=your_key
# ... set all others

# Deploy
railway up
```

---

## ✅ Verify Deployment Works

### 1. Check Deployment Status
**Reflex Cloud**: Reflex Dashboard → Deployments
**Render**: Render Dashboard → Services
**Railway**: Railway Dashboard → Services

### 2. Test Backend After Deployment
```bash
# Visit your deployed URL and test:
# - Navigate to pages that use recommendations
# - Check browser console for errors
# - Verify data loads from app.backend```

### 3. Common Issues & Fixes

#### Problem: Backend import errors
**Cause**: Backend files not included in deployment
**Fix**: Verify `rxconfig.py` has `include_directories=["backend", ...]`

#### Problem: Recommendations not working
**Cause**: `cleaned_data.csv` missing or environment variables not set
**Fix**: 
- Ensure `cleaned_data.csv` is in root directory
- Set `GROQ_API_KEY` on platform
- Restart deployment

#### Problem: Firebase not working
**Cause**: Firebase env vars not set
**Fix**: Set all `FIREBASE_*` variables in deployment platform

#### Problem: Razorpay errors (optional)
**Cause**: `RAZORPAY_KEY_*` not configured
**Fix**: Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in deployment platform

---

## 📦 What Gets Deployed

### ✓ **Included** (will be on server)
```
backend/              ← All backend code
pages/                ← All page components
state/                ← All state management
components/           ← Shared components
requirements.txt      ← Dependencies
```

### ✗ **NOT Included** (will NOT be on server)
```
.env                  ← Secrets (set via platform instead)
__pycache__/          ← Python cache
.web/                 ← Reflex build artifacts
.states/              ← Local state
```

---

## 🔐 Security Best Practices

1. **NEVER commit `.env`** - It's in `.gitignore` for a reason
2. **Set secrets via platform** - Use Reflex Cloud/Render/Railway dashboards
3. **Use `.env.example`** - Document required variables, no actual keys
4. **Rotate keys regularly** - Update sensitive keys quarterly
5. **Use separate credentials** - Dev keys ≠ Prod keys

---

## 📞 Support & Troubleshooting

### Before contacting support, verify:
1. Run `python validate_reflex_deploy.py` ✓ All pass
2. `reflex run` works locally ✓
3. All environment variables set on platform ✓
4. `cleaned_data.csv` exists ✓

### Common Commands
```bash
# View logs (Reflex Cloud)
reflex logs

# View logs (Render)
# Via dashboard or: render logs your-app-name

# Clear cache and redeploy
reflex clean && reflex deploy

# View environment
reflex env
```

---

## ✨ Final Checklist Before Going Live

- [ ] Run `python validate_reflex_deploy.py` - All pass
- [ ] Tested locally with `reflex run`
- [ ] Backend imports work
- [ ] `.env.example` is committed (NOT `.env`)
- [ ] All environment variables set on platform
- [ ] `cleaned_data.csv` is in root directory
- [ ] `rxconfig.py` includes backend directories
- [ ] Recommendations work on deployed URL
- [ ] User authentication works
- [ ] Payment flow works (if using Razorpay)

---

## 📝 Notes

- Your `.env` file (local) is NOT uploaded to the server - this is correct
- Environment variables must be set on your hosting platform
- Backend files ARE uploaded (via `include_directories` in `rxconfig.py`)
- Data files like `cleaned_data.csv` ARE uploaded automatically

For questions: Check Reflex docs at [reflex.dev](https://reflex.dev/docs/hosting/deploy)

**Railway:**
```bash
railway variable set FIREBASE_API_KEY=your_key
```

**Heroku:**
```bash
heroku config:set FIREBASE_API_KEY=your_key
```

---

## 📦 Verifying Deployment Success

After deployment, verify:

1. **Frontend loads**: Visit your deployed URL
2. **Backend works**: 
   - Check browser console for errors
   - Test recommendation features
   - Check network tab for API calls
3. **Environment variables work**:
   - Authentication appears
   - Chatbot responds (Groq API)
   - Payment integration works

### Check deployment logs:
- **Render**: Environment → Logs
- **Railway**: Logs tab
- **Heroku**: `heroku logs --tail`

---

## ❌ Troubleshooting

### "ModuleNotFoundError: No module named 'backend'"
**Solution**: 
- Ensure `backend/__init__.py` exists ✓
- Check imports use correct paths
- Ensure requirements.txt has all dependencies

### Environment variables not loading
**Solution**:
- Verify variables are set on platform dashboard
- Check variable names match exactly
- Restart/redeploy after setting variables
- Use `python -c "import os; print(os.environ.get('FIREBASE_API_KEY'))"` to debug

### Recommendations not showing
**Solution**:
- Verify `cleaned_data.csv` is deployed
- Check backend logs for import errors
- Ensure all backend files are included

### Frontend works but backend doesn't
**Solution**:
- This was your previous issue!
- Verify all backend files are in git repository
- Add backend files to git: `git add backend/`
- Ensure they're not in `.gitignore`

---

## 📝 .gitignore Best Practice

**Current issue**: `.env` is ignored (correct to prevent secrets), but this breaks deployment.

**Solution**: 
1. Keep `.env` in `.gitignore` ✓ (Already done)
2. Use `.env.example` as template ✓ (Created)
3. Set env vars on deployment platform ✓ (This guide)

**Verify backend files are NOT ignored:**
```
# Check if backend is ignored
grep "^backend" .gitignore  # Should return nothing

# Correct- backend should NOT be here
```

---

## 🛟 Quick Deploy Summary

1. ✅ Local test: `reflex run`
2. ✅ Push to git: `git push`
3. ✅ Connect to deployment platform
4. ✅ Set environment variables
5. ✅ Deploy starts automatically
6. ✅ Test URL works

---

## 📞 Support

If deployment fails:
1. Check deployment platform logs
2. Verify all environment variables are set
3. Ensure `cleaned_data.csv` exists
4. Run locally first: `reflex run`
5. Check backend imports work

---

**Last Updated**: 2026-03-31
**Status**: All backend files verified ✓
