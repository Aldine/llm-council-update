# LLM Council - Complete Setup Guide

## ✅ Software Requirements (You Already Have These!)

- **Python 3.13.5** ✓ (Required: 3.10+)
- **Node.js v24.4.0** ✓ (Required: 14+)
- **uv 0.8.15** ✓ (Python package manager)

## 🔑 Step 1: Get Your OpenRouter API Key

**Why OpenRouter?** This project uses OpenRouter as a unified gateway to access multiple LLM providers (OpenAI, Anthropic, Google, xAI, etc.) with a single API key.

### Get API Key:
1. Visit **https://openrouter.ai/**
2. Click "Sign In" (top right) - you can use Google/GitHub login
3. After logging in, go to **Keys** section: https://openrouter.ai/keys
4. Click "Create Key" and give it a name (e.g., "LLM Council")
5. Copy the key (starts with `sk-or-v1-...`)

### Add Credits:
6. Go to **Credits**: https://openrouter.ai/credits
7. Add credits (recommended: start with $5-10)
8. Or enable "Auto Top-up" for convenience

## 🔧 Step 2: Configure Your Environment

I've created a `.env` file in your project root. **Open it and add your API key:**

```bash
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
```

**Important:** Replace `your_api_key_here` with the actual key you copied from OpenRouter.

## 📦 Step 3: Install Dependencies

Run these commands in your terminal:

```powershell
# Install Python dependencies (from project root)
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## 🎯 Step 4: Choose Your Models (Optional)

You can customize which AI models participate in the council. Edit `backend/config.py`:

```python
COUNCIL_MODELS = [
    "openai/gpt-5.2",              # OpenAI GPT-4.5 Turbo
    "google/gemini-3-pro-preview",  # Google Gemini 2.0 Pro
    "anthropic/claude-sonnet-4.5",  # Anthropic Claude 3.5 Sonnet
    "x-ai/grok-4",                  # xAI Grok Beta
]

CHAIRMAN_MODEL = "google/gemini-3-pro-preview"  # Synthesizes final answer
```

### Available Models on OpenRouter:

**OpenAI:**
- `openai/gpt-4o` - GPT-4o (faster, cheaper)
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/o1` - o1 (reasoning model)

**Anthropic:**
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet (latest)
- `anthropic/claude-3-opus` - Claude 3 Opus (most capable)

**Google:**
- `google/gemini-pro-1.5` - Gemini 1.5 Pro
- `google/gemini-flash-1.5` - Gemini 1.5 Flash (faster)

**Others:**
- `meta-llama/llama-3.1-70b-instruct` - Meta Llama 3.1
- `mistralai/mistral-large` - Mistral Large

Browse all models: https://openrouter.ai/models

## 🚀 Step 5: Start the Application

### Option A: Using the start script (recommended)
```powershell
# On Windows, use:
bash start.sh
```

### Option B: Manual (use two separate terminals)

**Terminal 1 - Backend:**
```powershell
uv run python -m backend.main
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 🌐 Step 6: Open in Browser

Visit: **http://localhost:5173**

The backend API will be running on: **http://localhost:8001**

## 🧪 Testing Your Setup

1. Click "New Conversation" in the sidebar
2. Ask a question like: "What is the capital of France?"
3. Watch the 3-stage process:
   - **Stage 1:** Each model responds individually
   - **Stage 2:** Models rank each other's responses (anonymized)
   - **Stage 3:** Chairman synthesizes the final answer

## ⚠️ Troubleshooting

### "Module not found" errors
```powershell
# Make sure you're in the project root and run:
uv sync
```

### "OPENROUTER_API_KEY not found"
- Check that `.env` file exists in project root
- Verify the API key is correct (starts with `sk-or-v1-`)
- No quotes needed around the key in `.env`

### CORS errors in browser
- Backend must be running on port 8001
- Frontend must be on port 5173
- Check `backend/main.py` CORS settings if you changed ports

### "Insufficient credits" error
- Add credits at https://openrouter.ai/credits
- Each query uses ~$0.01-0.10 depending on models chosen

## 💡 Cost Estimation

Approximate cost per query (with 4 models):
- **Stage 1:** 4 models × input/output tokens ≈ $0.04-0.08
- **Stage 2:** 4 models × ranking ≈ $0.04-0.08  
- **Stage 3:** 1 chairman × synthesis ≈ $0.01-0.02
- **Total per query:** ~$0.09-0.18

To reduce costs:
- Use fewer models (3 instead of 4)
- Choose cheaper models (GPT-4o Mini, Gemini Flash)
- Remove Stage 2 rankings (edit `backend/main.py`)

## 📚 Additional Resources

- **OpenRouter Docs:** https://openrouter.ai/docs
- **Model Pricing:** https://openrouter.ai/models (click any model to see pricing)
- **Project README:** See `README.md` in this folder
- **Architecture Details:** See `CLAUDE.md` for technical deep-dive

## 🎉 You're Ready!

Your system is now configured to run LLM Council. Enjoy deliberating with multiple AI models!
