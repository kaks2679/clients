"""
signal_detector.py  –  Client Hunter v2  (Stephen Muema / Steve Kaks)
──────────────────────────────────────────────────────────────────────
Sources:
  1. Reddit RSS  (100% FREE — no account, no API key, no age restriction)
  2. Reddit PRAW (when API credentials available)
  3. Reddit URL  (paste any Reddit URL → auto-scrape via .json)
  4. Twitter/X   (Bearer token — basic search)
  5. Demo mode   (zero credentials needed, always works)
"""

import os, json, time, random, uuid, re, html
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_FILE    = Path(__file__).parent / "data" / "signals.json"
HEATMAP_FILE = Path(__file__).parent / "data" / "heatmap.json"
DATA_FILE.parent.mkdir(exist_ok=True)

# ── RSS scanning subreddits (no API key needed) ──────────────────────────────
SUBREDDITS_RSS = [
    "HomeworkHelp", "learnpython", "statistics", "datascience",
    "college", "AskStatistics", "learnmachinelearning",
    "Python", "dataanalysis", "AskAcademia", "GradSchool", "mlquestions",
]

# RSS search queries — combined as multi-sub searches
RSS_QUERIES = [
    "due tomorrow help",
    "deadline help",
    "pandas error help",
    "python error assignment",
    "homework help urgent",
    "thesis help urgent",
    "data analysis help",
    "machine learning help assignment",
    "statistics homework help",
    "essay help due",
]

# ── Keywords ─────────────────────────────────────────────────────────────────
URGENT_KW = [
    "due tomorrow","deadline","due tonight","due in ","help please",
    "please help","desperate","stuck on","i give up","assignment help",
    "homework help","cant figure","can't figure","not working",
    "keeps erroring","anyone help","urgent","asap","due monday",
    "due friday","need help fast","running out of time", "due tonight",
    "due in 2", "due in 3", "due in 4", "due this",
]
TOPIC_KW = [
    "pandas","python error","jupyter","numpy","matplotlib","seaborn",
    "scikit","sklearn","regression","classification","data cleaning",
    "data analysis","machine learning","neural network",
    "p-value","hypothesis","anova","t-test","statistics",
    "csv","dataframe","keyerror","valueerror","typeerror","indexerror",
    "essay","thesis","research paper","dissertation","proofreading",
    "academic writing","lit review","literature review","report",
    "excel","tableau","sql","database","visualization",
]
PAY_KW = ["pay","willing to pay","can pay","hire","how much","price","dm me"]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ── Service detection ─────────────────────────────────────────────────────────
SERVICE_DETECT = [
    (["keyerror","valueerror","typeerror","indexerror","python error",
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
     "body":"Masters student. My advisor keeps saying 'too vague, no clear argument'. 4 pages, climate policy topic. Deadline Monday. Happy to pay.",
     "subreddit":"GradSchool","author":"masters_climate_policy",
     "url":"https://reddit.com/r/GradSchool/comments/xdemo3","reddit_score":23,"source":"reddit"},
    {"title":"ML model giving 99% accuracy — I know something is wrong, deadline tomorrow",
     "body":"Random forest classifier for my capstone. Accuracy is 99.7%. I don't know how to fix train/test split. Submission is 9 AM tomorrow.",
     "subreddit":"learnmachinelearning","author":"cs_senior_panicking",
     "url":"https://reddit.com/r/learnmachinelearning/comments/xdemo4","reddit_score":17,"source":"reddit"},
    {"title":"Pandas ValueError — cannot convert NaN to integer, due tonight",
     "body":"Getting `ValueError: Cannot convert non-finite values`. I tried `dropna()` but it breaks my merge. Due in 3 hours.",
     "subreddit":"HomeworkHelp","author":"biz_student_3am",
     "url":"https://reddit.com/r/HomeworkHelp/comments/xdemo5","reddit_score":4,"source":"reddit"},
    {"title":"Need 5 matplotlib visualizations for data science capstone — can pay",
     "body":"I need: histogram, scatter, box plot, heatmap, bar chart from one CSV. Would love commented code.",
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
     "body":"40 sources in APA 7th edition. Half are websites and I keep getting the format wrong. Need editing help.",
     "subreddit":"AskAcademia","author":"phd_student_struggling",
     "url":"https://reddit.com/r/AskAcademia/comments/xdemo10","reddit_score":14,"source":"reddit"},
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
        if any(k in text for k in kws):
            return svc, price, tag
    return "General Help", "$20–40", "General"


def _urgency(title: str, body: str) -> int:
    text  = (title + " " + body).lower()
    score = 0
    for kw in URGENT_KW:
        if kw in text: score += 10
    for kw in TOPIC_KW:
        if kw in text: score += 4
    if any(w in text for w in PAY_KW): score += 20
    return min(score, 99)


def _strip_html(raw: str) -> str:
    """Strip HTML tags and unescape entities."""
    clean = re.sub(r'<[^>]+>', ' ', html.unescape(raw or ''))
    return re.sub(r'\s+', ' ', clean).strip()


def _build_signal(post: dict) -> dict:
    title  = post.get("title", "").strip()
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
        "subject_tag":      tag,
        "source":           source,
        "detected_at":      datetime.now(timezone.utc).isoformat(),
        "status":           "new",
        "replied_to":       None,
        "ai_reply":         None,
        "ai_dm":            None,
        "reply_variants":   {},
        "is_demo":          post.get("is_demo", False),
    }


def _update_heatmap(hour: int):
    hm = {}
    if HEATMAP_FILE.exists():
        try: hm = json.loads(HEATMAP_FILE.read_text())
        except Exception: hm = {}
    hm[str(hour)] = hm.get(str(hour), 0) + 1
    HEATMAP_FILE.write_text(json.dumps(hm))


# ── Public API ────────────────────────────────────────────────────────────────

def load_signals() -> list:
    if DATA_FILE.exists():
        try: return json.loads(DATA_FILE.read_text())
        except Exception: return []
    return []


def save_signals(signals: list):
    DATA_FILE.write_text(json.dumps(signals, indent=2))


def load_heatmap() -> dict:
    if HEATMAP_FILE.exists():
        try: return json.loads(HEATMAP_FILE.read_text())
        except Exception: pass
    demo = {"0":"3","1":"2","2":"4","3":"3","4":"1","5":"1","6":"2","7":"4",
            "8":"6","9":"7","10":"8","11":"9","12":"10","13":"9","14":"8",
            "15":"9","16":"10","17":"11","18":"13","19":"15","20":"18",
            "21":"24","22":"28","23":"22"}
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


# ── Reddit RSS Scanner (NO API KEY, NO ACCOUNT AGE) ─────────────────────────

def scan_reddit_rss() -> list:
    """
    Scans Reddit using public RSS feeds.
    Works with ZERO credentials — no account, no API key, no age restriction.
    Reddit RSS is fully public and unauthenticated.
    """
    existing      = load_signals()
    existing_urls = {s["url"] for s in existing}
    new           = []

    # Strategy 1: Search each subreddit for urgent keywords via RSS
    search_subs = "learnpython+HomeworkHelp+statistics+datascience+college+AskStatistics+learnmachinelearning+Python+dataanalysis+AskAcademia+GradSchool"

    for query in RSS_QUERIES[:6]:   # limit to avoid rate limit
        try:
            q_enc = requests.utils.quote(query)
            url   = f"https://www.reddit.com/r/{search_subs}/search.rss?q={q_enc}&sort=new&limit=15"
            r     = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue

            root    = ET.fromstring(r.content)
            ns      = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            for entry in entries:
                title_el   = entry.find("atom:title", ns)
                content_el = entry.find("atom:content", ns)
                link_el    = entry.find("atom:link", ns)
                author_el  = entry.find("atom:author/atom:name", ns)
                category_el= entry.find("atom:category", ns)

                title  = title_el.text if title_el is not None else ""
                body   = _strip_html(content_el.text if content_el is not None else "")
                url_   = link_el.get("href","") if link_el is not None else ""
                author = (author_el.text or "unknown") if author_el is not None else "unknown"
                sub    = (category_el.get("term","unknown") if category_el is not None else "unknown")

                # Extract subreddit from URL
                sub_match = re.search(r'/r/([^/]+)/', url_)
                if sub_match: sub = sub_match.group(1)

                if not title or not url_ or url_ in existing_urls:
                    continue

                # Urgency filter — must match at least one signal
                text = (title + " " + body).lower()
                has_signal = (any(kw in text for kw in URGENT_KW) or
                              any(kw in text for kw in TOPIC_KW))
                if not has_signal:
                    continue

                post = {"title": title, "body": body, "subreddit": sub,
                        "author": author, "url": url_, "reddit_score": 0,
                        "source": "reddit_rss"}
                sig = _build_signal(post)
                new.append(sig)
                existing_urls.add(url_)
                _update_heatmap(datetime.now().hour)

            time.sleep(0.5)   # polite
        except Exception as e:
            print(f"[RSS] Query '{query}': {e}")

    # Strategy 2: Browse new posts per subreddit via RSS
    for sub in SUBREDDITS_RSS[:6]:
        try:
            url = f"https://www.reddit.com/r/{sub}/new/.rss?limit=20"
            r   = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue

            root    = ET.fromstring(r.content)
            ns      = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            for entry in entries:
                title_el   = entry.find("atom:title", ns)
                content_el = entry.find("atom:content", ns)
                link_el    = entry.find("atom:link", ns)
                author_el  = entry.find("atom:author/atom:name", ns)

                title  = title_el.text if title_el is not None else ""
                body   = _strip_html(content_el.text if content_el is not None else "")
                url_   = link_el.get("href","") if link_el is not None else ""
                author = (author_el.text or "unknown") if author_el is not None else "unknown"

                if not title or not url_ or url_ in existing_urls:
                    continue

                text = (title + " " + body).lower()
                has_urgent = any(kw in text for kw in URGENT_KW)
                has_topic  = any(kw in text for kw in TOPIC_KW)
                if not (has_urgent or has_topic):
                    continue

                post = {"title": title, "body": body, "subreddit": sub,
                        "author": author, "url": url_, "reddit_score": 0,
                        "source": "reddit_rss"}
                sig = _build_signal(post)
                new.append(sig)
                existing_urls.add(url_)
                _update_heatmap(datetime.now().hour)

            time.sleep(0.4)
        except Exception as e:
            print(f"[RSS] Sub r/{sub}: {e}")

    # Deduplicate by URL
    seen_urls = set()
    deduped   = []
    for s in new:
        if s["url"] not in seen_urls:
            seen_urls.add(s["url"])
            deduped.append(s)

    all_sigs = (deduped + existing)[:300]
    save_signals(sorted(all_sigs, key=lambda s: s.get("detected_at",""), reverse=True))
    print(f"[RSS] Found {len(deduped)} new real signals")
    return deduped


# ── Reddit URL paste → instant signal ────────────────────────────────────────

def scrape_reddit_url(url: str) -> dict:
    """
    Given any Reddit post URL, fetch title+body via the public .json endpoint.
    Works without any API key. Works from a browser perspective.
    Falls back to RSS-style fetch if .json is blocked.
    """
    url = url.strip().rstrip("/")

    # Remove any existing .json suffix
    if url.endswith(".json"):
        json_url = url
    else:
        json_url = url + ".json"

    # Make sure it's a valid Reddit URL
    if "reddit.com" not in json_url:
        return {"error": "Not a Reddit URL"}

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/html",
        }
        r = requests.get(json_url, headers=headers, timeout=10)

        if r.status_code == 200:
            data   = r.json()
            post   = data[0]["data"]["children"][0]["data"]
            title  = post.get("title","")
            body   = post.get("selftext","") or post.get("url","")
            author = str(post.get("author","unknown"))
            sub    = post.get("subreddit","unknown")
            score  = int(post.get("score",0))

            if body in ("[deleted]","[removed]",""):
                body = title   # use title as body if no text

            existing      = load_signals()
            existing_urls = {s["url"] for s in existing}

            # Strip .json from final URL
            clean_url = url.replace(".json","")

            if clean_url in existing_urls:
                # Return existing signal
                return next(s for s in existing if s["url"] == clean_url)

            post_data = {
                "title": title, "body": body, "subreddit": sub,
                "author": author, "url": clean_url,
                "reddit_score": score, "source": "reddit_url",
            }
            sig      = _build_signal(post_data)
            all_sigs = [sig] + existing
            save_signals(all_sigs)
            _update_heatmap(datetime.now().hour)
            return sig

        else:
            # Fallback: try to at least extract title from URL
            slug = url.split("/")[-1].replace("_"," ").replace("-"," ")
            sub_match = re.search(r'/r/([^/]+)/', url)
            sub = sub_match.group(1) if sub_match else "reddit"

            post_data = {
                "title": f"[URL] {slug[:80]}",
                "body":  f"Pasted from: {url} — full text could not be fetched (Reddit blocked server-side). Check the post manually.",
                "subreddit": sub, "author": "unknown",
                "url": url, "reddit_score": 0, "source": "reddit_url",
            }
            sig = _build_signal(post_data)
            existing = load_signals()
            save_signals([sig] + existing)
            return sig

    except Exception as e:
        return {"error": str(e)}


# ── Reddit PRAW scanner (when API credentials available) ─────────────────────

def scan_reddit_praw() -> list:
    cid  = os.getenv("REDDIT_CLIENT_ID","").strip()
    csec = os.getenv("REDDIT_CLIENT_SECRET","").strip()
    ua   = os.getenv("REDDIT_USER_AGENT","ClientHunter/2.0 by SteveKaks")
    if not cid or not csec:
        return []
    try:
        import praw
        reddit        = praw.Reddit(client_id=cid, client_secret=csec, user_agent=ua)
        existing      = load_signals()
        existing_urls = {s["url"] for s in existing}
        new           = []
        for sub_name in SUBREDDITS_RSS[:10]:
            try:
                for submission in reddit.subreddit(sub_name).new(limit=30):
                    post_url = f"https://reddit.com{submission.permalink}"
                    if post_url in existing_urls: continue
                    text = (submission.title + " " + (submission.selftext or "")).lower()
                    if any(kw in text for kw in URGENT_KW) or any(kw in text for kw in TOPIC_KW):
                        post = {"title": submission.title, "body": submission.selftext or "",
                                "subreddit": sub_name, "author": str(submission.author or "unknown"),
                                "url": post_url, "reddit_score": submission.score, "source": "reddit"}
                        sig = _build_signal(post)
                        new.append(sig)
                        existing_urls.add(post_url)
                        _update_heatmap(datetime.now().hour)
                time.sleep(0.6)
            except Exception as e:
                print(f"[PRAW] r/{sub_name}: {e}")
        all_sigs = (new + existing)[:300]
        save_signals(sorted(all_sigs, key=lambda s: s.get("detected_at",""), reverse=True))
        return new
    except Exception as e:
        print(f"[PRAW] Auth failed: {e}")
        return []


# ── Twitter/X scanner ─────────────────────────────────────────────────────────

TWITTER_QUERIES = [
    "pandas error deadline -is:retweet lang:en",
    "python homework help due -is:retweet lang:en",
    "thesis help deadline -is:retweet lang:en",
    "data analysis help due -is:retweet lang:en",
    "machine learning assignment help -is:retweet lang:en",
]

def scan_twitter_live() -> list:
    token = os.getenv("TWITTER_BEARER_TOKEN","").strip()
    if not token: return []
    import urllib.parse
    token = urllib.parse.unquote(token)  # decode %2F etc
    try:
        headers       = {"Authorization": f"Bearer {token}"}
        existing      = load_signals()
        existing_urls = {s["url"] for s in existing}
        new           = []
        r = requests.get("https://api.twitter.com/2/tweets/search/recent",
            params={"query": TWITTER_QUERIES[0], "max_results": 20,
                    "tweet.fields":"created_at,author_id,text",
                    "expansions":"author_id","user.fields":"username"},
            headers=headers, timeout=10)
        if r.status_code == 200:
            data  = r.json()
            users = {u["id"]: u["username"] for u in data.get("includes",{}).get("users",[])}
            for tweet in data.get("data",[]):
                tid   = tweet["id"]
                turl  = f"https://twitter.com/i/web/status/{tid}"
                if turl in existing_urls: continue
                author = "@" + users.get(tweet["author_id"],"unknown")
                post   = {"title": tweet["text"][:120], "body": tweet["text"],
                          "subreddit":"twitter","author":author,
                          "url":turl,"reddit_score":0,"source":"twitter"}
                sig = _build_signal(post)
                new.append(sig)
                existing_urls.add(turl)
                _update_heatmap(datetime.now().hour)
            all_sigs = (new + existing)[:300]
            save_signals(sorted(all_sigs, key=lambda s: s.get("detected_at",""), reverse=True))
        else:
            print(f"[Twitter] Status {r.status_code}: {r.text[:150]}")
        return new
    except Exception as e:
        print(f"[Twitter] {e}")
        return []


# ── Main scanner (tries RSS first, then PRAW if available) ───────────────────

def scan_reddit_live() -> list:
    """Primary Reddit scanner — uses RSS (no credentials) + PRAW if available."""
    rss_results  = scan_reddit_rss()
    praw_results = scan_reddit_praw()   # only runs if PRAW creds present
    return rss_results + praw_results


# ── Stats ─────────────────────────────────────────────────────────────────────

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
    resp_rate = f"{round(replied/(replied+no_reply)*100)}%" if (replied+no_reply) else "—"
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
        "total": total, "new": new, "drafted": drafted, "sent": sent,
        "converted": converted, "high_urgency": high_urg,
        "response_rate": resp_rate,
        "conversion_rate": f"{round(converted/total*100)}%" if total else "0%",
        "service_breakdown": svc_counts,
        "source_breakdown":  src_counts,
        "tag_breakdown":     tag_counts,
    }


if __name__ == "__main__":
    print("Testing RSS scanner (no API key needed)...")
    sigs = scan_reddit_rss()
    print(f"\nFound {len(sigs)} real signals from Reddit RSS:")
    for s in sigs[:5]:
        print(f"  [{s['urgency_score']:>2}] [{s['source']:12}] {s['title'][:60]}")
