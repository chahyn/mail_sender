import os, json, uuid, smtplib, threading, time, base64, logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify, send_file, render_template, Response
from google import genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)
DATA_FILE  = "data/emails.json"
CONF_FILE  = "data/config.json"
UPLOAD_DIR = "uploads"

# ── persistence helpers ────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def load_config():
    if not os.path.exists(CONF_FILE):
        return {}
    with open(CONF_FILE) as f:
        return json.load(f)

def save_config(c):
    with open(CONF_FILE, "w") as f:
        json.dump(c, f, indent=2)

# ── tracking pixel ─────────────────────────────────────────────────────────────
PIXEL_B64 = (
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)

@app.route("/track/<email_id>.gif")
def track_open(email_id):
    emails = load_data()
    for e in emails:
        if e["id"] == email_id:
            e["opens"] = e.get("opens", 0) + 1
            e["open_times"] = e.get("open_times", [])
            e["open_times"].append(datetime.now().isoformat())
            e["status"] = "opened"
            log.info(f"📬 Email {email_id} opened — total: {e['opens']}")
            break
    save_data(emails)
    pixel = base64.b64decode(PIXEL_B64)
    return Response(pixel, mimetype="image/gif",
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate",
                             "Pragma": "no-cache", "Expires": "0"})

# ── AI mail generation ──────────────────────────────────────────────────────────
def generate_email_content(company_email, company_name, sender_name, extra_info, api_key):
    client = genai.Client(api_key=api_key)
    prompt = f"""You are helping a student write a professional internship application email.

Student name: {sender_name}
Target company email: {company_email}
Company name (guessed from email domain if unknown): {company_name or company_email.split('@')[-1].split('.')[0].capitalize()}
Extra context from student: {extra_info or 'None'}

Write a concise, professional, and personalized internship application email.
Return ONLY a JSON object with exactly two keys:
- "subject": the email subject line
- "body": the full HTML email body (use simple HTML: <p>, <br>, <strong> tags only)

The email must:
- Be warm, confident, and specific to the company
- Mention that the CV is attached
- Be 150-200 words max
- End with a professional sign-off using the student's name

Return ONLY the JSON, no markdown, no explanation."""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    raw = response.text.strip()
    # strip possible markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── email sending ───────────────────────────────────────────────────────────────
def send_email(entry, config, tracking_base_url):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = config["sender_email"]
        msg["To"]      = entry["to"]
        msg["Subject"] = entry["subject"]

        tracking_pixel = ""
        if tracking_base_url:
            tracking_pixel = (
                f'<img src="{tracking_base_url}/track/{entry["id"]}.gif" '
                f'width="1" height="1" style="display:none" alt="" />'
            )

        html_body = entry["body"] + tracking_pixel
        msg.attach(MIMEText(html_body, "html"))

        # attach CV
        cv_path = entry.get("cv_path", "")
        if cv_path and os.path.exists(cv_path):
            with open(cv_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(cv_path)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            msg.attach(part)

        smtp_host = config.get("smtp_host", "smtp.gmail.com")
        smtp_port = int(config.get("smtp_port", 587))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(config["sender_email"], config["app_password"])
            server.sendmail(config["sender_email"], entry["to"], msg.as_string())

        log.info(f"✅ Sent to {entry['to']}")
        return True
    except Exception as ex:
        log.error(f"❌ Failed to send to {entry['to']}: {ex}")
        return False

# ── scheduler loop ──────────────────────────────────────────────────────────────
def check_and_send_scheduled():
    config = load_config()
    if not config:
        return
    tracking_url = config.get("tracking_url", "").rstrip("/")
    emails = load_data()
    now = datetime.now()
    changed = False
    for e in emails:
        if e.get("status") == "scheduled":
            try:
                send_at = datetime.fromisoformat(e["send_at"].replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                continue
            if now >= send_at:
                log.info(f"⏰ Time reached for {e['to']} — sending now...")
                ok = send_email(e, config, tracking_url)
                e["status"] = "sent" if ok else "failed"
                e["sent_at"] = now.isoformat()
                changed = True
    if changed:
        save_data(emails)

def scheduler_loop():
    log.info("🕐 Scheduler started — checking every 30 seconds")
    check_and_send_scheduled()  # run immediately on startup
    while True:
        time.sleep(30)
        try:
            check_and_send_scheduled()
        except Exception as ex:
            log.error(f"Scheduler error: {ex}")

# ── API routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config", methods=["GET", "POST"])
def config_route():
    if request.method == "GET":
        c = load_config()
        # never expose password
        safe = {k: v for k, v in c.items() if k != "app_password"}
        safe["has_password"] = bool(c.get("app_password"))
        safe["has_api_key"]  = bool(c.get("gemini_api_key"))
        return jsonify(safe)
    data = request.json
    c = load_config()
    for key in ["sender_email", "sender_name", "smtp_host", "smtp_port",
                "tracking_url", "app_password", "gemini_api_key"]:
        if key in data and data[key] != "":
            c[key] = data[key]
    save_config(c)
    return jsonify({"ok": True})

@app.route("/api/upload-cv", methods=["POST"])
def upload_cv():
    f = request.files.get("cv")
    if not f:
        return jsonify({"error": "No file"}), 400
    path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(path)
    return jsonify({"path": path, "name": f.filename})

@app.route("/api/generate", methods=["POST"])
def generate():
    data   = request.json
    config = load_config()
    api_key = config.get("gemini_api_key")
    if not api_key:
        return jsonify({"error": "Anthropic API key not set in settings"}), 400
    try:
        result = generate_email_content(
            data["to"], data.get("company_name", ""),
            config.get("sender_name", "Student"), data.get("extra_info", ""),
            api_key
        )
        return jsonify(result)
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.route("/api/emails", methods=["GET"])
def list_emails():
    return jsonify(load_data())

@app.route("/api/emails", methods=["POST"])
def create_email():
    data   = request.json
    config = load_config()
    entry  = {
        "id":        str(uuid.uuid4()),
        "to":        data["to"],
        "subject":   data["subject"],
        "body":      data["body"],
        "company":   data.get("company", ""),
        "cv_path":   data.get("cv_path", ""),
        "send_at":   data["send_at"],
        "status":    "scheduled",
        "opens":     0,
        "open_times":[],
        "created_at": datetime.now().isoformat()
    }
    emails = load_data()
    emails.append(entry)
    save_data(emails)
    log.info(f"📅 Scheduled email to {entry['to']} at {entry['send_at']}")
    return jsonify({"ok": True, "id": entry["id"]})

@app.route("/api/emails/<email_id>", methods=["DELETE"])
def delete_email(email_id):
    emails = [e for e in load_data() if e["id"] != email_id]
    save_data(emails)
    return jsonify({"ok": True})

@app.route("/api/emails/<email_id>/send-now", methods=["POST"])
def send_now(email_id):
    config = load_config()
    tracking_url = config.get("tracking_url", "").rstrip("/")
    emails = load_data()
    for e in emails:
        if e["id"] == email_id:
            ok = send_email(e, config, tracking_url)
            e["status"] = "sent" if ok else "failed"
            e["sent_at"] = datetime.now().isoformat()
            save_data(emails)
            return jsonify({"ok": ok})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/stats")
def stats():
    emails = load_data()
    return jsonify({
        "total":     len(emails),
        "scheduled": sum(1 for e in emails if e["status"] == "scheduled"),
        "sent":      sum(1 for e in emails if e["status"] in ("sent", "opened")),
        "opened":    sum(1 for e in emails if e["status"] == "opened"),
        "failed":    sum(1 for e in emails if e["status"] == "failed"),
    })

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    log.info("🚀 Internship Mailer running → http://localhost:8080")
    app.run(debug=False, port=8080, use_reloader=False)