"""Fase MONITOR: verify.py detecta si el equipo coincide con lo deseado."""
from conftest import VARS
from deploy import reconcile
from verify import main, verify


def test_equipo_vacio_falla(cfg, switch):
    assert verify(cfg, switch, out=lambda *_: None) == 4


def test_despues_del_deploy_todo_pasa(cfg, switch):
    reconcile(cfg, switch, out=lambda *_: None)
    assert verify(cfg, switch, out=lambda *_: None) == 0


def test_codigo_de_salida_para_el_pipeline(cfg, switch, capsys):
    assert main(["--config", str(VARS)], client=switch) == 1
    reconcile(cfg, switch, out=lambda *_: None)
    assert main(["--config", str(VARS)], client=switch) == 0
    assert "4 PASS, 0 FAIL" in capsys.readouterr().out
