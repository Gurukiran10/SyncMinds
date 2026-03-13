# 🚀 Setup Guide: OpenAI API for Meeting Transcription

## Step 1: Get Your OpenAI API Key

### Create OpenAI Account & Get API Key:

1. **Go to OpenAI Platform**: https://platform.openai.com/
2. **Sign up or Log in** to your account
3. **Navigate to API Keys**: Click on your profile → "View API Keys" or go to https://platform.openai.com/api-keys
4. **Create New Key**: Click "+ Create new secret key"
   - Name it something like "Meeting Intelligence Agent"
   - Copy the key immediately (you won't see it again!)
   - Format looks like: `sk-proj-...` or `sk-...`

### Pricing Information:
- **Whisper API** (transcription): ~$0.006 per minute
- **GPT-4** (analysis): ~$0.03 per 1K tokens
- Example: 1-hour meeting = ~$0.36 transcription + ~$0.50 analysis = **~$1 per hour**

## Step 2: Add API Key to Your Application

### Edit the `.env` file:

```bash
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
nano .env
```

### Update this line:
```dotenv
# Change from:
OPENAI_API_KEY=sk-your-openai-api-key-here

# To your actual key:
OPENAI_API_KEY=sk-proj-abc123youractualkeyhere
```

### Optional: Add Organization ID (if you have one):
```dotenv
OPENAI_ORG_ID=org-youractualorgid
```

Save and exit (Ctrl+O, Enter, Ctrl+X for nano)

## Step 3: Restart the Backend Server

The backend needs to reload the environment variables:

```bash
# Stop the current backend
lsof -ti :8000 | xargs kill -9

# Start it again
cd "/Applications/vs codee/meeting-intelligence-agent/backend"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the background version:
```bash
lsof -ti :8000 | xargs kill -9
cd "/Applications/vs codee/meeting-intelligence-agent/backend" && \
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
```

## Step 4: Test the Setup

### Upload a test recording:
1. Go to http://127.0.0.1:3001/meetings
2. Click "+ New Meeting" 
3. Fill in meeting details and save
4. Click on the meeting card to open details
5. Upload an audio/video file (MP3, WAV, M4A, MP4 supported)

### What happens:
- ✅ File uploads to server
- ✅ Whisper API transcribes the audio
- ✅ GPT-4 analyzes for:
  - Meeting summary
  - Action items
  - Key decisions
  - Sentiment analysis
  - Speaking time per participant

## Alternative: Use Free Demo Mode

If you don't want to set up OpenAI yet, you can:
- Upload meetings (files will be stored)
- Add transcripts manually
- Create action items manually
- Test all other features

The transcription will just show "pending" until you add an API key.

## Troubleshooting

### "Invalid API Key" error:
- Make sure you copied the entire key (starts with `sk-`)
- No quotes around the key in .env file
- No spaces before/after the key
- Restart backend after changing .env

### "Insufficient quota" error:
- Add payment method at https://platform.openai.com/account/billing
- Minimum $5 credit required
- Check usage at https://platform.openai.com/usage

### Transcription not starting:
- Check backend logs: `tail -50 /tmp/server.log`
- Verify API key is loaded: backend logs show "OpenAI initialized" on startup
- Check file format is supported (MP3, WAV, M4A, MP4)

## Cost Optimization Tips

1. **Test with short clips** first (1-2 minutes)
2. **Use GPT-3.5-turbo** for analysis instead of GPT-4 (edit in backend/app/services/)
3. **Enable caching** - summaries are stored in database
4. **Set spending limits** on OpenAI dashboard
