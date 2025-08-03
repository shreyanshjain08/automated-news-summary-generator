import feedparser
import google.generativeai as genai

# Gemini API Configuration
genai.configure(api_key="API-KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

# Summarization Function 
def summarize_article(text):
    prompt = f"Summarize the following article in under 300 words:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f" Error: {str(e)}"

# Fetch Articles from RSS Feed
def fetch_articles(rss_url, limit=3):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary
        })
    return articles

if __name__ == "__main__":
    rss_url = "https://techcrunch.com/feed/"  # You can replace with any RSS feed
    articles = fetch_articles(rss_url)

    # Generate summaries using Gemini
    for article in articles:
        article['ai_summary'] = summarize_article(article['summary'])

    # Write output to file
    with open("daily_news.txt", "w", encoding="utf-8") as f:
        for article in articles:
            f.write(f" {article['title']}\n")
            f.write(f" {article['link']}\n")
            f.write(f" Summary:\n{article['ai_summary']}\n")
            f.write("-" * 40 + "\n\n")

    print(" Daily news saved to 'daily_news.txt'")

import smtplib
from email.message import EmailMessage

def send_email():
    EMAIL_ADDRESS = "your_email@gmail.com"        # Your Gmail address
    EMAIL_PASSWORD = "Passcode"          # 16-char app password
    TO_EMAIL = "recivier_email@gmail.com"         # Can be same as yours

    msg = EmailMessage()
    msg['Subject'] = "Your AI Daily News"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL

    # Load content from daily_news.txt
    with open("daily_news.txt", "w", encoding="utf-8") as f:

        msg.set_content(f.read())

    # Send email via Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print("Email sent to", TO_EMAIL)

if __name__ == "__main__":
    ...
    print("Daily news saved to 'daily_newst.txt'")
    send_email()

