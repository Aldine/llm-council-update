# 🚀 Quick Start - LLM Council

## ✅ Installation Complete!
All dependencies are installed. You're ready to go!

## 🔑 NEXT STEP: Add Your API Key

1. **Get your OpenRouter API key:**
   - Visit: https://openrouter.ai/keys
   - Sign in (Google/GitHub login available)
   - Click "Create Key"
   - Copy the key (starts with `sk-or-v1-...`)

2. **Add credits to your account:**
   - Visit: https://openrouter.ai/credits
   - Add $5-10 to start (each query costs ~$0.10-0.20)

3. **Edit the `.env` file:**
   - Open the `.env` file in this folder
   - Replace `your_api_key_here` with your actual key
   - Save the file

## 🎯 Start the Application

### Option 1: PowerShell (Two Terminals)

**Terminal 1 - Backend:**
```powershell
uv run python -m backend.main
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Option 2: Git Bash (Single Command)
```bash
bash start.sh
```

## 🌐 Open in Browser
Visit: **http://localhost:5173**

## 📊 Current Models Configured
- OpenAI GPT-5.1
- Google Gemini 3 Pro Preview
- Anthropic Claude Sonnet 4.5
- xAI Grok 4

**To change models:** Edit `backend/config.py`

## 💰 Cost Per Query
Approximately $0.09-0.18 per complete query (all 3 stages)

## ❓ Need Help?
- Full setup guide: `SETUP_GUIDE.md`
- Technical details: `CLAUDE.md`
- Project overview: `README.md`
