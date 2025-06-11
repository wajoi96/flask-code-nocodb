import importlib.util
import json
import requests
from pathlib import Path

spec = importlib.util.spec_from_file_location("main_module", Path(__file__).resolve().parents[1] / "main (4).py")
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
update_sentimen_in_nocodb = main.update_sentimen_in_nocodb


def test_index():
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert "Server Flask" in text


def test_update_sentimen(monkeypatch):
    def mock_get(url, headers):
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {"list": [{"Id": 1}]}
        return Resp()

    def mock_post(url, headers, json=None):
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {}
        return Resp()

    monkeypatch.setattr(requests, 'get', mock_get)
    monkeypatch.setattr(requests, 'post', mock_post)
    with app.test_client() as client:
        resp = client.post('/update-sentimen', json={"pair": "BTC/USDT", "sentimen": "Bullish"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "Berjaya"


def test_url_encoding(monkeypatch):
    captured = {}

    def mock_get(url, headers):
        captured['url'] = url
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {"list": [{"Id": 1}]}
        return Resp()

    def mock_post(url, headers, json=None):
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {}
        return Resp()

    monkeypatch.setattr(requests, 'get', mock_get)
    monkeypatch.setattr(requests, 'post', mock_post)

    success, _ = update_sentimen_in_nocodb('BTC/USDT', 'Bearish')
    assert success
    assert '%2F' in captured['url']
