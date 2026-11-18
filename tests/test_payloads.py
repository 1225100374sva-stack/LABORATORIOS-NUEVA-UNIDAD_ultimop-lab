"""Fase TEST: los payloads YANG se construyen bien a partir de vars.yml."""
from payloads import NATIVE, build_items, is_subset


def test_cuatro_recursos(cfg):
    assert len(build_items(cfg)) == 4


def test_todas_las_rutas_cuelgan_de_native(cfg):
    for path, _ in build_items(cfg):
        assert path.startswith(NATIVE + "/")


def test_loopback_ip_en_payload(cfg):
    path, body = build_items(cfg)[0]
    assert path.endswith(f"interface/Loopback={cfg['loopback']['id']}")
    lb = body["Cisco-IOS-XE-native:Loopback"]
    assert lb["name"] == cfg["loopback"]["id"]
    assert lb["description"] == cfg["loopback"]["description"]
    prim = lb["ip"]["address"]["primary"]
    assert prim == {"address": cfg["loopback"]["ip"], "mask": cfg["loopback"]["mask"]}


def test_comunidad_snmp_solo_lectura(cfg):
    path, body = build_items(cfg)[1]
    assert path.endswith(f"Cisco-IOS-XE-snmp:community={cfg['snmp']['community']}")
    com = body["Cisco-IOS-XE-snmp:community"]
    assert com["name"] == cfg["snmp"]["community"]
    assert "RO" in com and "RW" not in com


def test_location_y_contact(cfg):
    items = dict(build_items(cfg))
    loc = items[f"{NATIVE}/snmp-server/Cisco-IOS-XE-snmp:location"]
    con = items[f"{NATIVE}/snmp-server/Cisco-IOS-XE-snmp:contact"]
    assert loc == {"Cisco-IOS-XE-snmp:location": cfg["snmp"]["location"]}
    assert con == {"Cisco-IOS-XE-snmp:contact": cfg["snmp"]["contact"]}


def test_el_payload_usa_el_mismo_nodo_que_la_ruta(cfg):
    # RESTCONF exige que la raíz del JSON sea el último nodo de la URL.
    for path, body in build_items(cfg):
        ultimo = path.rsplit("/", 1)[-1].split("=")[0]
        nodo = next(iter(body))
        assert nodo.split(":")[-1] == ultimo.split(":")[-1]


def test_otro_loopback_cambia_la_ruta(cfg):
    cfg["loopback"]["id"] = 74
    path, body = build_items(cfg)[0]
    assert path.endswith("Loopback=74")
    assert body["Cisco-IOS-XE-native:Loopback"]["name"] == 74


def test_is_subset_diccionarios():
    assert is_subset({"a": 1}, {"a": 1, "b": 2})
    assert not is_subset({"a": 1}, {"a": 2})
    assert not is_subset({"a": 1}, {"b": 1})


def test_is_subset_anidado():
    assert is_subset({"a": {"b": 1}}, {"a": {"b": 1, "c": 3}, "d": 4})
    assert not is_subset({"a": {"b": 1}}, {"a": {"b": 2}})
    assert not is_subset({"a": {"b": 1}}, {"a": "texto"})


def test_is_subset_compara_como_texto():
    # IOS-XE devuelve a veces números como texto ("201"): deben coincidir.
    assert is_subset({"name": 201}, {"name": "201"})


def test_is_subset_listas():
    assert is_subset({"RO": [None]}, {"RO": [None]})
    assert not is_subset({"RO": [None]}, {"RO": []})
    assert not is_subset({"RO": [None]}, {"RO": None})
