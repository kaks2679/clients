# 🎯 Client Hunter v2 — Steve Kaks

A **100% free** student client acquisition system for Stephen Muema.  
Scans Reddit + Twitter/X for students who need exactly what you offer — then AI-drafts the perfect reply.

---

## 🚀 Run on Your Laptop

### Mac / Linux
```bash
git clone https://github.com/kaks2679/clients.git
cd clients
chmod +x run.sh
./run.sh
```

### Windows
```
git clone https://github.com/kaks2679/clients.git
cd clients
Double-click run_windows.bat
```

Then open **http://localhost:5000** in your browser.

---

## 🔑 Free API Keys (Unlock Full Power)

All three are 100% free. No credit card.

| Key | Where to get it | What it unlocks |
|-----|----------------|----------------|
| **Groq** | [console.groq.com](https://console.groq.com) | AI reply drafts (smarter, personalised) |
| **Reddit Client ID + Secret** | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) → Create App → "script" | Live Reddit scanning |
| **Twitter Bearer Token** | [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard) | Live Twitter/X scanning |

**How to add keys:** Open the dashboard → click **Settings** → paste keys → **Save**. Works instantly, no restart.

---

## 💡 Features

| Feature | Description |
|---------|-------------|
| 🎯 **Signal Detection** | Scans 12 subreddits + 7 Twitter queries for urgent student posts |
| 🔥 **Urgency Scoring** | Every signal scored 0–99. "Due in 3 hours" scores higher than "due next week" |
| 🤖 **AI Reply Drafts** | 5 modes: Urgent, Long-term, Group, Low-key (anti-ban), DM |
| 📋 **Copy + Open** | Copy reply, then open the Reddit post — all in one click |
| 📊 **Subject Tags** | Data Science / Writing / Debugging — filter by what you want to work on |
| ✅ **Reply Tracking** | Track "Did they reply?" — measure your response rate |
| 🔄 **Status Tracking** | New → Drafted → Sent → Converted — full pipeline visibility |
| 🌡️ **Heat Map** | Post volume by hour — know exactly when to be online |
| 🐦 **Twitter/X Scanning** | Students tweet things like "pandas is ruining my life" — catch them |
| 🔒 **Low-key Mode** | Replies with no promo link — safe for strict subreddits |
| ⚡ **Instant Key Load** | Paste API key → works immediately, no server restart |

---

## 🛡️ Reddit Anti-Ban Strategy

- **Use Low-key mode** for `r/HomeworkHelp` — sounds like a helpful classmate, no portfolio link
- **Use Urgent/DM mode** for `r/learnpython`, `r/datascience`, `r/college` — more open to offers
- Reply to max **5–10 posts per session** — don't spam
- Always give genuine value in the first 1–2 sentences

---

## 🌙 The Sunday Night Strategy

Be online **9 PM – midnight** on Sundays.  
That's when students panic before Monday deadlines.  
Open the dashboard → Scan Reddit → Reply to top 5 hot signals → Wait for DMs.  
Takes 15 minutes. Can net you **$50–200 per session**.

---

## 📁 Project Structure

```
client-hunter/
├── app.py              # Flask server + API endpoints
├── signal_detector.py  # Reddit + Twitter scanner + demo signals
├── ai_reply.py         # 5-mode reply generator (Groq + local templates)
├── templates/
│   └── index.html      # Full dashboard UI
├── data/
│   ├── signals.json    # All detected signals (auto-created)
│   └── heatmap.json    # Hour-of-day activity data (auto-created)
├── .env                # Your credentials (never commit this)
├── requirements.txt    # Python dependencies
├── run.sh              # Mac/Linux launcher
└── run_windows.bat     # Windows launcher
```

---

## 💰 Service Pricing Reference

| Service | Price | Turnaround |
|---------|-------|------------|
| Python Error Fix | $15–25 | ~1 hour |
| Data Cleaning | $35–50 | 2 hours |
| Data Visualization | $30–45 | 90 min |
| Statistics Help | $40–60 | 2 hours |
| Machine Learning | $75–100 | 3–5 hours |
| Full Data Analysis | $50–75 | 2–4 hours |
| Essay / Thesis | $25–50 | Same day |

---

Built by Stephen Muema (Steve Kaks) | [stephenmueama.com](https://stephenmueama.com)
