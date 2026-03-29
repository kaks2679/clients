"""
ai_reply.py  –  Client Hunter (100% FREE)
──────────────────────────────────────────
Generates personalised reply drafts for each student signal.

FREE AI tier used: Groq (llama-3.1-8b-instant) — get free key at console.groq.com
Fallback: Smart local templates (zero API needed).

Stephen's info is baked into every reply.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Stephen's info (pulled from .env which we pre-filled) ───────────────────
NAME      = os.getenv("YOUR_NAME",      "Stephen Muema (Steve Kaks)")
EMAIL     = os.getenv("YOUR_EMAIL",     "musyokas753@gmail.com")
PHONE     = os.getenv("YOUR_PHONE",     "+254-740-624-253")
PORTFOLIO = os.getenv("YOUR_PORTFOLIO", "https://stephenmueama.com")
SPECIALTY = os.getenv("YOUR_SPECIALTY", "Data Science, Python & Academic Writing")

# ── Groq system prompt ───────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are Stephen Muema (Steve Kaks), a Data Scientist and academic writer based in Kenya.
You help overwhelmed students finish their assignments — you are friendly, warm, knowledgeable, and fast.

When replying to a student's Reddit post:
1. First sentence: acknowledge their EXACT problem using their own words.
2. Second sentence: give ONE concrete, genuinely helpful free tip.
3. Third sentence: make a clear offer — price, what they get, turnaround time.
4. Last sentence: call to action — "DM me" + your contact hint.
5. Sign off with: — Steve Kaks | {PORTFOLIO}
6. Tone: like a smart, calm friend — never salesy, never robotic.
7. Max 100 words. No hashtags. No bullet points.
8. Include a realistic price (never say "free for everything").
"""

# ── Smart local templates (zero API, instant, personalised) ─────────────────
TEMPLATES = {
    "Python Debugging": (
        "That KeyError/ValueError is one of the most frustrating things in pandas — "
        "99% of the time it's a hidden space in the column name. "
        "Quick fix: run `print(df.columns.tolist())` and look carefully. "
        "If you want me to fix the whole notebook and explain every line, "
        "it's {price} flat and I can have it back to you in under an hour. "
        "DM me your error + code — no fix, no charge. — Steve Kaks | {portfolio}"
    ),
    "Data Cleaning": (
        "NaN errors in pandas are brutal, especially right before a deadline. "
        "Try `df[col].fillna(df[col].median())` instead of dropping rows — "
        "keeps your dataset complete for the merge. "
        "Send me your raw CSV and assignment prompt and I'll return a clean, "
        "commented notebook for {price}. Ready in 2 hours. "
        "DM me and let's get this done tonight. — Steve Kaks | {portfolio}"
    ),
    "Data Visualization": (
        "Five plots from one CSV is totally doable — "
        "`fig, axes = plt.subplots(2, 3, figsize=(15, 10))` gives you a clean grid to start. "
        "I can write all five with comments explaining each line for {price}. "
        "Send me the CSV and I'll have it running in about 90 minutes. "
        "DM me! — Steve Kaks | {portfolio}"
    ),
    "Statistics": (
        "p = 0.03 means: *if the null hypothesis were true, there is only a 3% chance "
        "of getting data this extreme by random chance* — since 0.03 < 0.05, you reject the null. "
        "For your write-up, state what the null was and what rejecting it means for your question. "
        "I can write the full interpretation paragraph for {price} — "
        "DM me your prompt and I'll draft it in 30 minutes. — Steve Kaks | {portfolio}"
    ),
    "Machine Learning": (
        "99% accuracy is almost always a data leak — "
        "you're likely fitting your scaler *before* the train/test split. "
        "Move `StandardScaler().fit_transform()` to inside the split and rerun. "
        "I can fix the full pipeline, add cross-validation, and return a clean notebook "
        "for {price}. DM me your code and I'll sort it before your deadline. "
        "— Steve Kaks | {portfolio}"
    ),
    "Data Analysis": (
        "Exploratory analysis trips everyone up at first — "
        "start with `df.describe()` and `df.isnull().sum()` to understand your data "
        "before anything else. "
        "I can do the full EDA, visualizations, and interpretation for {price}. "
        "Send me your dataset and prompt — turnaround is 2–3 hours. "
        "DM me! — Steve Kaks | {portfolio}"
    ),
    "Academic Writing": (
        "When advisors say 'too vague' they almost always mean your thesis statement "
        "isn't making a *specific, arguable claim* — "
        "try adding 'because [reason], which leads to [consequence]' to sharpen it. "
        "I can restructure your draft and sharpen your argument for {price}, "
        "keeping your ideas intact. Same-day turnaround. "
        "DM me your draft + rubric. — Steve Kaks | {portfolio}"
    ),
    "General Help": (
        "I can help with this — I work with students on data science projects, "
        "Python debugging, stats analysis, and academic writing. "
        "Depending on what you need, turnaround is usually 1–3 hours "
        "and prices start at $15 for quick fixes up to {price} for larger projects. "
        "Tell me more about your assignment and I'll give you an exact quote. "
        "DM me! — Steve Kaks | {portfolio}"
    ),
}


def _local_reply(service: str, price: str) -> str:
    tmpl = TEMPLATES.get(service, TEMPLATES["General Help"])
    return tmpl.format(price=price, name=NAME, portfolio=PORTFOLIO, email=EMAIL)


def generate_reply(signal: dict) -> str:
    """
    Generate a personalised reply.
    Uses Groq (free) if key is set, otherwise uses smart local templates.
    """
    service = signal.get("detected_service", "General Help")
    price   = signal.get("suggested_price",  "$20–40")
    title   = signal.get("title", "")
    body    = signal.get("body",  "")

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        return _local_reply(service, price)

    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        user_msg = (
            f"Student's Reddit post:\nTitle: {title}\nBody: {body[:500]}\n\n"
            f"Service I'm offering them: {service} ({price})\n\n"
            f"Write the reply now."
        )
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # free on Groq
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=180,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq] Error: {e} → local template")
        return _local_reply(service, price)


# ── Offer cards shown in the dashboard ──────────────────────────────────────
OFFER_CARDS = {
    "Python Debugging":  {"icon": "🐍", "title": "Python Error Fix",
                          "line": "Paste error + code → fix + explanation in 1h",
                          "price": "$15–25", "turnaround": "~1 hour",
                          "hook": "No fix, no charge"},
    "Data Cleaning":     {"icon": "🧹", "title": "CSV Data Cleaning",
                          "line": "Raw CSV + prompt → clean commented notebook",
                          "price": "$35–50", "turnaround": "2 hours",
                          "hook": "Ready to run, one click"},
    "Data Visualization":{"icon": "📊", "title": "Data Visualizations",
                          "line": "Any plots your professor wants, with comments",
                          "price": "$30–45", "turnaround": "90 min",
                          "hook": "Matplotlib + Seaborn"},
    "Statistics":        {"icon": "📈", "title": "Stats Help",
                          "line": "Regression, hypothesis testing, p-value write-up",
                          "price": "$40–60", "turnaround": "2 hours",
                          "hook": "Plain-English explanation included"},
    "Machine Learning":  {"icon": "🤖", "title": "ML Project Fix",
                          "line": "Model, cross-validation, accuracy, evaluation",
                          "price": "$75–100", "turnaround": "3–5 hours",
                          "hook": "Full commented notebook"},
    "Data Analysis":     {"icon": "🔍", "title": "Full Data Analysis",
                          "line": "EDA + visualizations + interpretation",
                          "price": "$50–75", "turnaround": "2–4 hours",
                          "hook": "Professor-ready output"},
    "Academic Writing":  {"icon": "✍️", "title": "Essay / Thesis",
                          "line": "Restructure, sharpen argument, fix flow",
                          "price": "$25–50", "turnaround": "Same day",
                          "hook": "Your ideas, just clearer"},
    "General Help":      {"icon": "📚", "title": "Student Help",
                          "line": "Data science, coding, or academic writing",
                          "price": "$15–75", "turnaround": "Fast",
                          "hook": "DM with your problem"},
}

def get_offer_card(service: str) -> dict:
    return OFFER_CARDS.get(service, OFFER_CARDS["General Help"])


if __name__ == "__main__":
    test = {
        "title": "Pandas KeyError, assignment due in 3 hours",
        "body":  "I keep getting KeyError: 'Age' when I run df['Age'].mean().",
        "detected_service": "Python Debugging",
        "suggested_price":  "$15–25",
    }
    print(generate_reply(test))
