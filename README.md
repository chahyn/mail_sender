# InternMail 📬
### Automated Internship Email Campaign Manager

A free, open-source tool to generate, schedule, and track internship application emails — powered by Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python) ![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask) ![Gemini](https://img.shields.io/badge/Gemini-AI-orange?logo=google) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- ✨ **AI-generated emails** — Gemini writes a personalized email for each company automatically
- 📋 **Bulk import** — paste dozens of company emails at once, one per line
- 📅 **Scheduling** — pick a date and time, emails send automatically
- 📎 **CV attachment** — your PDF is attached to every email
- 👁 **Open tracking** — see if and how many times each recipient opened your email, with timestamps
- 📊 **Dashboard** — live stats on sent, opened, scheduled, and failed emails

---

## Screenshots

> Dashboard · Compose · Campaigns · Tracking

*(add your own screenshots here)*

---

## Requirements

- Python 3.10+
- A Gmail account (or any SMTP provider)
- A free [Google Gemini API key](https://aistudio.google.com/app/apikey)
- A free [ngrok account](https://ngrok.com) *(only for open tracking)*

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/internmail.git
cd internmail

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open your browser at **http://localhost:8080**

---

## Configuration

On first run, go to **⚙️ Settings** in the sidebar and fill in:

| Field | Description |
|---|---|
| Sender email | Your email address |
| Your full name | Used in AI-generated emails |
| App password | Your Gmail App Password (see below) |
| Gemini API key | From [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — free |
| SMTP host | `smtp.gmail.com` for Gmail |
| SMTP port | `587` |
| Tracking URL | Your ngrok public URL (see below) |

---

## Gmail Setup (App Password)

> ⚠️ Do NOT use your normal Gmail password. You need an App Password.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Click **Create** → name it anything (e.g. "InternMail")
5. Copy the **16-character password** → paste it into Settings

> 🎓 **University email users:** Some university Google accounts disable App Passwords. If that's the case, use a personal `@gmail.com` account as the sender instead.

---

## Gemini API Key (Free)

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy and paste it into Settings

The free tier is enough for generating hundreds of emails.

---

## Open Tracking Setup (ngrok)

Open tracking works by embedding an invisible pixel image in each email. When the recipient opens the email, their client loads the image from your server — recording the open with a timestamp.

To make this work from anywhere:

```bash
# 1. Download ngrok from https://ngrok.com/download
# 2. Sign up for a free account and get your auth token
# 3. Run in a second terminal (keep it open alongside app.py):

ngrok config add-authtoken YOUR_TOKEN_HERE
ngrok http 8080
```

4. Copy the URL ngrok gives you, e.g. `https://abc123.ngrok-free.app`
5. Paste it into **Tracking URL** in Settings → Save

> Keep both `python app.py` and `ngrok` running at the same time.
> Some email clients block remote images — Gmail, Outlook, and most mobile clients load them by default.

---

## Usage

### 1. Compose & Send
1. Go to **Compose**
2. Upload your CV (PDF)
3. Paste company emails — one per line or comma-separated
4. Optionally add a company name hint and a note about yourself for the AI
5. Click **✨ Generate with AI** — Gemini writes a personalized email
6. Edit the subject and body if needed
7. Pick a **send date & time**
8. Click **📅 Schedule** or **⚡ Send Now**

### 2. Track Opens
- Go to **Campaigns** to see all emails and their status
- Once a recipient opens your email, a green **👁 opens** badge appears
- Click **📊 Details** to see exact open timestamps

### 3. Dashboard
- Overview of sent, opened, scheduled, and failed counts
- Recent activity feed

---

## Running 24/7 (so scheduled emails send even when your laptop is off)

By default the app only runs while your terminal is open. To keep it running permanently:

**Option A — Deploy to Railway (free, recommended)**
1. Push your project to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Set your environment or config through the Settings page after deployment

**Option B — Keep your machine on**
- Set your PC sleep settings to "Never"
- Keep the terminal open with `python app.py` running

---

## File Structure

```
internmail/
├── app.py                  # Flask backend — SMTP, scheduler, tracking, API
├── requirements.txt
├── templates/
│   └── index.html          # Full single-page frontend
├── data/
│   ├── emails.json         # Email records (auto-created)
│   └── config.json         # Your settings (auto-created, gitignored)
└── uploads/                # Uploaded CVs (gitignored)
```

---

## .gitignore

Make sure to add this `.gitignore` so your credentials are never pushed to GitHub:

```
data/config.json
uploads/
__pycache__/
*.pyc
.env
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Port already in use | Change `port=8080` to another port in `app.py` |
| `SMTPAuthenticationError` | You used your real password — use the App Password instead |
| Emails not sending on schedule | Make sure `python app.py` is still running in the terminal |
| Gemini `429 RESOURCE_EXHAUSTED` | Wait 1 minute (free tier rate limit) and try again |
| Tracking not working | Make sure ngrok is running and the URL is saved in Settings |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |

---

## Tech Stack

- **Backend** — Python, Flask
- **Email** — smtplib (SMTP), MIME
- **AI** — Google Gemini 2.0 Flash Lite via `google-genai`
- **Scheduling** — Python threading + time.sleep
- **Tracking** — 1×1 GIF pixel served by Flask
- **Frontend** — Vanilla HTML/CSS/JS (single file, no framework)

---

## License

MIT — free to use, modify, and distribute.

---

## Contributing

Pull requests are welcome! If you find a bug or want to add a feature, open an issue first to discuss it.
