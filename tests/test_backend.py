from fastapi.testclient import TestClient
from backend.app import app
import config

client = TestClient(app)

def test_sources():
    r = client.get(f"/sources/{config.STUDENT_ID}")
    assert r.status_code == 200
    assert "sources" in r.json()
