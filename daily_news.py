import os
import re
import ssl
import smtplib
import feedparser
import google.generativeai as genai
import schedule
import time
from email.message import EmailMessage
from datetime import datetime
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Make sure VADER lexicon is downloaded
nltk.download("vader_lexicon")

# ================= CONFIG =================
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

EMAIL_FROM = "your_email@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"  # Gmail App Password
EMAIL_TO = "receiver_email@gmail.com"
EMAIL_SUBJECT = "📬 Automated Daily News "
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT_SSL = 465

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
]
MAX_ARTICLES_PER_FEED = 5
SUMMARY_MAX_WORDS = 180

OUTPUT_DIR = "data"
FILENAME_PREFIX = "daily_news_"
SEND_EMAIL_AFTER_RUN = True
# ==========================================


# --- helper functions ---
def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def today_filename(prefix: str, ext=".txt"):
    return f"{prefix}{datetime.today():%Y-%m-%d}{ext}"

def strip_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()

def fetch_rss_articles(feed_urls, limit=5):
    articles = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for e in feed.entries[:limit]:
            content = e.get("content", [{}])[0].get("value") if e.get("content") else e.get("summary", "")
            articles.append({
                "title": e.get("title", "(no title)"),
                "link": e.get("link", ""),
                "raw": strip_html(content)
            })
    return articles

def init_gemini(api_key: str, model_name="gemini-1.5-flash"):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def summarize(model, text: str, max_words=180) -> str:
    if not text:
        return "(No content available)"
    prompt = (
        f"Summarize the following article in under {max_words} words:\n\n"
        f"{text[:6000]}"
    )
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()

def categorize(text: str) -> str:
    _CATEGORY_KEYWORDS = {
        "technology": ["startup", "tech", "software", "ai", "app", "device", "cloud", "chip", "robot"],
        "business": ["revenue", "funding", "merger", "market", "profit", "stock", "ipo"],
        "science": ["research", "study", "scientists", "physics", "biology", "space"],
        "sports": ["match", "tournament", "league", "goal", "player", "cricket", "football"],
        "politics": ["election", "minister", "policy", "parliament", "government"],
        "entertainment": ["movie", "film", "music", "series", "celebrity", "award"]
    }
    t = text.lower()
    best, score = "general", 0
    for label, kws in _CATEGORY_KEYWORDS.items():
        s = sum(k in t for k in kws)
        if s > score:
            score, best = s, label
    return best

# --- Sentiment Analysis ---
def analyze_sentiment(text: str) -> str:
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    if scores["compound"] >= 0.05:
        return "Positive"
    elif scores["compound"] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def write_digest_file(items: list, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(f"📰 {it['title']}\n")
            f.write(f"🔗 {it['link']}\n")
            f.write(f"📂 Category: {it['category']}\n")
            f.write(f"📈 Sentiment: {it['sentiment']}\n")
            f.write(f"🧠 Summary:\n{it['summary']}\n")
            f.write("-" * 70 + "\n")

def send_email_file(filepath: str):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Digest file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        body = f.read()

    msg = EmailMessage()
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    with open(filepath, "rb") as af:
        msg.add_attachment(af.read(), maintype="text", subtype="plain", filename=os.path.basename(filepath))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT_SSL, context=context) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print(f"✅ Emailed digest: {filepath}")


# --- main run ---
def run():
    model = init_gemini(GEMINI_API_KEY)

    print("📡 Fetching articles...")
    articles = fetch_rss_articles(RSS_FEEDS, limit=MAX_ARTICLES_PER_FEED)

    print("🤖 Summarizing & Analyzing...")
    processed = []
    for a in articles:
        summary = summarize(model, a["raw"], max_words=SUMMARY_MAX_WORDS)
        sentiment = analyze_sentiment(summary)
        processed.append({
            "title": a["title"],
            "link": a["link"],
            "category": categorize(f"{a['title']} {summary}"),
            "summary": summary,
            "sentiment": sentiment
        })

    ensure_dir(OUTPUT_DIR)
    out_file = os.path.join(OUTPUT_DIR, today_filename(FILENAME_PREFIX))
    write_digest_file(processed, out_file)
    print(f"📂 Digest saved: {out_file}")

    if SEND_EMAIL_AFTER_RUN:
        send_email_file(out_file)


# --- scheduler ---
def schedule_job():
    schedule.every().day.at("09:00").do(run
