# InternMail — Internship Campaign Manager

A local web app to generate, schedule, and track internship application emails.

---

## Features
- ✨ AI-generated personalized email content (Claude API)
- 📅 Schedule emails to be sent at any date/time
- 📎 Attach your CV (PDF) automatically
- 👁 Track email opens & how many times (with timestamps)
- 📊 Dashboard with campaign stats

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```
Open http://localhost:5000 in your browser.

---

## Configuration (Settings page)

| Field | Value |
|---|---|
| Sender email | chahine.ouledouhiba@enicar.ucar.tn |
| Your name | Chahine Ouled Ouhiba |
| App password | Gmail App Password (see below) |
| Gemini API key | From https://aistudio.google.com/app/apikey (free) |
| SMTP host | smtp.gmail.com |
| SMTP port | 587 |
| Tracking URL | Your ngrok public URL (see below) |

---

## Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Create a new app password → copy and paste into Settings

---

## Email Open Tracking

Open tracking works by embedding an invisible 1×1 pixel image served from this app.
The recipient's email client loads the image → the server records the open.

**To enable tracking from anywhere:**
1. Install ngrok: https://ngrok.com/download
2. Run: `ngrok http 5000`
3. Copy the public URL (e.g. `https://abc123.ngrok.io`)
4. Paste it into Settings → Tracking URL

The tracking pixel URL will be: `https://abc123.ngrok.io/track/<email-id>.gif`

> Note: Some email clients block remote images. Gmail, Outlook, and most mobile clients load them by default.

---

## Usage

1. **Settings** — Configure your email, app password, API keys, and tracking URL
2. **Compose** — Upload CV → paste company emails → generate with AI → schedule
3. **Campaigns** — View all emails, send now, see open counts and timestamps
4. **Dashboard** — Overview stats

---

## File Structure
```
internship_mailer/
├── app.py              # Flask backend + scheduler + SMTP
├── requirements.txt
├── templates/
│   └── index.html      # Full SPA frontend
├── data/
│   ├── emails.json     # Email records (auto-created)
│   └── config.json     # Your settings (auto-created)
└── uploads/            # Uploaded CVs
```
