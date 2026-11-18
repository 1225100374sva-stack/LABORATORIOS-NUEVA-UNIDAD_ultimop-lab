"""Fases TEST / DEPLOY / OPERATE con un switch simulado (sin red)."""
from conftest import VARS, FakeSwitch
from deploy import main, reconcile
from payloads import NATIVE, build_items

LOCATION = f"{NATIVE}/snmp-server/Cisco-IOS-XE-snmp:location"


def test_check_no_modifica_el_equipo(cfg, switch):
    cambios = reconcile(cfg, switch, check=True, out=lambda *_: None)
    assert cambios == 4
    assert switch.puts == []
    assert switch.state == {}


def test_deploy_aplica_los_cuatro_recursos(cfg, switch):
    cambios = reconcile(cfg, switch, out=lambda *_: None)
    assert cambios == 4
    assert len(switch.puts) == 4


def test_deploy_es_idempotente(cfg, switch):
    reconcile(cfg, switch, out=lambda *_: None)
    switch.puts.clear()
    cambios = reconcile(cfg, switch, out=lambda *_: None)
    assert cambios == 0
    assert switch.puts == []


def test_corrige_desviacion_manual(cfg, switch):
    reconcile(cfg, switch, out=lambda *_: None)
    switch.state[LOCATION] = {"Cisco-IOS-XE-snmp:location": "alguien-lo-cambio"}
    switch.puts.clear()
    cambios = reconcile(cfg, switch, out=lambda *_: None)
    assert cambios == 1
    assert switch.puts == [LOCATION]
    assert switch.state[LOCATION]["Cisco-IOS-XE-snmp:location"] == cfg["snmp"]["location"]


def test_campos_extra_del_equipo_no_cuentan_como_cambio(cfg):
    estado = {}
    for path, payload in build_items(cfg):
        estado[path] = payload
    lb_path = build_items(cfg)[0][0]
    estado[lb_path] = {"Cisco-IOS-XE-native:Loopback": {
        **estado[lb_path]["Cisco-IOS-XE-native:Loopback"], "shutdown": [None]}}
    sw = FakeSwitch(estado)
    assert reconcile(cfg, sw, out=lambda *_: None) == 0


def test_codigos_http_201_y_204(cfg, switch):
    lineas = []
    reconcile(cfg, switch, out=lineas.append)
    assert all("HTTP 201" in ln for ln in lineas if ln.startswith("[APLICADO]"))
    switch.state[LOCATION] = {"Cisco-IOS-XE-snmp:location": "otro"}
    lineas.clear()
    reconcile(cfg, switch, out=lineas.append)
    assert any("HTTP 204" in ln for ln in lineas)


def test_main_check_por_linea_de_comandos(switch, capsys):
    assert main(["--config", str(VARS), "--check"], client=switch) == 0
    salida = capsys.readouterr().out
    assert "Resumen: 4 cambio(s) pendiente(s)" in salida
    assert switch.puts == []
