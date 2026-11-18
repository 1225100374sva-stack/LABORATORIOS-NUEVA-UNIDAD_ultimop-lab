"""Fase PLAN/CODE: el archivo de variables es válido antes de tocar el equipo."""
import ipaddress


def test_tiene_todas_las_secciones(cfg):
    for clave in ("host", "port", "loopback", "snmp"):
        assert clave in cfg


def test_loopback_id_valido(cfg):
    assert isinstance(cfg["loopback"]["id"], int)
    assert 0 <= cfg["loopback"]["id"] <= 2147483647


def test_ip_y_mascara_validas(cfg):
    lb = cfg["loopback"]
    red = ipaddress.ip_network(f"{lb['ip']}/{lb['mask']}", strict=False)
    assert red.prefixlen == 32, "un Loopback de gestión debe ser /32"


def test_ip_es_privada(cfg):
    assert ipaddress.ip_address(cfg["loopback"]["ip"]).is_private


def test_comunidad_snmp_no_es_por_defecto(cfg):
    assert cfg["snmp"]["community"].lower() not in ("public", "private")


def test_contacto_es_correo(cfg):
    assert "@" in cfg["snmp"]["contact"]


def test_puerto_https(cfg):
    assert cfg["port"] == 443
