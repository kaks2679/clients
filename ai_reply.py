"""
ai_reply.py  –  Client Hunter v2  (Stephen Muema / Steve Kaks)
───────────────────────────────────────────────────────────────
100% FREE.  Uses Groq (free tier) or local smart templates.

Reply modes:
  urgent    → short, punchy, same-day offer
  longterm  → tutoring package angle
  group     → group project, split pricing
  lowkey    → no portfolio link, no sales — just value + soft DM invite
  dm        → ultra-short, for sliding into DMs
"""

import os
from dotenv import load_dotenv

load_dotenv()

NAME      = os.getenv("YOUR_NAME",      "Stephen Muema (Steve Kaks)")
EMAIL     = os.getenv("YOUR_EMAIL",     "musyokas753@gmail.com")
PHONE     = os.getenv("YOUR_PHONE",     "+254-740-624-253")
PORTFOLIO = os.getenv("YOUR_PORTFOLIO", "https://stephenmueama.com")
LINKEDIN  = os.getenv("YOUR_LINKEDIN",  "https://www.linkedin.com/in/stephen-muema-617339359")

# ── Groq system prompt ───────────────────────────────────────────────────────
def _system_prompt(mode: str) -> str:
    base = f"""You are Stephen Muema (Steve Kaks), a Data Scientist and academic writer from Kenya.
You help overwhelmed students finish assignments — friendly, warm, fast, expert.
Contact: {EMAIL} | Portfolio: {PORTFOLIO}
"""
    modes = {
        "urgent": """URGENT MODE: Student has hours left.
- 3–4 sentences MAX. No fluff.
- Sentence 1: name their exact problem.
- Sentence 2: one quick free fix.
- Sentence 3: offer — price, what they get, "in [X] hours".
- Sign off: — Steve Kaks | {portfolio}
- Sound like a calm person who has done this 100 times.""",

        "longterm": """LONG-TERM MODE: Student is struggling with a whole course, not just one deadline.
- 4–5 sentences.
- Sentence 1: empathise with the ongoing struggle.
- Sentence 2: show you understand the course, not just the task.
- Sentence 3: offer a package — e.g. "I can work with you for the rest of the semester".
- Sentence 4: price range + what's included (multiple sessions).
- Sign off: — Steve Kaks | {portfolio}""",

        "group": """GROUP PROJECT MODE: Student is suffering because of a dysfunctional group.
- 4 sentences.
- Sentence 1: acknowledge the group pain (dead weight, etc).
- Sentence 2: offer to handle the technical/writing portion for the group.
- Sentence 3: group discount pricing — split among members it's very cheap.
- Sentence 4: "DM me and I'll sort the [coding/writing] part for everyone."
- Sign off: — Steve Kaks | {portfolio}""",

        "lowkey": """LOW-KEY MODE: Sound like a helpful person, NOT a salesman. Reddit mods watch for self-promo.
- NO portfolio link. NO email. NO "hire me".
- Just give genuine value + a soft DM invite.
- 3 sentences: fix their problem partially → tell them what's left → "DM me if you want to finish it".
- Sound like a smart classmate, not a freelancer.""",

        "dm": """DM MODE: This is a private message, not a public comment.
- Ultra short: 2–3 sentences only.
- Warmer, more personal tone.
- Include WhatsApp/email at the end: {phone} or {email}
- End with: "What's your deadline?" to get them talking.""",
    }
    tpl = modes.get(mode, modes["urgent"])
    return base + "\n" + tpl.format(portfolio=PORTFOLIO, phone=PHONE, email=EMAIL)


# ── Local smart templates (all 5 modes × all services) ──────────────────────
# Each is a dict: service → template string
# Placeholders: {price}, {portfolio}, {phone}, {email}

TEMPLATES = {
    "urgent": {
        "Python Debugging": "That KeyError is almost always a hidden space in the column name — run `print(df.columns.tolist())` right now to confirm. If you want me to fix the whole thing and send back a clean notebook, I can do it for {price} and have it to you within the hour. DM me your code + error. — Steve Kaks | {portfolio}",
        "Data Cleaning": "NaN errors before a merge are brutal — try `df.dropna(subset=['the_column'])` to target just the broken column instead of nuking all rows. If you need the full clean + commented CSV back, {price} and 90 minutes. DM me now. — Steve Kaks | {portfolio}",
        "Data Visualization": "For 5 plots fast: `fig, axes = plt.subplots(2,3,figsize=(15,10))` gives you a clean grid — pass `ax=axes[row][col]` to each plot call. I can write all 5 with comments for {price}, ready in 90 minutes. DM me the CSV. — Steve Kaks | {portfolio}",
        "Statistics": "p = 0.03 < 0.05 → reject the null. In your write-up say: 'With p=0.03, we have sufficient evidence to reject H₀, suggesting [your finding].' I can write the full interpretation section for {price} in 30 minutes. DM me the prompt. — Steve Kaks | {portfolio}",
        "Machine Learning": "99% accuracy = data leak — you're scaling before the split. Move `scaler.fit_transform()` to AFTER `train_test_split` and rerun. I can fix the full pipeline + add cross-validation for {price}, back to you in 2 hours. DM me. — Steve Kaks | {portfolio}",
        "Data Analysis": "Start with `df.describe()` and `df.isnull().sum()` — those two lines will show you exactly what's broken. Full EDA + visualizations + write-up for {price}, 2–3 hour turnaround. DM me your dataset now. — Steve Kaks | {portfolio}",
        "Academic Writing": "When your advisor says 'too vague' they mean your thesis isn't making a *specific, arguable claim* — add 'because [X], which causes [Y]' to sharpen it instantly. I can restructure your whole draft for {price}, same-day turnaround. DM me now. — Steve Kaks | {portfolio}",
        "General Help": "I can help with this — send me your assignment prompt and I'll give you an exact quote and timeline in 15 minutes. Prices start at $15 for quick fixes. DM me. — Steve Kaks | {portfolio}",
    },
    "longterm": {
        "Python Debugging": "If this keeps happening, it's usually because the course hasn't taught proper data types and indexing fundamentals — it's not your fault, it's a gap in the curriculum. I work with students through entire Data Science modules — we tackle each assignment together so you actually understand it, not just submit it. For the rest of the semester I charge a flat $60/month for up to 4 sessions, or $20 per individual project. DM me and let's build a plan. — Steve Kaks | {portfolio}",
        "Data Cleaning": "Pandas data cleaning trips up almost every student because professors assign messy real-world data but teach you with perfect textbook examples. I work with students through whole courses — we tackle each dataset together and I explain the *why* behind every fix. Monthly package is $60 for 4 sessions, individual projects from $35. DM me and let's talk. — Steve Kaks | {portfolio}",
        "Statistics": "Statistics courses are notoriously bad at connecting theory to software — most students can pass the theory exam but freeze when they see real data. I've helped students through entire stats modules — hypothesis testing, regression, ANOVA, the whole thing. $60/month for ongoing support or $40 per assignment. DM me. — Steve Kaks | {portfolio}",
        "Machine Learning": "ML courses move fast and the gap between lecture slides and working code is huge — you're not alone in this. I work with students through full ML modules — we go step by step through your assignments so you can defend your code in the final. $80/month for ongoing help or $75 per project. DM me. — Steve Kaks | {portfolio}",
        "Academic Writing": "Academic writing is a skill that compounds — once you understand structure and argument flow, every paper gets easier. I work with students through whole semesters of writing-heavy courses: essays, lit reviews, dissertations. $50/month for ongoing editing support or $25–50 per paper. DM me. — Steve Kaks | {portfolio}",
        "General Help": "This sounds like something that's going to keep coming up through your course — if you want ongoing support rather than just a one-off fix, I work with students month by month. $60/month covers up to 4 sessions. DM me and let's see if it's a good fit. — Steve Kaks | {portfolio}",
    },
    "group": {
        "Python Debugging": "Group projects where one person ends up doing all the code while others disappear — the classic. I can handle the entire Python/data portion for your group: clean code, comments, and a short explanation so everyone can pretend they understood it. Split $60 among 3–4 people and it's $15 each — cheaper than one coffee. DM me the brief and I'll sort it. — Steve Kaks | {portfolio}",
        "Data Analysis": "If your group keeps going in circles on the analysis, let me be the technical member — I'll do the full EDA, visualizations, and interpretation write-up. Split between your group members it works out to $15–20 each. DM me the dataset and prompt and I'll take it from there. — Steve Kaks | {portfolio}",
        "Machine Learning": "Group ML projects are chaos when only one person touches the code. I can build the full pipeline — model, cross-validation, evaluation, write-up — so your whole group can present it confidently. $100 flat split among 3–4 people is basically nothing. DM me. — Steve Kaks | {portfolio}",
        "Academic Writing": "Group papers where everyone writes a different section in a completely different style and nobody agrees on structure — I know this pain. I can edit the full paper into one coherent voice with proper transitions. $50 split among your group is very manageable. DM me the draft. — Steve Kaks | {portfolio}",
        "General Help": "If this is a group project, splitting the cost makes it very affordable — I charge $50–80 for most projects and split among 3–4 people it's $15–25 each. DM me the details and I can quote you exactly. — Steve Kaks | {portfolio}",
    },
    "lowkey": {
        "Python Debugging": "That error is almost always a hidden space in your column name — run `print(df.columns.tolist())` and check carefully. The fix is usually `df.rename(columns=lambda x: x.strip())` to clean all column names at once. If you're still stuck after that, DM me and I'll take a look.",
        "Data Cleaning": "For NaN before a merge, try `df[col].fillna(df[col].median())` rather than dropping rows — keeps your dataset complete. Also check `df.dtypes` to make sure the column you're merging on is the same type in both frames. If it's still breaking, DM me.",
        "Data Visualization": "For multiple plots in one figure: `fig, axes = plt.subplots(2, 3, figsize=(15,10))` then pass `ax=axes[0][0]` etc to each plot. Much cleaner than separate figures. If you want help setting up the rest, DM me.",
        "Statistics": "p = 0.03 means there's a 3% chance of seeing your results if the null hypothesis were true — since that's below 0.05, you reject the null. In your write-up, state what H₀ was and what rejecting it means for your specific research question. If you need help with the full interpretation, DM me.",
        "Machine Learning": "99% accuracy almost always means data leakage — you're probably fitting your scaler on the whole dataset before splitting. Try: split first with `train_test_split`, then fit the scaler ONLY on X_train, then transform both. That should bring accuracy back to reality. DM me if you need help.",
        "Data Analysis": "Start with `df.describe()` for numeric summary and `df.isnull().sum()` for missing values — those two lines tell you 80% of what you need to know about a dataset before touching it. If you want to talk through the rest, DM me.",
        "Academic Writing": "When a professor says 'too vague', they usually mean your thesis isn't making a specific, arguable claim. Try adding 'because [reason], which results in [consequence]' — it forces specificity. If you want someone to look at your draft, DM me.",
        "General Help": "This is a common issue — happy to point you in the right direction. Could you share a bit more about what you're working on? DM me and let's figure it out.",
    },
    "dm": {
        "Python Debugging": "Hey, saw your post about the pandas error — I fix these all the time. Send me your code and error message and I'll have it back to you in under an hour. What's your deadline? {phone} / {email}",
        "Data Cleaning": "Hey, saw your data cleaning issue — very fixable. Send me the CSV and I'll return a clean notebook with comments. What's your deadline? {phone} / {email}",
        "Data Visualization": "Hey, saw you need those plots done. Send me the CSV and I'll write all of them with comments. What's your deadline? {phone} / {email}",
        "Statistics": "Hey, saw your stats question — I can write the interpretation section for you. What's the full prompt and when is it due? {phone} / {email}",
        "Machine Learning": "Hey, saw your ML accuracy issue — that's a data leak, very fixable. Send me your notebook and I'll sort it. What's your deadline? {phone} / {email}",
        "Data Analysis": "Hey, saw your data analysis post. Send me the dataset and prompt and I'll take it from there. What's your deadline? {phone} / {email}",
        "Academic Writing": "Hey, saw your essay/thesis post — I do academic editing and restructuring. Send me the draft and rubric. What's your deadline? {phone} / {email}",
        "General Help": "Hey, saw your post — I help students with data science and academic writing. What are you working on and when is it due? {phone} / {email}",
    },
}


def _render(template: str, price: str) -> str:
    return template.format(
        price=price, portfolio=PORTFOLIO,
        phone=PHONE, email=EMAIL, name=NAME,
    )


def _local_reply(service: str, price: str, mode: str) -> str:
    svc_map = TEMPLATES.get(mode, TEMPLATES["urgent"])
    tmpl    = svc_map.get(service) or svc_map.get("General Help", "DM me to discuss. — Steve Kaks")
    return _render(tmpl, price)


def generate_reply(signal: dict, mode: str = "urgent") -> str:
    """
    Generate reply for a signal.
    mode: urgent | longterm | group | lowkey | dm
    Uses Groq free tier if key available, else smart local templates.
    """
    service = signal.get("detected_service", "General Help")
    price   = signal.get("suggested_price",  "$20–40")
    title   = signal.get("title", "")
    body    = signal.get("body",  "")

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        return _local_reply(service, price, mode)

    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        user_msg = (
            f"Student post:\nTitle: {title}\nBody: {body[:500]}\n\n"
            f"Service I'm offering: {service} ({price})\n"
            f"Write the reply in {mode.upper()} mode."
        )
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # best free model on Groq
            messages=[
                {"role": "system", "content": _system_prompt(mode)},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=220,
            temperature=0.72,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq] {e} → local template")
        return _local_reply(service, price, mode)


def generate_all_modes(signal: dict) -> dict:
    """Return all 5 reply variants at once."""
    return {mode: generate_reply(signal, mode)
            for mode in ["urgent", "longterm", "group", "lowkey", "dm"]}


# ── Offer cards ──────────────────────────────────────────────────────────────
OFFER_CARDS = {
    "Python Debugging":   {"icon":"🐍","title":"Python Error Fix",    "line":"Error + code → fix + explanation","price":"$15–25","turn":"~1 hour","hook":"No fix, no charge"},
    "Data Cleaning":      {"icon":"🧹","title":"CSV Data Cleaning",   "line":"Raw CSV → clean commented notebook","price":"$35–50","turn":"2 hours","hook":"One-click ready"},
    "Data Visualization": {"icon":"📊","title":"Data Visualizations", "line":"Any plots, with code comments",    "price":"$30–45","turn":"90 min", "hook":"Matplotlib + Seaborn"},
    "Statistics":         {"icon":"📈","title":"Statistics Help",     "line":"Regression, p-values, write-up",   "price":"$40–60","turn":"2 hours","hook":"Plain-English included"},
    "Machine Learning":   {"icon":"🤖","title":"ML Project Fix",      "line":"Model, CV, evaluation, notebook",  "price":"$75–100","turn":"3–5 h","hook":"Full commented notebook"},
    "Data Analysis":      {"icon":"🔍","title":"Full Data Analysis",  "line":"EDA + visualizations + write-up",  "price":"$50–75","turn":"2–4 hours","hook":"Professor-ready"},
    "Academic Writing":   {"icon":"✍️","title":"Essay / Thesis",     "line":"Restructure + sharpen + fix flow",  "price":"$25–50","turn":"Same day","hook":"Your ideas, clearer"},
    "General Help":       {"icon":"📚","title":"Student Help",        "line":"Data science or academic writing",  "price":"$15–75","turn":"Fast","hook":"DM your problem"},
}

def get_offer_card(service: str) -> dict:
    return OFFER_CARDS.get(service, OFFER_CARDS["General Help"])


if __name__ == "__main__":
    test_sig = {
        "title": "Pandas KeyError, final project due in 3 hours",
        "body":  "KeyError: 'Age' when I run df['Age'].mean(). Dataset is attached.",
        "detected_service": "Python Debugging",
        "suggested_price":  "$15–25",
    }
    for mode in ["urgent","longterm","group","lowkey","dm"]:
        print(f"\n── {mode.upper()} ──")
        print(generate_reply(test_sig, mode))
