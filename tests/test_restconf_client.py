"""El cliente arma bien las peticiones RESTCONF (requests simulado)."""
import pytest
import requests

import restconf_client
from restconf_client import HEADERS, RestconfClient


class Resp:
    def __init__(self, status, text=""):
        self.status_code = status
        self.text = text

    def json(self):
        return {"ok": True}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SANDBOX_USER", "usuario")
    monkeypatch.setenv("SANDBOX_PASS", "clave")
    monkeypatch.delenv("VERIFY_SSL", raising=False)
    return RestconfClient("10.10.20.48")


def test_url_base_y_credenciales(client):
    assert client.base == "https://10.10.20.48:443/restconf/data"
    assert client.auth == ("usuario", "clave")
    assert client.verify is False


def test_sin_credenciales_falla(monkeypatch):
    monkeypatch.delenv("SANDBOX_USER", raising=False)
    with pytest.raises(KeyError):
        RestconfClient("x")


def test_cabeceras_yang_json():
    assert HEADERS["Accept"] == "application/yang-data+json"
    assert HEADERS["Content-Type"] == "application/yang-data+json"


def test_get_404_es_none(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "get", lambda *a, **k: Resp(404))
    assert client.get("algo") is None


def test_get_200_devuelve_json(client, monkeypatch):
    llamadas = {}

    def falso_get(url, **kw):
        llamadas.update(url=url, **kw)
        return Resp(200, "{}")

    monkeypatch.setattr(restconf_client.requests, "get", falso_get)
    assert client.get("Cisco-IOS-XE-native:native/hostname") == {"ok": True}
    assert llamadas["url"].endswith("/restconf/data/Cisco-IOS-XE-native:native/hostname")
    assert llamadas["headers"] == HEADERS


def test_get_401_lanza_error(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "get", lambda *a, **k: Resp(401))
    with pytest.raises(requests.HTTPError):
        client.get("algo")


def test_put_devuelve_codigo(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "put", lambda *a, **k: Resp(201))
    assert client.put("algo", {"x": 1}) == 201


def test_put_400_lanza_error(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "put", lambda *a, **k: Resp(400))
    with pytest.raises(requests.HTTPError):
        client.put("algo", {"x": 1})
