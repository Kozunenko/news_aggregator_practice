import feedparser
import sqlite3
import config
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import STUDENT_ID, SOURCES
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

# CORS дозволи
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Змінні
store = {STUDENT_ID: SOURCES.copy()}
news_store = {STUDENT_ID: []}

# ---- Роутинг ----

@app.get("/sources/{student_id}")
def get_sources(student_id: str):
    if student_id not in store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"sources": store[student_id]}

@app.post("/sources/{student_id}")
def add_source(student_id: str, payload: dict):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    store[student_id].append(url)
    return {"sources": store[student_id]}

@app.post("/fetch/{student_id}")
def fetch_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    news_store[student_id].clear()
    for url in config.SOURCES:
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
    return {"fetched": len(news_store[student_id])}

@app.get("/news/{student_id}")
def get_news(student_id: str):
    if student_id not in news_store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store[student_id]}

@app.post("/analyze/{student_id}")
def analyze_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")

    analyzer = SentimentIntensityAnalyzer()
    result = []

    for art in news_store.get(student_id, []):
        text = art.get("title", "")
        scores = analyzer.polarity_scores(text)
        comp = scores["compound"]
        label = (
            "positive" if comp >= 0.05
            else "negative" if comp <= -0.05
            else "neutral"
        )
        result.append({**art, "sentiment": label, "scores": scores})

    # 💾 Збереження до бази
    save_to_db(student_id, result)

    return {"analyzed": len(result), "articles": result}

# ---- Збереження в базу ----

def save_to_db(student_id, articles):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            title TEXT,
            link TEXT,
            published TEXT,
            sentiment TEXT
        )
    """)

    for a in articles:
        cur.execute("""
            INSERT INTO articles (student_id, title, link, published, sentiment)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            a['title'],
            a['link'],
            a['published'],
            a['sentiment']
        ))

    conn.commit()
    conn.close()
