# 🎯 RENDER DEPLOYMENT - ACTION GUIDE

Ready to deploy? Follow this checklist!

---

## ✅ PRE-DEPLOYMENT (DO FIRST)

### **1. Verify Your Code is Ready**

```powershell
# Navigate to project
cd "C:\Users\prasa\Downloads\Retail Marketing Agent\Retail Marketing Agent"

# Check files exist
ls render_app.py
ls Procfile
ls requirements.txt
cat .env.example | head -10
```

**Expected output:**
```
✓ render_app.py        (Flask API)
✓ Procfile             (web: python render_app.py)
✓ requirements.txt     (includes flask, flask-cors)
✓ .env.example         (OPENAI_API_BASE, etc.)
```

### **2. Ensure Git is Set Up**

```powershell
# Check git status
git status

# If not initialized:
# git init
# git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO

# Push code to GitHub
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

## 🚀 DEPLOYMENT STEPS (DETAILED)

### **STEP 1: CREATE RENDER ACCOUNT** (5 min)

1. **Visit:** https://render.com
2. **Click:** "Get Started"
3. **Sign Up:** With GitHub (click "GitHub")
4. **Authorize:** Grant Render access to your repos
5. **Verify:** Check your email
6. **Login:** To Render dashboard

**Result:** ✅ You're logged into Render

---

### **STEP 2: CREATE WEB SERVICE** (10 min)

1. **In Render Dashboard:**
   - Click "New +"
   - Select "Web Service"

2. **Select Repository:**
   - Click "Connect Repository"
   - Search: "retail-marketing-agent" (or your repo name)
   - Click "Connect"

3. **Fill in Configuration:**

| Field | Value |
|-------|-------|
| **Name** | retail-marketing-agent |
| **Environment** | Python 3 |
| **Region** | Ohio (closest to US) |
| **Branch** | main |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python render_app.py` |
| **Instance Type** | Free |

4. **Enable Auto-Deploy:**
   - Toggle "Auto-Deploy" = ON
   - This auto-deploys when you push to GitHub

5. **Scroll Down** to "Environment"

---

### **STEP 3: ADD ENVIRONMENT VARIABLES** (5 min)

In the "Environment" section, click "Add Environment Variable" for each:

**Variable 1: OpenAI API Key**
```
Name:  OPENAI_API_KEY
Value: [Your Azure OpenAI API Key]
```

**Variable 2: OpenAI Endpoint**
```
Name:  OPENAI_API_BASE
Value: https://your-instance.openai.azure.com/
```

**Variable 3: OpenAI Version**
```
Name:  OPENAI_API_VERSION
Value: 2024-02-01
```

**Variable 4: Deployment Name**
```
Name:  OPENAI_DEPLOYMENT_NAME
Value: gpt-4o
```

**Variable 5: Flask Environment**
```
Name:  FLASK_ENV
Value: production
```

**How to get these values:**

```
OPENAI_API_KEY
└─ Go to Azure Portal → OpenAI resource → Keys and Endpoint → Copy Key 1

OPENAI_API_BASE
└─ Azure Portal → OpenAI resource → Keys and Endpoint → Copy Endpoint URL
   (should look like: https://mycompany.openai.azure.com/)

OPENAI_DEPLOYMENT_NAME
└─ Usually "gpt-4o" or "gpt-4" - check your Azure deployment
```

---

### **STEP 4: DEPLOY** (2 min)

1. **Scroll to Bottom**
2. **Click "Create Web Service"**
3. **Watch the Magic:**

```
Building your service...
Cloning repository...
Installing dependencies...
Running build command...
✓ Build successful
Deploying...
✓ Deployment successful
```

**Wait 2-5 minutes for deployment to complete**

---

### **STEP 5: GET YOUR URL** (1 min)

Once deployed:

1. **In Render Dashboard:**
   - See your service: `retail-marketing-agent`
   - At the top: Your live URL
   - Example: `https://retail-marketing-agent-abc123.onrender.com`

2. **Copy This URL:**
   - You'll use it to test your API
   - Share it with frontend apps
   - This is your public API!

---

## 🧪 TESTING YOUR DEPLOYMENT

### **TEST 1: Health Check** (Should be instant)

```powershell
# Replace with your actual URL
$URL = "https://retail-marketing-agent-XXX.onrender.com"

# Test health endpoint
curl "$URL/api/health" -v
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T10:30:45.123456",
  "service": "Retail Marketing Agent API"
}
```

**Status should be:** ✅ **200 OK**

---

### **TEST 2: Initialize Agent** (5-10 seconds first time)

```powershell
$URL = "https://retail-marketing-agent-XXX.onrender.com"

$body = @{
    client_name = "Fashion Store NYC"
    store_type = "fashion"
    location = "New York"
    has_online_store = $true
} | ConvertTo-Json

curl -X POST "$URL/api/initialize" `
  -H "Content-Type: application/json" `
  -Body $body -v
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

**Status should be:** ✅ **201 Created**

---

### **TEST 3: Generate Campaign** (10-15 seconds)

```powershell
$URL = "https://retail-marketing-agent-XXX.onrender.com"

$body = @{
    agent_id = "agent_Fashion_Store_NYC_1705840200"
    goal_type = "customer_acquisition"
    target = "Increase foot traffic by 30%"
    budget = 5000
} | ConvertTo-Json

curl -X POST "$URL/api/generate-campaign" `
  -H "Content-Type: application/json" `
  -Body $body -v
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

**Status should be:** ✅ **201 Created**

---

## 📊 MONITOR YOUR API

### **View Logs**

1. **In Render Dashboard:**
   - Click your service
   - Click "Logs" tab
   - See real-time logs
   - Green text = Success
   - Red text = Errors

### **Check Status**

- **Green checkmark** = ✅ Running
- **Yellow** = ⚠️ Deploying
- **Red** = ❌ Error

### **View Metrics**

- Click "Metrics" tab
- See CPU, Memory, Network usage
- Should be minimal on free tier

---

## 🔄 MAKING CODE UPDATES

### **After Deployment, To Update Your Code:**

```powershell
# 1. Edit code locally
code render_app.py
# ... make changes ...

# 2. Test locally (optional)
python render_app.py

# 3. Commit and push
git add .
git commit -m "Updated campaign generation logic"
git push origin main

# 4. Watch in Render Dashboard
# Render detects the push and automatically redeploys!
```

---

## ⚡ COMMON ISSUES & FIXES

### **Issue: 502 Bad Gateway**

```
502 Bad Gateway - Something went wrong!
```

**Fix:**
1. Check Render logs for errors
2. Verify Start Command: `python render_app.py`
3. Verify Python version: 3.11 or 3.10
4. Check environment variables are set

---

### **Issue: 500 Error**

```
500 - Internal Server Error
```

**Fix:**
1. Check logs in Render dashboard
2. Verify OpenAI API key is correct
3. Verify OpenAI endpoint URL is complete
4. Test API key locally first

---

### **Issue: Deployment Fails**

```
Build failed / Build command failed
```

**Fix:**
1. Check build logs for specific error
2. Verify `requirements.txt` syntax
3. Common issues:
   - Missing package name
   - Wrong version specification
   - Typo in package name

---

### **Issue: API Very Slow on First Request**

```
First request takes 10-15 seconds
```

**This is NORMAL!** Reasons:
- Free tier service spins down after 15 min idle
- First request wakes it up (cold start)
- Subsequent requests: < 500ms
- **Solution:** Your Gradio UI keeps it warm

---

## 🎯 FINAL CHECKLIST

### **Before Deployment**
- [ ] Code pushed to GitHub
- [ ] `render_app.py` exists
- [ ] `Procfile` exists
- [ ] `requirements.txt` updated
- [ ] `.env.example` exists

### **During Deployment**
- [ ] Render service created
- [ ] 5 environment variables set
- [ ] Build succeeded (green)
- [ ] Service shows Active

### **After Deployment**
- [ ] `/api/health` returns 200
- [ ] `/api/initialize` works
- [ ] `/api/generate-campaign` works
- [ ] All endpoints respond < 500ms
- [ ] No errors in logs

---

## 📞 QUICK REFERENCE

| Action | Command/Steps |
|--------|---------------|
| **Test API** | `curl https://YOUR_URL/api/health` |
| **View Logs** | Render Dashboard → Logs tab |
| **Redeploy** | Push to GitHub (automatic) |
| **Manual Redeploy** | Render Dashboard → Manual deploy |
| **Check Status** | Render Dashboard → Status indicator |
| **Update Env Vars** | Render Dashboard → Environment |

---

## 🎉 YOU'RE DEPLOYED!

### **Your Live API:**
```
https://retail-marketing-agent-XXX.onrender.com/api
```

### **Available Now:**
- ✅ 7 REST API endpoints
- ✅ Real-time logging
- ✅ Auto-deploy on GitHub push
- ✅ HTTPS/SSL included
- ✅ Free tier ($0/month)

### **What's Next:**
1. **Keep monitoring** - Watch logs and metrics
2. **Share your API** - With frontend or partners
3. **Make code updates** - Push to GitHub, auto-redeploys
4. **Upgrade later** - If you outgrow free tier

---

## 📖 ADDITIONAL RESOURCES

| Resource | Link |
|----------|------|
| **Render Documentation** | https://render.com/docs |
| **Flask Documentation** | https://flask.palletsprojects.com |
| **This Project** | See: RENDER_DEPLOYMENT_GUIDE.md |
| **Azure OpenAI** | https://platform.openai.com/docs |

---

**🚀 Ready to deploy? Start from "STEP 1: CREATE RENDER ACCOUNT" above!**

**Questions?** See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for detailed help.
