# 🔑 API Keys Setup Guide

## Required API Key: Google Gemini

The Automated Code Review Agent requires **ONLY ONE API key**: the **Google Gemini API key**.

---

## 📝 Step-by-Step Setup

### 1. Get Your Google Gemini API Key

#### Option A: Get Free API Key (Recommended for Testing)

1. **Go to Google AI Studio**:
   - Visit: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Sign in with your Google Account**

3. **Create API Key**:
   - Click "Get API key" or "Create API key"
   - Choose "Create API key in new project" (or select existing project)
   - Copy the generated key (starts with `AIza...`)

4. **Save the key** - You'll need it for the next step

#### Option B: Use Google Cloud Console (For Production)

1. Go to: https://console.cloud.google.com/
2. Create or select a project
3. Enable the **Generative Language API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the generated key

---

### 2. Configure Your .env File

#### Create the .env file:

```bash
# In the project directory, copy the template
copy .env.template .env
```

#### Edit the .env file:

Open `.env` in any text editor and add your API key:

```env
# ============================================
# REQUIRED: Google Gemini API Key
# ============================================
GOOGLE_API_KEY=AIzaSyD-9tSrke72URrkcEDnsXXXXXXXXXXX

# ============================================
# OPTIONAL: Model Selection
# ============================================
# Use Pro for better accuracy (slower, more expensive)
GEMINI_MODEL=gemini-1.5-pro-latest

# Or use Flash for speed (faster, cheaper)
# GEMINI_MODEL=gemini-1.5-flash-latest

# ============================================
# OPTIONAL: Advanced Settings
# ============================================
MAX_TOKENS_PER_REQUEST=100000
TEMPERATURE=0.1
MAX_FILE_SIZE_MB=5
LOG_LEVEL=INFO
```

**Replace `AIzaSyD-9tSrke72URrkcEDnsXXXXXXXXXXX` with your actual API key!**

---

### 3. Verify Your Setup

Run the verification script:

```bash
python verify_installation.py
```

You should see:
```
✅ Environment Config: PASS
✅ GOOGLE_API_KEY configured (40 characters)
```

---

## 🆓 API Pricing & Limits

### Free Tier (Google AI Studio)
- **60 requests per minute**
- **1,500 requests per day**
- **Perfect for testing and development**

### Gemini 1.5 Flash Pricing (Paid)
- **Input**: $0.075 / 1M tokens
- **Output**: $0.30 / 1M tokens
- Very affordable for most use cases

### Gemini 1.5 Pro Pricing (Paid)
- **Input**: $1.25 / 1M tokens
- **Output**: $5.00 / 1M tokens
- Better accuracy, higher cost

**For a typical code review of a 50-file project:**
- Cost: ~$0.10 - $0.50 USD
- Time: 2-5 minutes

---

## ❓ FAQ

### Q: Do I need any other API keys?
**A:** No! Only the Google Gemini API key is required.

### Q: What about Bandit and Radon?
**A:** These are installed locally via pip. No API keys needed.

### Q: Can I use OpenAI instead of Gemini?
**A:** The current implementation uses Gemini. You'd need to modify the agent code to use OpenAI.

### Q: Is the API key safe in the .env file?
**A:** Yes, if you:
- ✅ Keep `.env` in `.gitignore` (already configured)
- ✅ Never commit `.env` to version control
- ✅ Use environment variables in production

### Q: What if I hit rate limits?
**A:** 
- Use `gemini-1.5-flash-latest` (faster)
- Analyze smaller projects
- Upgrade to paid tier if needed

### Q: Can I use a free API key forever?
**A:** Google AI Studio free tier is great for:
- Testing and development
- Small projects
- Personal use

For production/heavy use, consider the paid tier.

---

## 🔒 Security Best Practices

### ✅ DO:
- Store API key in `.env` file
- Use environment variables
- Keep `.env` in `.gitignore`
- Rotate keys periodically
- Use separate keys for dev/prod

### ❌ DON'T:
- Hardcode API keys in code
- Commit `.env` to Git
- Share API keys publicly
- Use production keys for testing

---

## 🧪 Testing Your Setup

Once you've configured the API key:

```bash
# 1. Verify installation
python verify_installation.py

# 2. Run the demo (creates sample code and analyzes it)
python demo.py

# 3. Analyze the test project
python main.py --path test_project
```

---

## 📞 Troubleshooting

### Error: "GOOGLE_API_KEY not set"
**Solution:** 
- Verify `.env` file exists in project root
- Check that `GOOGLE_API_KEY=` line has your actual key
- Restart terminal after editing `.env`

### Error: "Invalid API key"
**Solution:**
- Get a new key from https://makersuite.google.com/app/apikey
- Ensure no extra spaces in `.env` file
- Key should start with `AIza`

### Error: "Quota exceeded"
**Solution:**
- Wait for quota to reset (1 minute for rate limit)
- Use `gemini-1.5-flash-latest` for fewer tokens
- Upgrade to paid tier

---

## ✅ Checklist

Before running the code review:

- [ ] Got API key from Google AI Studio
- [ ] Created `.env` file from template
- [ ] Added `GOOGLE_API_KEY=` with actual key
- [ ] Ran `python verify_installation.py` ✅
- [ ] All checks passed
- [ ] Ready to review code! 🚀

---

**That's it! You only need the Google Gemini API key to use the system.**

Get your key here: 🔗 **https://makersuite.google.com/app/apikey**
