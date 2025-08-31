# 📰 AI News Intelligence System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Generative AI](https://img.shields.io/badge/Generative%20AI-Google%20Gemini%202.5%20Flash-green)]()
[![NLP](https://img.shields.io/badge/NLP-Transformers-yellow)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An **AI-powered news monitoring and summarization tool** that:
- 📡 Fetches the latest news articles from **RSS feeds**  
- 🤖 Summarizes content using **Google Gemini API (Gemini 2.5 Flash)**  
- 📊 Performs **Sentiment Analysis** (Positive / Negative / Neutral)  
- 📧 Saves summaries locally or emails them via **Gmail SMTP**  

---

## 🚀 Features
- **Automated News Fetching** — Live updates from RSS feeds  
- **AI Summarization** — Concise, human-like summaries using Generative AI  
- **Sentiment Analysis** — Detects tone of news articles  
- **Email Integration** — Sends curated digests directly to your inbox  
- **Scheduler Support** — Automates digest delivery daily at 9 AM  

---

## 🛠 Tech Stack
- **Language:** Python  
- **AI Models:** Google Gemini API (Gemini 2.5 Flash)  
- **Libraries:** `feedparser`, `transformers`, `NLTK`, `smtplib`, `schedule`, `beautifulsoup4`  
- **Others:** RSS Feeds, SMTP Automation  

---

## 📂 Project Structure
automated-news-summary-generator/
│── main.py # Main script (fetch, summarize, sentiment, email)
│── data/ # Generated daily digests
│ └── daily_news.txt
│── README.md # Documentation

## 📂 Project Structure
