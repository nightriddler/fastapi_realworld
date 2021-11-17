from starlette.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_ping():
    pass
