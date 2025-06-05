from fastapi.testclient import TestClient
from backend.app import app, news_store
from config import STUDENT_ID
import feedparser

client = TestClient(app)

def test_get_news_empty():
    news_store[STUDENT_ID] = []
    res = client.get(f"/news/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"articles": []}

class DummyFeed:
    entries = [
        {"title": "Good news", "link": "http://a", "published": "2025-01-01"},
        {"title": "Bad news", "link": "http://b", "published": ""}
    ]

def test_fetch_and_get(monkeypatch):
    monkeypatch.setattr("config.SOURCES", ["http://example.com/rss"])
    monkeypatch.setattr(feedparser, "parse", lambda url: DummyFeed)
    news_store[STUDENT_ID] = []

    res1 = client.post(f"/fetch/{STUDENT_ID}")
    assert res1.status_code == 200
    assert res1.json() == {"fetched": 2}

    res2 = client.get(f"/news/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json() == {
        "articles": [
            {"title": "Good news", "link": "http://a", "published": "2025-01-01", "tone": "positive"},
            {"title": "Bad news", "link": "http://b", "published": "", "tone": "negative"}
        ]
    }

def test_filter_by_tone(monkeypatch):
    # Уже є 2 статті після попереднього тесту
    res_pos = client.get(f"/news/{STUDENT_ID}?tone=positive")
    assert res_pos.status_code == 200
    assert len(res_pos.json()["articles"]) == 1
    assert res_pos.json()["articles"][0]["tone"] == "positive"

    res_neg = client.get(f"/news/{STUDENT_ID}?tone=negative")
    assert res_neg.status_code == 200
    assert len(res_neg.json()["articles"]) == 1
    assert res_neg.json()["articles"][0]["tone"] == "negative"