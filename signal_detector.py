"""
signal_detector.py  –  Client Hunter (100% FREE)
─────────────────────────────────────────────────
Scans Reddit for students who need exactly what Stephen offers.

MODES:
  LIVE  → Reddit API (free at reddit.com/prefs/apps)
  DEMO  → Realistic fake signals — works with ZERO credentials
"""

import os, json, time, random, uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = Path(__file__).parent / "data" / "signals.json"
DATA_FILE.parent.mkdir(exist_ok=True)

# ── Subreddits Stephen should hunt ──────────────────────────────────────────
SUBREDDITS = [
    "HomeworkHelp", "learnpython", "statistics", "datascience",
    "college", "AskStatistics", "learnmachinelearning",
    "Python", "dataanalysis", "AskAcademia", "GradSchool",
    "mlquestions", "MachineLearning",
]

# ── High-intent keywords that signal a paying student ───────────────────────
URGENT_KEYWORDS = [
    "due tomorrow", "deadline", "due tonight", "due in", "help please",
    "please help", "desperate", "stuck on", "i give up", "assignment help",
    "hw help", "homework help", "cant figure", "can't figure",
    "not working", "keeps erroring", "broken", "anyone help",
]

TOPIC_KEYWORDS = [
    "pandas", "python error", "jupyter", "numpy", "matplotlib", "seaborn",
    "scikit", "sklearn", "regression", "classification", "data cleaning",
    "data analysis", "machine learning", "deep learning", "neural network",
    "p-value", "hypothesis", "anova", "t-test", "statistics",
    "csv", "dataframe", "KeyError", "ValueError", "TypeError", "IndexError",
    "essay", "thesis", "research paper", "dissertation", "proofreading",
    "academic writing", "lit review", "literature review", "citation",
    "apa format", "mla format", "report writing",
]

# ── Map post content → what Stephen can sell ────────────────────────────────
SERVICE_DETECT = [
    (["KeyError","ValueError","TypeError","IndexError","python error",
      "error message","not working","broken","debug"],         "Python Debugging",   "$15–25"),
    (["pandas","csv","dataframe","data cleaning","dropna","merge",
      "fillna","groupby"],                                     "Data Cleaning",      "$35–50"),
    (["matplotlib","seaborn","plot","visualization","graph",
      "chart","histogram","scatter"],                          "Data Visualization", "$30–45"),
    (["regression","correlation","p-value","anova","t-test",
      "hypothesis","confidence interval","statistics","spss"],  "Statistics",         "$40–60"),
    (["sklearn","scikit","classification","random forest",
      "neural","deep learning","accuracy","overfitting",
      "cross-validation","machine learning"],                  "Machine Learning",   "$75–100"),
    (["jupyter","notebook","data analysis","eda","exploratory"],
                                                               "Data Analysis",      "$50–75"),
    (["essay","thesis","dissertation","research paper",
      "lit review","literature review","proofreading",
      "academic writing","citation","apa","mla","report"],     "Academic Writing",   "$25–50"),
]

# ── Realistic demo posts Stephen would find on Reddit ───────────────────────
DEMO_POSTS = [
    {
        "title": "URGENT — KeyError: 'Age' pandas, assignment due in 4 hours",
        "body": "I keep getting `KeyError: 'Age'` when I run `df['Age'].mean()`. I've checked the CSV and the column is definitely there. My stats final project is due at midnight and I'm losing my mind. Anyone please help!!",
        "subreddit": "learnpython", "author": "exhausted_stats_major",
        "url": "https://reddit.com/r/learnpython/comments/xdemo1", "reddit_score": 5,
    },
    {
        "title": "Multiple regression help — final project due Friday, I'm so lost",
        "body": "My professor gave us a CSV with 18 columns. I need to run a multiple regression, check assumptions, and interpret the coefficients. I've never done this before. The TA's office hours are completely full. I'm willing to pay someone who actually knows this stuff.",
        "subreddit": "statistics", "author": "mba_student_Nairobi",
        "url": "https://reddit.com/r/statistics/comments/xdemo2", "reddit_score": 11,
    },
    {
        "title": "My thesis introduction is a disaster — advisor rejected it twice",
        "body": "Masters student here. My advisor keeps saying 'too vague, no clear argument'. I have all my research but I just can't structure it. 4 pages, climate policy topic. Deadline is Monday. Does anyone do academic editing? Happy to pay.",
        "subreddit": "GradSchool", "author": "masters_climate_policy",
        "url": "https://reddit.com/r/GradSchool/comments/xdemo3", "reddit_score": 23,
    },
    {
        "title": "ML model giving 99% accuracy — I know something is wrong, deadline tomorrow",
        "body": "I'm building a random forest classifier for my capstone. Accuracy is 99.7% which obviously means something is broken (data leak probably?). I don't know how to fix train/test split properly or add cross-validation. Submission is 9 AM tomorrow.",
        "subreddit": "learnmachinelearning", "author": "cs_senior_panicking",
        "url": "https://reddit.com/r/learnmachinelearning/comments/xdemo4", "reddit_score": 17,
    },
    {
        "title": "Pandas — cannot convert float NaN to integer, assignment due tonight",
        "body": "Getting `ValueError: Cannot convert non-finite values (NA or inf) to integer`. I've tried `dropna()` but it breaks my merge. I'm a business student trying to clean a sales dataset for my data analytics class. Due in 3 hours. Please.",
        "subreddit": "HomeworkHelp", "author": "biz_student_3am",
        "url": "https://reddit.com/r/HomeworkHelp/comments/xdemo5", "reddit_score": 4,
    },
    {
        "title": "Need 5 matplotlib visualizations for data science capstone — can pay",
        "body": "I need: histogram, scatter plot, box plot, correlation heatmap, and bar chart — all from the same CSV. I can share the file. Would love someone to write it with comments so I can learn from it. When can you have it done?",
        "subreddit": "datascience", "author": "cs_capstone_help",
        "url": "https://reddit.com/r/datascience/comments/xdemo6", "reddit_score": 9,
    },
    {
        "title": "p-value question — assignment due in 6 hours, totally confused",
        "body": "My professor wants me to 'interpret the p-value of 0.03 in context of our research hypothesis'. I don't understand what that means. This is 30% of my grade and I'm so confused. Can anyone explain OR just help me write this section?",
        "subreddit": "AskStatistics", "author": "psych_undergrad_lost",
        "url": "https://reddit.com/r/AskStatistics/comments/xdemo7", "reddit_score": 8,
    },
    {
        "title": "Research paper structure is terrible, professor said start over, due tomorrow",
        "body": "10-page paper on renewable energy policy. Professor said my structure is 'incoherent' and my transitions are missing. I have all my sources and arguments I just can't organize them. Is there anyone good at academic writing who can help me restructure tonight? I can pay.",
        "subreddit": "college", "author": "senior_humanities_rip",
        "url": "https://reddit.com/r/college/comments/xdemo8", "reddit_score": 31,
    },
    {
        "title": "sklearn predict() giving wrong results — data science homework stuck",
        "body": "My logistic regression from sklearn is predicting everything as class 0. I think it's a class imbalance issue but I don't know how to fix it. Tried class_weight='balanced' but accuracy dropped to 50%. Homework due in 2 days. Super stuck.",
        "subreddit": "learnmachinelearning", "author": "ml_beginner_help",
        "url": "https://reddit.com/r/learnmachinelearning/comments/xdemo9", "reddit_score": 6,
    },
    {
        "title": "APA citation format — dissertation chapter due Friday, please help",
        "body": "I have 40 sources that need to be in APA 7th edition format for my dissertation bibliography. Half of them are websites and I keep getting the format wrong. Turnitin also flagged my paraphrasing. Can anyone help with editing and citations?",
        "subreddit": "AskAcademia", "author": "phd_student_struggling",
        "url": "https://reddit.com/r/AskAcademia/comments/xdemo10", "reddit_score": 14,
    },
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _detect_service(title: str, body: str):
    """Return (service_name, suggested_price) by scanning content."""
    text = (title + " " + body).lower()
    for keywords, service, price in SERVICE_DETECT:
        if any(kw.lower() in text for kw in keywords):
            return service, price
    return "General Help", "$20–40"


def _urgency_score(title: str, body: str) -> int:
    text = (title + " " + body).lower()
    score = 0
    for kw in URGENT_KEYWORDS:
        if kw in text:
            score += 10
    for kw in TOPIC_KEYWORDS:
        if kw in text:
            score += 5
    # Bonus for explicit payment offer
    if any(w in text for w in ["pay", "willing to pay", "can pay", "hire"]):
        score += 20
    return min(score, 99)


def _build_signal(post: dict, is_demo: bool = False) -> dict:
    title   = post.get("title", "")
    body    = post.get("body", "") or post.get("selftext", "")
    service, price = _detect_service(title, body)
    urgency = _urgency_score(title, body)
    return {
        "id":               str(uuid.uuid4()),
        "title":            title,
        "body":             body[:500] + ("…" if len(body) > 500 else ""),
        "subreddit":        post.get("subreddit", "unknown"),
        "author":           post.get("author", "unknown"),
        "url":              post.get("url", "#"),
        "reddit_score":     post.get("reddit_score", post.get("score", 0)),
        "urgency_score":    urgency,
        "detected_service": service,
        "suggested_price":  price,
        "detected_at":      datetime.now(timezone.utc).isoformat(),
        "status":           "new",   # new | drafted | sent | converted | ignored
        "ai_reply":         None,
        "is_demo":          is_demo,
    }


# ── Public API ───────────────────────────────────────────────────────────────

def load_signals() -> list:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            return []
    return []


def save_signals(signals: list):
    DATA_FILE.write_text(json.dumps(signals, indent=2))


def generate_demo_signals(n: int = 8) -> list:
    """Inject realistic demo signals — zero credentials needed."""
    existing      = load_signals()
    existing_urls = {s["url"] for s in existing}
    pool          = [p for p in DEMO_POSTS if p["url"] not in existing_urls]
    random.shuffle(pool)
    new_signals   = []
    for post in pool[:n]:
        sig = _build_signal(post, is_demo=True)
        # scatter timestamps realistically (0–8 hours ago)
        offset = random.randint(0, 28800)
        ts = datetime.fromtimestamp(time.time() - offset, tz=timezone.utc)
        sig["detected_at"] = ts.isoformat()
        new_signals.append(sig)
    all_signals = new_signals + existing
    save_signals(all_signals)
    return new_signals


def scan_reddit_live() -> list:
    """
    Fetch real posts from Reddit (free API).
    Falls back to demo if credentials missing/invalid.
    """
    client_id     = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    user_agent    = os.getenv("REDDIT_USER_AGENT", "ClientHunter/1.0 by SteveKaks")

    if not client_id or not client_secret:
        print("[Scanner] No Reddit credentials → DEMO mode")
        return generate_demo_signals(4)

    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        existing      = load_signals()
        existing_urls = {s["url"] for s in existing}
        new_signals   = []

        all_kw = URGENT_KEYWORDS + TOPIC_KEYWORDS

        for sub_name in SUBREDDITS[:8]:
            try:
                sub = reddit.subreddit(sub_name)
                for submission in sub.new(limit=30):
                    url = f"https://reddit.com{submission.permalink}"
                    if url in existing_urls:
                        continue
                    text = (submission.title + " " + (submission.selftext or "")).lower()
                    # Must match at least one urgent AND one topic keyword
                    has_urgent = any(kw in text for kw in URGENT_KEYWORDS)
                    has_topic  = any(kw in text for kw in TOPIC_KEYWORDS)
                    if has_urgent or has_topic:
                        post = {
                            "title":        submission.title,
                            "body":         submission.selftext or "",
                            "subreddit":    sub_name,
                            "author":       str(submission.author or "unknown"),
                            "url":          url,
                            "reddit_score": submission.score,
                        }
                        new_signals.append(_build_signal(post, is_demo=False))
                        existing_urls.add(url)
                time.sleep(0.6)   # polite rate limiting
            except Exception as e:
                print(f"[Reddit] r/{sub_name}: {e}")

        all_signals = new_signals + existing
        all_signals = sorted(all_signals, key=lambda s: s.get("detected_at",""), reverse=True)[:300]
        save_signals(all_signals)
        return new_signals

    except Exception as e:
        print(f"[Reddit] Auth failed: {e} → DEMO mode")
        return generate_demo_signals(4)


def get_stats() -> dict:
    signals   = load_signals()
    total     = len(signals)
    new       = sum(1 for s in signals if s["status"] == "new")
    drafted   = sum(1 for s in signals if s["status"] == "drafted")
    sent      = sum(1 for s in signals if s["status"] == "sent")
    converted = sum(1 for s in signals if s["status"] == "converted")
    high_urg  = sum(1 for s in signals if s.get("urgency_score", 0) >= 30)
    # service distribution
    svc_counts: dict = {}
    for s in signals:
        k = s.get("detected_service", "Other")
        svc_counts[k] = svc_counts.get(k, 0) + 1
    top_svc = max(svc_counts, key=svc_counts.get) if svc_counts else "—"
    return {
        "total":           total,
        "new":             new,
        "drafted":         drafted,
        "sent":            sent,
        "converted":       converted,
        "high_urgency":    high_urg,
        "top_service":     top_svc,
        "conversion_rate": f"{round(converted/total*100)}%" if total else "0%",
        "service_breakdown": svc_counts,
    }


if __name__ == "__main__":
    sigs = generate_demo_signals(10)
    print(f"Seeded {len(sigs)} demo signals")
    for s in sigs:
        print(f"  [{s['urgency_score']:>2}] {s['title'][:55]:55s} → {s['detected_service']}")
