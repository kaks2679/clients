"""
signal_detector.py  –  Client Hunter v2  (Stephen Muema / Steve Kaks)
──────────────────────────────────────────────────────────────────────
Sources:
  1. Reddit (free API via PRAW)
  2. Twitter/X (free Bearer token, search API v2)
  3. Demo mode (zero credentials needed)

New features:
  - Sub-tags for better filtering (Data Science / Writing / Debugging)
  - replied_to tracking (did they respond?)
  - Heatmap data (hour-of-day signal count)
"""

import os, json, time, random, uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_FILE    = Path(__file__).parent / "data" / "signals.json"
HEATMAP_FILE = Path(__file__).parent / "data" / "heatmap.json"
DATA_FILE.parent.mkdir(exist_ok=True)

# ── Subreddits ───────────────────────────────────────────────────────────────
SUBREDDITS = [
    "HomeworkHelp","learnpython","statistics","datascience",
    "college","AskStatistics","learnmachinelearning",
    "Python","dataanalysis","AskAcademia","GradSchool","mlquestions",
]

# ── Keywords ─────────────────────────────────────────────────────────────────
URGENT_KW = [
    "due tomorrow","deadline","due tonight","due in","help please",
    "please help","desperate","stuck on","i give up","assignment help",
    "homework help","cant figure","can't figure","not working",
    "keeps erroring","anyone help","urgent","asap","due monday",
    "due friday","need help fast","running out of time",
]
TOPIC_KW = [
    "pandas","python error","jupyter","numpy","matplotlib","seaborn",
    "scikit","sklearn","regression","classification","data cleaning",
    "data analysis","machine learning","neural network",
    "p-value","hypothesis","anova","t-test","statistics",
    "csv","dataframe","KeyError","ValueError","TypeError","IndexError",
    "essay","thesis","research paper","dissertation","proofreading",
    "academic writing","lit review","literature review","report writing",
    "apa format","mla format","excel","tableau","sql","database",
]
PAY_KW = ["pay","willing to pay","can pay","hire","how much","price","dm me","dm"]

# ── Twitter search queries ────────────────────────────────────────────────────
TWITTER_QUERIES = [
    "pandas error deadline -is:retweet lang:en",
    "python homework help due -is:retweet lang:en",
    "thesis help deadline -is:retweet lang:en",
    "data analysis help due -is:retweet lang:en",
    "jupyter notebook error help -is:retweet lang:en",
    "statistics homework help -is:retweet lang:en",
    "machine learning assignment help -is:retweet lang:en",
]

# ── Service detection ─────────────────────────────────────────────────────────
SERVICE_DETECT = [
    (["KeyError","ValueError","TypeError","IndexError","python error",
      "error message","not working","broken","debug","traceback"],
     "Python Debugging", "$15–25", "Debugging"),

    (["pandas","csv","dataframe","data cleaning","dropna","merge",
      "fillna","groupby","excel","sql"],
     "Data Cleaning", "$35–50", "Data Science"),

    (["matplotlib","seaborn","plot","visualization","graph",
      "chart","histogram","scatter","heatmap"],
     "Data Visualization", "$30–45", "Data Science"),

    (["regression","correlation","p-value","anova","t-test",
      "hypothesis","confidence interval","statistics","spss","coefficient"],
     "Statistics", "$40–60", "Data Science"),

    (["sklearn","scikit","classification","random forest",
      "neural","deep learning","accuracy","overfitting",
      "cross-validation","machine learning","model","xgboost"],
     "Machine Learning", "$75–100", "Data Science"),

    (["jupyter","notebook","data analysis","eda","exploratory","dataset"],
     "Data Analysis", "$50–75", "Data Science"),

    (["essay","thesis","dissertation","research paper",
      "lit review","literature review","proofreading",
      "academic writing","citation","apa","mla","report","assignment"],
     "Academic Writing", "$25–50", "Writing"),
]

# ── Demo posts ────────────────────────────────────────────────────────────────
DEMO_POSTS = [
    {"title":"URGENT — KeyError: 'Age' pandas, assignment due in 4 hours",
     "body":"I keep getting `KeyError: 'Age'` when I run `df['Age'].mean()`. My stats final is due at midnight. Please help!!",
     "subreddit":"learnpython","author":"exhausted_stats_major",
     "url":"https://reddit.com/r/learnpython/comments/xdemo1","reddit_score":5,"source":"reddit"},

    {"title":"Multiple regression help — final project due Friday, I'm so lost",
     "body":"My professor gave us a CSV with 18 columns. I need to run a multiple regression. The TA's office hours are full. I'm willing to pay.",
     "subreddit":"statistics","author":"mba_student_Nairobi",
     "url":"https://reddit.com/r/statistics/comments/xdemo2","reddit_score":11,"source":"reddit"},

    {"title":"My thesis introduction is a disaster — advisor rejected it twice",
     "body":"Masters student. My advisor keeps saying 'too vague, no clear argument'. 4 pages, climate policy topic. Deadline Monday. Happy to pay for editing.",
     "subreddit":"GradSchool","author":"masters_climate_policy",
     "url":"https://reddit.com/r/GradSchool/comments/xdemo3","reddit_score":23,"source":"reddit"},

    {"title":"ML model giving 99% accuracy — I know something is wrong, deadline tomorrow",
     "body":"Random forest classifier for my capstone. Accuracy is 99.7%. I don't know how to fix train/test split. Submission is 9 AM tomorrow.",
     "subreddit":"learnmachinelearning","author":"cs_senior_panicking",
     "url":"https://reddit.com/r/learnmachinelearning/comments/xdemo4","reddit_score":17,"source":"reddit"},

    {"title":"Pandas ValueError — cannot convert NaN to integer, due tonight",
     "body":"Getting `ValueError: Cannot convert non-finite values (NA or inf) to integer`. I tried `dropna()` but it breaks my merge. Due in 3 hours.",
     "subreddit":"HomeworkHelp","author":"biz_student_3am",
     "url":"https://reddit.com/r/HomeworkHelp/comments/xdemo5","reddit_score":4,"source":"reddit"},

    {"title":"Need 5 matplotlib visualizations for data science capstone — can pay",
     "body":"I need: histogram, scatter, box plot, heatmap, bar chart from one CSV. Can share the file. Would love commented code.",
     "subreddit":"datascience","author":"cs_capstone_help",
     "url":"https://reddit.com/r/datascience/comments/xdemo6","reddit_score":9,"source":"reddit"},

    {"title":"p-value question — assignment due in 6 hours, totally confused",
     "body":"My professor wants me to 'interpret the p-value of 0.03 in context of our research hypothesis'. 30% of my grade. Can pay.",
     "subreddit":"AskStatistics","author":"psych_undergrad_lost",
     "url":"https://reddit.com/r/AskStatistics/comments/xdemo7","reddit_score":8,"source":"reddit"},

    {"title":"Research paper structure is terrible, professor said start over, due tomorrow",
     "body":"10-page paper on renewable energy policy. Professor said my structure is 'incoherent'. I have sources but can't organize them. Can pay.",
     "subreddit":"college","author":"senior_humanities_rip",
     "url":"https://reddit.com/r/college/comments/xdemo8","reddit_score":31,"source":"reddit"},

    {"title":"sklearn predict() all zeros — data science homework, stuck for days",
     "body":"My logistic regression predicts everything as class 0. Tried class_weight='balanced' but accuracy dropped to 50%. Due in 2 days.",
     "subreddit":"learnmachinelearning","author":"ml_beginner_help",
     "url":"https://reddit.com/r/learnmachinelearning/comments/xdemo9","reddit_score":6,"source":"reddit"},

    {"title":"APA citation format — dissertation chapter due Friday",
     "body":"40 sources in APA 7th edition. Half are websites and I keep getting the format wrong. Turnitin also flagged my paraphrasing. Need editing help.",
     "subreddit":"AskAcademia","author":"phd_student_struggling",
     "url":"https://reddit.com/r/AskAcademia/comments/xdemo10","reddit_score":14,"source":"reddit"},

    # Twitter-style demo signals
    {"title":"pandas is literally ruining my life rn. due in 2 hours. help",
     "body":"pandas is literally ruining my life rn. due in 2 hours. help",
     "subreddit":"twitter","author":"@frustrated_ds_student",
     "url":"https://twitter.com/frustrated_ds_student/status/xdemo11","reddit_score":0,"source":"twitter"},

    {"title":"who even understands logistic regression??? assignment due tomorrow and i want to cry",
     "body":"who even understands logistic regression??? assignment due tomorrow and i want to cry",
     "subreddit":"twitter","author":"@ml_lost_student",
     "url":"https://twitter.com/ml_lost_student/status/xdemo12","reddit_score":0,"source":"twitter"},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect(title: str, body: str):
    text = (title + " " + body).lower()
    for kws, svc, price, tag in SERVICE_DETECT:
        if any(k.lower() in text for k in kws):
            return svc, price, tag
    return "General Help", "$20–40", "General"


def _urgency(title: str, body: str) -> int:
    text  = (title + " " + body).lower()
    score = 0
    for kw in URGENT_KW:
        if kw in text:
            score += 10
    for kw in TOPIC_KW:
        if kw in text:
            score += 4
    if any(w in text for w in PAY_KW):
        score += 20
    return min(score, 99)


def _build_signal(post: dict) -> dict:
    title  = post.get("title", "")
    body   = post.get("body", "") or post.get("selftext", "")
    source = post.get("source", "reddit")
    svc, price, tag = _detect(title, body)
    urg = _urgency(title, body)
    return {
        "id":               str(uuid.uuid4()),
        "title":            title,
        "body":             body[:500] + ("…" if len(body) > 500 else ""),
        "subreddit":        post.get("subreddit", "unknown"),
        "author":           post.get("author", "unknown"),
        "url":              post.get("url", "#"),
        "reddit_score":     post.get("reddit_score", post.get("score", 0)),
        "urgency_score":    urg,
        "detected_service": svc,
        "suggested_price":  price,
        "subject_tag":      tag,       # Data Science / Writing / Debugging / General
        "source":           source,    # reddit | twitter | demo
        "detected_at":      datetime.now(timezone.utc).isoformat(),
        "status":           "new",
        "replied_to":       None,      # None | True | False
        "ai_reply":         None,
        "ai_dm":            None,
        "is_demo":          post.get("is_demo", False),
    }


def _update_heatmap(hour: int):
    """Track signal count by hour of day (0–23)."""
    hm = {}
    if HEATMAP_FILE.exists():
        try:
            hm = json.loads(HEATMAP_FILE.read_text())
        except Exception:
            hm = {}
    hm[str(hour)] = hm.get(str(hour), 0) + 1
    HEATMAP_FILE.write_text(json.dumps(hm))


# ── Public API ────────────────────────────────────────────────────────────────

def load_signals() -> list:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            return []
    return []


def save_signals(signals: list):
    DATA_FILE.write_text(json.dumps(signals, indent=2))


def load_heatmap() -> dict:
    if HEATMAP_FILE.exists():
        try:
            return json.loads(HEATMAP_FILE.read_text())
        except Exception:
            pass
    # seed with realistic demo heatmap
    demo = {
        "0":"3","1":"2","2":"4","3":"3","4":"1","5":"1",
        "6":"2","7":"4","8":"6","9":"7","10":"8","11":"9",
        "12":"10","13":"9","14":"8","15":"9","16":"10","17":"11",
        "18":"13","19":"15","20":"18","21":"24","22":"28","23":"22",
    }
    HEATMAP_FILE.write_text(json.dumps(demo))
    return demo


def generate_demo_signals(n: int = 5) -> list:
    existing      = load_signals()
    existing_urls = {s["url"] for s in existing}
    pool          = [p for p in DEMO_POSTS if p["url"] not in existing_urls]
    random.shuffle(pool)
    new = []
    for post in pool[:n]:
        post["is_demo"] = True
        sig = _build_signal(post)
        offset = random.randint(0, 28800)
        sig["detected_at"] = datetime.fromtimestamp(
            time.time() - offset, tz=timezone.utc).isoformat()
        _update_heatmap(datetime.now().hour)
        new.append(sig)
    all_sigs = new + existing
    save_signals(all_sigs)
    return new


def scan_reddit_live() -> list:
    cid    = os.getenv("REDDIT_CLIENT_ID","").strip()
    csec   = os.getenv("REDDIT_CLIENT_SECRET","").strip()
    ua     = os.getenv("REDDIT_USER_AGENT","ClientHunter/2.0 by SteveKaks")

    if not cid or not csec:
        return generate_demo_signals(4)

    try:
        import praw
        reddit = praw.Reddit(client_id=cid, client_secret=csec, user_agent=ua)
        existing      = load_signals()
        existing_urls = {s["url"] for s in existing}
        new = []
        for sub_name in SUBREDDITS[:10]:
            try:
                for submission in reddit.subreddit(sub_name).new(limit=30):
                    url = f"https://reddit.com{submission.permalink}"
                    if url in existing_urls:
                        continue
                    text = (submission.title + " " + (submission.selftext or "")).lower()
                    if any(kw in text for kw in URGENT_KW) or any(kw in text for kw in TOPIC_KW):
                        post = {
                            "title": submission.title,
                            "body":  submission.selftext or "",
                            "subreddit": sub_name,
                            "author": str(submission.author or "unknown"),
                            "url": url,
                            "reddit_score": submission.score,
                            "source": "reddit",
                        }
                        sig = _build_signal(post)
                        new.append(sig)
                        existing_urls.add(url)
                        _update_heatmap(datetime.now().hour)
                time.sleep(0.6)
            except Exception as e:
                print(f"[Reddit] r/{sub_name}: {e}")
        all_sigs = (new + existing)[:300]
        save_signals(sorted(all_sigs, key=lambda s: s.get("detected_at",""), reverse=True))
        return new
    except Exception as e:
        print(f"[Reddit] Auth failed: {e}")
        return generate_demo_signals(4)


def scan_twitter_live() -> list:
    token = os.getenv("TWITTER_BEARER_TOKEN","").strip()
    if not token:
        return []
    try:
        import requests
        headers = {"Authorization": f"Bearer {token}"}
        existing      = load_signals()
        existing_urls = {s["url"] for s in existing}
        new = []
        query = TWITTER_QUERIES[0]  # rotate in future
        url   = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query, "max_results": 20,
            "tweet.fields": "created_at,author_id,text",
            "expansions": "author_id",
            "user.fields": "username",
        }
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            data  = r.json()
            users = {u["id"]: u["username"] for u in data.get("includes",{}).get("users",[])}
            for tweet in data.get("data", []):
                tid   = tweet["id"]
                turl  = f"https://twitter.com/i/web/status/{tid}"
                if turl in existing_urls:
                    continue
                author = "@" + users.get(tweet["author_id"], "unknown")
                post = {
                    "title": tweet["text"][:120],
                    "body":  tweet["text"],
                    "subreddit": "twitter",
                    "author": author,
                    "url": turl,
                    "reddit_score": 0,
                    "source": "twitter",
                }
                sig = _build_signal(post)
                new.append(sig)
                existing_urls.add(turl)
                _update_heatmap(datetime.now().hour)
        all_sigs = (new + existing)[:300]
        save_signals(sorted(all_sigs, key=lambda s: s.get("detected_at",""), reverse=True))
        return new
    except Exception as e:
        print(f"[Twitter] {e}")
        return []


def get_stats() -> dict:
    signals   = load_signals()
    total     = len(signals)
    new       = sum(1 for s in signals if s["status"] == "new")
    drafted   = sum(1 for s in signals if s["status"] == "drafted")
    sent      = sum(1 for s in signals if s["status"] == "sent")
    converted = sum(1 for s in signals if s["status"] == "converted")
    high_urg  = sum(1 for s in signals if s.get("urgency_score",0) >= 30)
    replied   = sum(1 for s in signals if s.get("replied_to") is True)
    no_reply  = sum(1 for s in signals if s.get("replied_to") is False)
    response_rate = f"{round(replied/(replied+no_reply)*100)}%" if (replied+no_reply) else "—"

    svc_counts: dict = {}
    src_counts: dict = {}
    tag_counts: dict = {}
    for s in signals:
        k = s.get("detected_service","Other")
        svc_counts[k] = svc_counts.get(k,0) + 1
        src = s.get("source","reddit")
        src_counts[src] = src_counts.get(src,0) + 1
        t = s.get("subject_tag","General")
        tag_counts[t] = tag_counts.get(t,0) + 1

    return {
        "total":            total,
        "new":              new,
        "drafted":          drafted,
        "sent":             sent,
        "converted":        converted,
        "high_urgency":     high_urg,
        "response_rate":    response_rate,
        "conversion_rate":  f"{round(converted/total*100)}%" if total else "0%",
        "service_breakdown": svc_counts,
        "source_breakdown":  src_counts,
        "tag_breakdown":     tag_counts,
    }


if __name__ == "__main__":
    sigs = generate_demo_signals(12)
    print(f"Generated {len(sigs)} demo signals")
    for s in sigs:
        print(f"  [{s['urgency_score']:>2}] [{s['subject_tag']:12}] [{s['source']:7}] {s['title'][:50]}")
