"""
app.py  –  Client Hunter Dashboard  (Stephen Muema / Steve Kaks)
──────────────────────────────────────────────────────────────────
100% free Flask backend. No paid services required.
"""

import os, json, threading, time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from signal_detector import (
    load_signals, save_signals, scan_reddit_live,
    generate_demo_signals, get_stats,
)
from ai_reply import generate_reply, get_offer_card

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── Background scanner state ─────────────────────────────────────────────────
_scan_lock   = threading.Lock()
_scan_status = {"running": False, "last_run": None, "last_count": 0, "mode": "demo"}


def _run_scan():
    with _scan_lock:
        _scan_status["running"] = True
    try:
        new = scan_reddit_live()
        has_creds = bool(os.getenv("REDDIT_CLIENT_ID","").strip())
        _scan_status.update({
            "last_run":   datetime.now(timezone.utc).isoformat(),
            "last_count": len(new),
            "mode":       "live" if has_creds else "demo",
        })
    finally:
        with _scan_lock:
            _scan_status["running"] = False


def _start_auto_scan(interval_min: int = 15):
    def loop():
        while True:
            _run_scan()
            time.sleep(interval_min * 60)
    threading.Thread(target=loop, daemon=True).start()


# ════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ── Signals ──────────────────────────────────────────────────────────────────

@app.route("/api/signals")
def api_signals():
    signals       = load_signals()
    status_filter = request.args.get("status", "")
    sort_by       = request.args.get("sort", "urgency")   # urgency | date
    limit         = int(request.args.get("limit", 60))

    if status_filter and status_filter != "all":
        signals = [s for s in signals if s.get("status") == status_filter]

    if sort_by == "urgency":
        signals = sorted(signals, key=lambda s: s.get("urgency_score", 0), reverse=True)
    else:
        signals = sorted(signals, key=lambda s: s.get("detected_at", ""), reverse=True)

    return jsonify(signals[:limit])


@app.route("/api/signals/<sid>", methods=["GET"])
def api_signal_get(sid):
    sig = next((s for s in load_signals() if s["id"] == sid), None)
    return jsonify(sig) if sig else (jsonify({"error": "not found"}), 404)


@app.route("/api/signals/<sid>", methods=["DELETE"])
def api_signal_delete(sid):
    signals = [s for s in load_signals() if s["id"] != sid]
    save_signals(signals)
    return jsonify({"ok": True})


@app.route("/api/signals/<sid>/status", methods=["POST"])
def api_signal_status(sid):
    data   = request.get_json() or {}
    status = data.get("status", "")
    valid  = {"new", "drafted", "sent", "converted", "ignored"}
    if status not in valid:
        return jsonify({"error": f"status must be one of {valid}"}), 400
    signals = load_signals()
    for s in signals:
        if s["id"] == sid:
            s["status"] = status
            save_signals(signals)
            return jsonify({"ok": True, "signal": s})
    return jsonify({"error": "not found"}), 404


@app.route("/api/signals/<sid>/draft", methods=["POST"])
def api_signal_draft(sid):
    signals = load_signals()
    sig     = next((s for s in signals if s["id"] == sid), None)
    if not sig:
        return jsonify({"error": "not found"}), 404
    sig["ai_reply"] = generate_reply(sig)
    if sig["status"] == "new":
        sig["status"] = "drafted"
    save_signals(signals)
    return jsonify({"ok": True, "reply": sig["ai_reply"]})


@app.route("/api/signals/<sid>/offer")
def api_signal_offer(sid):
    sig = next((s for s in load_signals() if s["id"] == sid), None)
    if not sig:
        return jsonify({"error": "not found"}), 404
    return jsonify(get_offer_card(sig.get("detected_service", "General Help")))


# ── Bulk actions ──────────────────────────────────────────────────────────────

@app.route("/api/draft-all", methods=["POST"])
def api_draft_all():
    signals = load_signals()
    count   = 0
    for s in signals:
        if s["status"] == "new" and not s.get("ai_reply"):
            s["ai_reply"] = generate_reply(s)
            s["status"]   = "drafted"
            count += 1
    save_signals(signals)
    return jsonify({"ok": True, "drafted": count})


# ── Scanner ───────────────────────────────────────────────────────────────────

@app.route("/api/scan", methods=["POST"])
def api_scan():
    if _scan_status["running"]:
        return jsonify({"ok": False, "message": "Scan already running"})
    threading.Thread(target=_run_scan, daemon=True).start()
    return jsonify({"ok": True, "message": "Scan started"})


@app.route("/api/scan/demo", methods=["POST"])
def api_scan_demo():
    """Inject fresh demo signals — always works, zero credentials."""
    new = generate_demo_signals(5)
    return jsonify({"ok": True, "count": len(new)})


@app.route("/api/scan/status")
def api_scan_status():
    return jsonify(_scan_status)


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


# ── Settings ──────────────────────────────────────────────────────────────────

@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    return jsonify({
        "your_name":      os.getenv("YOUR_NAME",      "Stephen Muema (Steve Kaks)"),
        "your_email":     os.getenv("YOUR_EMAIL",     "musyokas753@gmail.com"),
        "your_phone":     os.getenv("YOUR_PHONE",     "+254-740-624-253"),
        "your_portfolio": os.getenv("YOUR_PORTFOLIO", "https://stephenmueama.com"),
        "your_linkedin":  os.getenv("YOUR_LINKEDIN",  "https://www.linkedin.com/in/stephen-muema-617339359"),
        "your_github":    os.getenv("YOUR_GITHUB",    "https://github.com/Kaks753"),
        "has_groq":       bool(os.getenv("GROQ_API_KEY","").strip()),
        "has_reddit":     bool(os.getenv("REDDIT_CLIENT_ID","").strip()),
    })


@app.route("/api/settings", methods=["POST"])
def api_settings_save():
    data     = request.get_json() or {}
    env_path = Path(__file__).parent / ".env"
    current  = env_path.read_text().splitlines() if env_path.exists() else []

    key_map = {
        "your_name":      "YOUR_NAME",
        "your_email":     "YOUR_EMAIL",
        "your_phone":     "YOUR_PHONE",
        "your_portfolio": "YOUR_PORTFOLIO",
        "your_linkedin":  "YOUR_LINKEDIN",
        "your_github":    "YOUR_GITHUB",
        "groq_api_key":   "GROQ_API_KEY",
        "reddit_client_id":     "REDDIT_CLIENT_ID",
        "reddit_client_secret": "REDDIT_CLIENT_SECRET",
    }
    updates = {key_map[k]: v for k, v in data.items() if k in key_map and v}

    new_lines, seen = [], set()
    for line in current:
        env_key = line.split("=")[0].strip()
        if env_key in updates:
            new_lines.append(f"{env_key}={updates[env_key]}")
            seen.add(env_key)
        else:
            new_lines.append(line)
    for k, v in updates.items():
        if k not in seen:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n")
    load_dotenv(override=True)
    return jsonify({"ok": True})


# ── Profile (for dashboard header) ───────────────────────────────────────────

@app.route("/api/profile")
def api_profile():
    return jsonify({
        "name":      os.getenv("YOUR_NAME",      "Stephen Muema (Steve Kaks)"),
        "email":     os.getenv("YOUR_EMAIL",     "musyokas753@gmail.com"),
        "phone":     os.getenv("YOUR_PHONE",     "+254-740-624-253"),
        "portfolio": os.getenv("YOUR_PORTFOLIO", "https://stephenmueama.com"),
        "linkedin":  os.getenv("YOUR_LINKEDIN",  "https://www.linkedin.com/in/stephen-muema-617339359"),
        "github":    os.getenv("YOUR_GITHUB",    "https://github.com/Kaks753"),
        "location":  os.getenv("YOUR_LOCATION",  "Kiambu, Kenya"),
    })


# ════════════════════════════════════════════════════════════════════════════
#  STARTUP
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not load_signals():
        print("[Startup] Seeding demo signals …")
        generate_demo_signals(10)

    _start_auto_scan(interval_min=15)

    print("\n" + "═" * 54)
    print("  🎯  CLIENT HUNTER  –  Steve Kaks Edition")
    print("  Running on  http://0.0.0.0:5000")
    print("  100% FREE  •  No paid APIs required")
    print("═" * 54 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
