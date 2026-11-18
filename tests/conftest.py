"""Piezas compartidas por las pruebas: la configuración y un switch simulado."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
VARS = ROOT / "config" / "vars.yml"


class FakeSwitch:
    """Imita al cliente RESTCONF guardando la configuración en un diccionario.

    Permite probar deploy.py y verify.py sin red ni credenciales.
    """

    def __init__(self, state=None):
        self.state = dict(state or {})
        self.puts = []

    def get(self, path):
        return self.state.get(path)

    def put(self, path, payload):
        code = 204 if path in self.state else 201
        self.state[path] = payload
        self.puts.append(path)
        return code


@pytest.fixture
def cfg():
    with open(VARS, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def switch():
    return FakeSwitch()
