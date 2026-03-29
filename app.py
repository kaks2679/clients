"""
app.py  –  Client Hunter v2  (Stephen Muema / Steve Kaks)
──────────────────────────────────────────────────────────
100% free Flask backend.

Key upgrade: settings saved to .env AND reloaded into os.environ immediately —
no restart needed after pasting API keys.
"""

import os, json, threading, time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv, dotenv_values

from signal_detector import (
    load_signals, save_signals,
    scan_reddit_live, scan_twitter_live,
    generate_demo_signals, get_stats, load_heatmap,
    scrape_reddit_url,
)
from ai_reply import generate_reply, generate_all_modes, get_offer_card

load_dotenv()

app = Flask(__name__)
CORS(app)

ENV_PATH = Path(__file__).parent / ".env"

# ── Background scanner state ──────────────────────────────────────────────────
_scan_lock   = threading.Lock()
_scan_status = {"running": False, "last_run": None, "last_count": 0, "mode": "demo"}


def _run_scan(sources=None):
    if sources is None:
        sources = ["reddit", "twitter"]
    with _scan_lock:
        _scan_status["running"] = True
    try:
        new = []
        if "reddit" in sources:
            new += scan_reddit_live()
        if "twitter" in sources:
            new += scan_twitter_live()
        has_reddit  = bool(os.getenv("REDDIT_CLIENT_ID","").strip())
        has_twitter = bool(os.getenv("TWITTER_BEARER_TOKEN","").strip())
        mode = "live" if (has_reddit or has_twitter) else "demo"
        _scan_status.update({
            "last_run":   datetime.now(timezone.utc).isoformat(),
            "last_count": len(new),
            "mode":       mode,
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


# ── Env hot-reload helper ─────────────────────────────────────────────────────
def _reload_env():
    """Re-read .env and push all values into os.environ immediately."""
    vals = dotenv_values(ENV_PATH)
    for k, v in vals.items():
        os.environ[k] = v or ""


# ════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ── Signals ───────────────────────────────────────────────────────────────────

@app.route("/api/signals")
def api_signals():
    signals       = load_signals()
    status_filter = request.args.get("status", "")
    tag_filter    = request.args.get("tag", "")
    source_filter = request.args.get("source", "")
    sort_by       = request.args.get("sort", "urgency")
    limit         = int(request.args.get("limit", 80))

    if status_filter and status_filter != "all":
        signals = [s for s in signals if s.get("status") == status_filter]
    if tag_filter and tag_filter != "all":
        signals = [s for s in signals if s.get("subject_tag","").lower() == tag_filter.lower()]
    if source_filter and source_filter != "all":
        signals = [s for s in signals if s.get("source","") == source_filter]

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
    valid  = {"new","drafted","sent","converted","ignored"}
    if status not in valid:
        return jsonify({"error": f"must be one of {valid}"}), 400
    signals = load_signals()
    for s in signals:
        if s["id"] == sid:
            s["status"] = status
            save_signals(signals)
            return jsonify({"ok": True, "signal": s})
    return jsonify({"error": "not found"}), 404


@app.route("/api/signals/<sid>/replied", methods=["POST"])
def api_signal_replied(sid):
    """Track whether the student replied back."""
    data    = request.get_json() or {}
    replied = data.get("replied_to")   # True | False | None
    signals = load_signals()
    for s in signals:
        if s["id"] == sid:
            s["replied_to"] = replied
            save_signals(signals)
            return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


@app.route("/api/signals/<sid>/draft", methods=["POST"])
def api_signal_draft(sid):
    """Generate one reply in requested mode."""
    data = request.get_json() or {}
    mode = data.get("mode", "urgent")  # urgent|longterm|group|lowkey|dm
    signals = load_signals()
    sig     = next((s for s in signals if s["id"] == sid), None)
    if not sig:
        return jsonify({"error": "not found"}), 404

    reply = generate_reply(sig, mode)
    # store by mode key
    if mode == "dm":
        sig["ai_dm"] = reply
    else:
        sig["ai_reply"] = reply
    sig["reply_mode"] = mode
    if sig["status"] == "new":
        sig["status"] = "drafted"
    save_signals(signals)
    return jsonify({"ok": True, "reply": reply, "mode": mode})


@app.route("/api/signals/<sid>/draft-all-modes", methods=["POST"])
def api_draft_all_modes(sid):
    """Generate all 5 reply variants at once."""
    signals = load_signals()
    sig     = next((s for s in signals if s["id"] == sid), None)
    if not sig:
        return jsonify({"error": "not found"}), 404
    variants = generate_all_modes(sig)
    sig["ai_reply"] = variants["urgent"]
    sig["ai_dm"]    = variants["dm"]
    sig["reply_variants"] = variants
    if sig["status"] == "new":
        sig["status"] = "drafted"
    save_signals(signals)
    return jsonify({"ok": True, "variants": variants})


@app.route("/api/signals/<sid>/offer")
def api_signal_offer(sid):
    sig = next((s for s in load_signals() if s["id"] == sid), None)
    if not sig:
        return jsonify({"error": "not found"}), 404
    return jsonify(get_offer_card(sig.get("detected_service","General Help")))


# ── Bulk ──────────────────────────────────────────────────────────────────────

@app.route("/api/draft-all", methods=["POST"])
def api_draft_all():
    signals = load_signals()
    count   = 0
    for s in signals:
        if s["status"] == "new" and not s.get("ai_reply"):
            s["ai_reply"] = generate_reply(s, "urgent")
            s["ai_dm"]    = generate_reply(s, "dm")
            s["status"]   = "drafted"
            count += 1
    save_signals(signals)
    return jsonify({"ok": True, "drafted": count})


# ── Scanner ───────────────────────────────────────────────────────────────────

@app.route("/api/scan", methods=["POST"])
def api_scan():
    if _scan_status["running"]:
        return jsonify({"ok": False, "message": "Scan already running"})
    data    = request.get_json() or {}
    sources = data.get("sources", ["reddit","twitter"])
    threading.Thread(target=_run_scan, args=(sources,), daemon=True).start()
    return jsonify({"ok": True, "message": f"Scanning {sources}…"})


@app.route("/api/scan/demo", methods=["POST"])
def api_scan_demo():
    data = request.get_json() or {}
    n    = int(data.get("n", 5))
    new  = generate_demo_signals(n)
    return jsonify({"ok": True, "count": len(new)})


@app.route("/api/scan/status")
def api_scan_status():
    return jsonify(_scan_status)


# ── Stats + heatmap ───────────────────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/heatmap")
def api_heatmap():
    return jsonify(load_heatmap())


# ── Settings  (hot-reload: no restart needed) ─────────────────────────────────

@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    _reload_env()
    return jsonify({
        "your_name":      os.getenv("YOUR_NAME",      "Stephen Muema (Steve Kaks)"),
        "your_email":     os.getenv("YOUR_EMAIL",     "musyokas753@gmail.com"),
        "your_phone":     os.getenv("YOUR_PHONE",     "+254-740-624-253"),
        "your_portfolio": os.getenv("YOUR_PORTFOLIO", "https://stephenmueama.com"),
        "your_linkedin":  os.getenv("YOUR_LINKEDIN",  "https://www.linkedin.com/in/stephen-muema-617339359"),
        "your_github":    os.getenv("YOUR_GITHUB",    "https://github.com/Kaks753"),
        "has_groq":       bool(os.getenv("GROQ_API_KEY","").strip()),
        "has_reddit":     bool(os.getenv("REDDIT_CLIENT_ID","").strip()),
        "has_twitter":    bool(os.getenv("TWITTER_BEARER_TOKEN","").strip()),
    })


@app.route("/api/settings", methods=["POST"])
def api_settings_save():
    data    = request.get_json() or {}
    current = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []

    key_map = {
        "your_name":             "YOUR_NAME",
        "your_email":            "YOUR_EMAIL",
        "your_phone":            "YOUR_PHONE",
        "your_portfolio":        "YOUR_PORTFOLIO",
        "your_linkedin":         "YOUR_LINKEDIN",
        "your_github":           "YOUR_GITHUB",
        "groq_api_key":          "GROQ_API_KEY",
        "reddit_client_id":      "REDDIT_CLIENT_ID",
        "reddit_client_secret":  "REDDIT_CLIENT_SECRET",
        "twitter_bearer_token":  "TWITTER_BEARER_TOKEN",
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

    ENV_PATH.write_text("\n".join(new_lines) + "\n")
    _reload_env()      # ← push into os.environ immediately, no restart needed
    return jsonify({"ok": True})


# ── Reddit URL paste → instant signal ────────────────────────────────────────

@app.route("/api/scrape_reddit_url", methods=["POST"])
def api_scrape_reddit_url():
    data = request.get_json() or {}
    url  = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400
    result = scrape_reddit_url(url)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"ok": True, "signal": result})


# ── Twitter search URLs (free — no API needed) ────────────────────────────────

TWITTER_SEARCH_QUERIES = [
    "pandas error deadline",
    "python homework help due",
    "thesis help deadline",
    "data analysis assignment help",
    "machine learning homework due",
    "statistics assignment help",
    "essay deadline help",
    "jupyter notebook error help",
    "sklearn help assignment",
    "csv cleaning help due",
]

@app.route("/api/twitter_search_urls")
def api_twitter_search_urls():
    import urllib.parse
    urls = []
    for q in TWITTER_SEARCH_QUERIES:
        encoded = urllib.parse.quote(q + " -is:retweet lang:en")
        urls.append({
            "query": q,
            "url": f"https://twitter.com/search?q={encoded}&src=typed_query&f=live",
            "nitter": f"https://nitter.net/search?q={urllib.parse.quote(q)}&f=tweets",
        })
    return jsonify(urls)


# ── WhatsApp click-to-chat link ───────────────────────────────────────────────

@app.route("/api/whatsapp_link")
def api_whatsapp_link():
    _reload_env()
    phone   = os.getenv("YOUR_PHONE", "+254-740-624-253").replace("-","").replace("+","")
    problem = request.args.get("problem", "data science or academic writing help")
    import urllib.parse
    msg = urllib.parse.quote(
        f"Hi Steve, I saw your post about {problem}. I need help with my assignment. Can you assist?"
    )
    return jsonify({"url": f"https://wa.me/{phone}?text={msg}"})


# ── Manual signal add ─────────────────────────────────────────────────────────

@app.route("/api/signals/add", methods=["POST"])
def api_signal_add():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    body  = data.get("body",  "").strip()
    url   = data.get("url",   "#")
    sub   = data.get("subreddit", "manual")
    src   = data.get("source",    "manual")
    if not title:
        return jsonify({"error": "title required"}), 400
    from signal_detector import _build_signal, _update_heatmap
    from datetime import datetime, timezone
    post = {"title": title, "body": body, "subreddit": sub,
            "author": "manual", "url": url, "reddit_score": 0,
            "source": src, "is_demo": False}
    sig  = _build_signal(post)
    existing = load_signals()
    save_signals([sig] + existing)
    _update_heatmap(datetime.now().hour)
    return jsonify({"ok": True, "signal": sig})


# ── Profile ───────────────────────────────────────────────────────────────────

@app.route("/api/profile")
def api_profile():
    _reload_env()
    return jsonify({
        "name":      os.getenv("YOUR_NAME",      "Stephen Muema (Steve Kaks)"),
        "email":     os.getenv("YOUR_EMAIL",     "musyokas753@gmail.com"),
        "phone":     os.getenv("YOUR_PHONE",     "+254-740-624-253"),
        "portfolio": os.getenv("YOUR_PORTFOLIO", "https://stephenmueama.com"),
        "linkedin":  os.getenv("YOUR_LINKEDIN",  "https://www.linkedin.com/in/stephen-muema-617339359"),
        "github":    os.getenv("YOUR_GITHUB",    "https://github.com/Kaks753"),
        "location":  os.getenv("YOUR_LOCATION",  "Kiambu, Kenya"),
    })


# ── Capabilities check (what's unlocked) ─────────────────────────────────────

@app.route("/api/capabilities")
def api_capabilities():
    _reload_env()
    return jsonify({
        "ai_replies":    bool(os.getenv("GROQ_API_KEY","").strip()),
        "reddit_scan":   bool(os.getenv("REDDIT_CLIENT_ID","").strip()),
        "twitter_scan":  bool(os.getenv("TWITTER_BEARER_TOKEN","").strip()),
        "demo_always":   True,
    })


# ════════════════════════════════════════════════════════════════════════════
#  STARTUP
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not load_signals():
        print("[Startup] Seeding demo signals…")
        generate_demo_signals(10)

    _start_auto_scan(interval_min=15)

    print("\n" + "═"*54)
    print("  🎯  CLIENT HUNTER v2  –  Steve Kaks Edition")
    print("  http://localhost:5000")
    print("  100% FREE  •  No paid APIs required")
    print("  Paste API keys in Settings → works instantly")
    print("═"*54 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
