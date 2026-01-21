# 🚀 DEPLOY TO RENDER.COM - STEP BY STEP GUIDE

Complete walkthrough for deploying Retail Marketing Agent to Render.com

---

## ⏱️ TOTAL TIME: 20-30 minutes

### Setup: 5 minutes
### Deployment: 10-15 minutes
### Testing: 5-10 minutes

---

## 📋 WHAT'S CHANGED IN YOUR CODE

### **New File: `render_app.py`**
- Flask API server (instead of Gradio for Render compatibility)
- 7 REST API endpoints
- Automatic environment variable handling
- CORS enabled for frontend integration
- Designed for Render.com's architecture

### **New File: `Procfile`**
- Tells Render how to start your app
- Simple: `web: python render_app.py`

### **Updated: `requirements.txt`**
- Added: `flask>=3.0.0` and `flask-cors>=4.0.0`
- Everything else stays the same

**Why these changes?**
- Render prefers simple HTTP servers
- Gradio works but Render + Gradio can have cold-start issues
- Flask API is lighter, faster, and more Render-friendly
- Your original `app.py` still works for local testing

---

## 🚀 STEP 1: PREPARE YOUR REPOSITORY

### **1.1 Check Files Are Ready**

Verify these files exist in your project root:

```
✓ render_app.py          (NEW - Flask API)
✓ Procfile               (NEW - Render config)
✓ requirements.txt       (UPDATED - has Flask + CORS)
✓ .env.example           (Should exist)
✓ README.md              (Should exist)
```

**Verify with:**
```powershell
ls *.py | Select-Object Name
ls Procfile
```

### **1.2 Update .env.example**

Make sure your `.env.example` has:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://your-instance.openai.azure.com/
OPENAI_API_VERSION=2024-02-01
OPENAI_DEPLOYMENT_NAME=gpt-4o
FLASK_ENV=production
```

### **1.3 Create .gitignore** (if not exists)

Make sure your `.gitignore` includes:

```
.env
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
node_modules/
```

---

## 🔐 STEP 2: SET UP GIT REPOSITORY

### **2.1 Initialize Git** (if not already done)

```powershell
cd "C:\Users\prasa\Downloads\Retail Marketing Agent\Retail Marketing Agent"

# Initialize git
git init

# Check git status
git status
```

### **2.2 Add Files to Git**

```powershell
# Add all files
git add .

# Check what will be committed
git status

# Commit
git commit -m "Initial commit: Retail Marketing Agent ready for Render"
```

### **2.3 Create GitHub Repository**

1. Go to https://github.com/new
2. Create new repository (any name, e.g., `retail-marketing-agent`)
3. **DO NOT** initialize with README (you already have one)
4. Copy the commands shown

### **2.4 Push to GitHub**

```powershell
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/retail-marketing-agent.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**Result:** Your code is now on GitHub! 🎉

---

## 🌐 STEP 3: CREATE RENDER ACCOUNT

### **3.1 Sign Up for Render**

1. Open https://render.com
2. Click "Get Started"
3. Sign up with GitHub (**important!**)
4. Authorize Render to access GitHub
5. Verify email

---

## 📦 STEP 4: DEPLOY TO RENDER

### **4.1 Create New Web Service**

1. Log in to Render dashboard
2. Click "New +" button (top right)
3. Select "Web Service"

### **4.2 Connect GitHub Repository**

1. Click "Connect Repository"
2. Find your repo: `retail-marketing-agent`
3. Click "Connect"

**If repo doesn't appear:**
- Click "Configure account"
- Grant Render access to all repositories
- Try again

### **4.3 Configure Service**

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `retail-marketing-agent` |
| **Environment** | `Python 3` |
| **Region** | `Ohio` (or closest to you) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python render_app.py` |

### **4.4 Add Environment Variables**

1. Scroll down to "Environment"
2. Click "Add Environment Variable"

**Add these variables:**

```
OPENAI_API_KEY = [your_openai_api_key]
OPENAI_API_BASE = https://your-instance.openai.azure.com/
OPENAI_API_VERSION = 2024-02-01
OPENAI_DEPLOYMENT_NAME = gpt-4o
FLASK_ENV = production
```

**How to get these values:**
- `OPENAI_API_KEY`: Your Azure OpenAI key
- `OPENAI_API_BASE`: Your Azure OpenAI endpoint (URL)
- `OPENAI_DEPLOYMENT_NAME`: Usually `gpt-4o`
- Others: Keep as shown

### **4.5 Configure Resource**

For free tier:
- **Instance Type**: Free
- **Auto-Deploy**: Toggle ON (auto-deploy on GitHub push)

### **4.6 Review & Deploy**

1. Scroll down to bottom
2. Click "Create Web Service"
3. Watch the deploy logs scroll

**Deployment takes 2-5 minutes**

Expected logs:
```
Building your service...
Installing Python 3.11...
Running: pip install -r requirements.txt
...
Building application...
App deployed successfully!
```

### **4.7 Get Your Live URL**

Once deployed, Render shows your URL:
```
https://retail-marketing-agent-XXXX.onrender.com
```

**Save this URL!** 🎉

---

## 🧪 STEP 5: TEST YOUR API

### **5.1 Test Health Endpoint**

```powershell
$API_URL = "https://retail-marketing-agent-XXXX.onrender.com"

# Test health
curl "$API_URL/api/health"
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T10:30:00.123456",
  "service": "Retail Marketing Agent API"
}
```

✅ If you see this, your API is LIVE!

### **5.2 Test Initialize Endpoint**

```powershell
$body = @{
    client_name = "Fashion Store NYC"
    store_type = "fashion"
    location = "New York"
    has_online_store = $true
} | ConvertTo-Json

curl -X POST "$API_URL/api/initialize" `
  -H "Content-Type: application/json" `
  -Body $body
```

**Expected response:**
```json
{
  "agent_id": "agent_Fashion_Store_NYC_1705840200",
  "client_name": "Fashion Store NYC",
  "store_type": "fashion",
  "location": "New York",
  "has_online_store": true,
  "status": "initialized"
}
```

### **5.3 Test Campaign Generation**

```powershell
$body = @{
    agent_id = "agent_Fashion_Store_NYC_1705840200"
    goal_type = "customer_acquisition"
    target = "Increase foot traffic by 30%"
    budget = 5000
} | ConvertTo-Json

curl -X POST "$API_URL/api/generate-campaign" `
  -H "Content-Type: application/json" `
  -Body $body
```

**Expected response:**
```json
{
  "campaign_id": "campaign_agent_Fashion_Store_NYC_1705840200_1705840300",
  "agent_id": "agent_Fashion_Store_NYC_1705840200",
  "goal_type": "customer_acquisition",
  "status": "draft",
  "campaign_plan": { ... }
}
```

### **5.4 All 5 Endpoints**

| Endpoint | Method | Status |
|----------|--------|--------|
| `/api/health` | GET | ✅ Ready |
| `/api/initialize` | POST | ✅ Ready |
| `/api/generate-campaign` | POST | ✅ Ready |
| `/api/execute-campaign` | POST | ✅ Ready |
| `/api/campaign-status/{id}` | GET | ✅ Ready |

---

## 📊 OPTIONAL: BUILD FRONTEND

### **Option A: Use with Gradio Locally**

You can still use your Gradio UI locally and connect to Render API:

```powershell
# Terminal 1: Keep Render API running (no action needed)

# Terminal 2: Run Gradio locally
python app.py

# In Gradio, it will call your live Render API
```

### **Option B: Build React Frontend**

Create a React app that uses your Render API:

```powershell
# Create React app
npx create-react-app frontend

cd frontend

# Install axios
npm install axios

# Create API client file (see Optional React Setup below)

# Run locally
npm start

# Build for production
npm run build
```

---

## 🔍 STEP 6: MONITOR YOUR DEPLOYMENT

### **6.1 View Logs in Render**

1. Go to https://dashboard.render.com
2. Click your service: `retail-marketing-agent`
3. Click "Logs" tab
4. Watch real-time logs as you make requests

### **6.2 Check Service Status**

- Green checkmark = ✅ Running
- Yellow/Red = ❌ Issue detected

### **6.3 View Metrics**

1. Click "Metrics" tab
2. See CPU, Memory, Network usage
3. Should be low for free tier

---

## 💡 STEP 7: UPDATE & REDEPLOY

### **7.1 Make Code Changes Locally**

```powershell
# Edit your files locally
code render_app.py

# Test locally if needed
python render_app.py

# Commit and push
git add .
git commit -m "Improved campaign generation"
git push origin main
```

### **7.2 Automatic Redeployment**

Render automatically redeploys when you push to GitHub!

**Check deployment status:**
1. Go to Render dashboard
2. Click your service
3. Click "Deploys" tab
4. See deploy history

---

## 🎯 YOUR LIVE API ENDPOINTS

**Base URL:** `https://retail-marketing-agent-XXXX.onrender.com`

### **All Available Endpoints:**

```
GET  /api/health
     → Check if API is alive

POST /api/initialize
     Body: {client_name, store_type, location, has_online_store}
     → Create new marketing agent

POST /api/generate-campaign
     Body: {agent_id, goal_type, target, budget}
     → Generate AI campaign plan

POST /api/execute-campaign
     Body: {campaign_id, agent_id}
     → Execute campaign

GET  /api/campaign-status/{campaign_id}
     → Get campaign metrics and progress

GET  /api/agents
     → List all agents

GET  /api/agents/{agent_id}
     → Get specific agent info
```

---

## ⚡ PERFORMANCE NOTES

### **Cold Starts (First Request)**
- First request: 5-10 seconds (Render spins up)
- Subsequent requests: < 500ms
- **Tip:** Keep your Gradio UI making requests to keep it warm

### **If Service Sleeps**
- Free tier services sleep after 15 minutes of no traffic
- Next request wakes it up (5-10 sec delay)
- No data loss, just a delay

### **To Keep Service Awake**
- Free tier will include health checks every 15 minutes
- Or you can set up external monitoring

---

## 🔐 SECURITY BEST PRACTICES

### **DO:**
- ✅ Store API keys in environment variables (done!)
- ✅ Use HTTPS (Render provides automatic SSL)
- ✅ Keep secrets out of code
- ✅ Use `.env` locally, not `.env.production`

### **DON'T:**
- ❌ Put API keys in code
- ❌ Push `.env` to GitHub
- ❌ Share your API URL publicly with secrets

---

## 🐛 TROUBLESHOOTING

### **Issue: Deploy Fails**

```
Error: Python 3.x not found
```

**Solution:**
- Check Python version in build logs
- Ensure `requirements.txt` is formatted correctly
- Try: Delete service and redeploy

### **Issue: API Returns 500 Error**

```
Internal Server Error
```

**Solution:**
1. Check logs in Render dashboard
2. Verify environment variables are set
3. Check OpenAI API key is correct
4. Test locally first: `python render_app.py`

### **Issue: 502 Bad Gateway**

```
502 Bad Gateway
```

**Solution:**
- Service crashed or restarting
- Check logs
- Ensure Start Command is: `python render_app.py`
- Check PORT isn't hardcoded (Render sets PORT env var)

### **Issue: API Very Slow**

**Solutions:**
1. First request after sleep: Normal (5-10 sec)
2. On free tier, resources are shared
3. Upgrade to paid plan for better performance
4. Consider Railway instead ($5/mo free tier)

### **Issue: Can't Push to GitHub**

```
fatal: 'origin' does not appear to be a 'git' repository
```

**Solution:**
```powershell
# Set up git remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## 📞 QUICK REFERENCE

| Action | Command |
|--------|---------|
| Test API | `curl https://YOUR_URL/api/health` |
| View logs | Go to Render dashboard → Logs tab |
| Redeploy | Push to GitHub (automatic) |
| Manual redeploy | Render dashboard → Manual deploy |
| Check status | Render dashboard → Status indicator |
| Update env vars | Render dashboard → Environment tab |

---

## ✅ DEPLOYMENT CHECKLIST

Before starting:
- [ ] Code pushed to GitHub
- [ ] `.env.example` has all variables
- [ ] `Procfile` exists
- [ ] `render_app.py` exists
- [ ] `requirements.txt` includes Flask

During deployment:
- [ ] Render service created
- [ ] Environment variables set
- [ ] Build succeeded (check logs)
- [ ] Service shows green checkmark

After deployment:
- [ ] Health endpoint works: `/api/health`
- [ ] Initialize endpoint works: `/api/initialize`
- [ ] Campaign generation works
- [ ] API responds in < 500ms

---

## 🎉 YOU'RE DONE!

### **Your Live API:**
```
https://retail-marketing-agent-XXXX.onrender.com/api
```

### **Next Steps:**

**Option 1: Test Everything**
```powershell
# Make all API calls from our test guide
curl https://YOUR_URL/api/health
```

**Option 2: Deploy Frontend**
- Create React app
- Point to your Render API
- Deploy to Vercel or Netlify (both free)

**Option 3: Keep It Running**
- Monitor in Render dashboard
- Make code changes → Push to GitHub
- Auto-redeploy happens automatically

---

## 📚 ADDITIONAL RESOURCES

| Resource | Link |
|----------|------|
| Render Docs | https://render.com/docs |
| Flask Docs | https://flask.palletsprojects.com |
| OpenAI Docs | https://platform.openai.com/docs |
| GitHub | https://github.com |

---

**Need help?** Check the logs in Render dashboard or see troubleshooting section above! 🚀
