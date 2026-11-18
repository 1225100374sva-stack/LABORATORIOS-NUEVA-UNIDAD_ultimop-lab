"""Fases DEPLOY / OPERATE: aplica la configuración por RESTCONF.

    python src/deploy.py --check   # prueba en seco: solo informa
    python src/deploy.py           # aplica con PUT (idempotente)
"""
import argparse
import sys

import yaml

from payloads import build_items, is_subset


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def reconcile(cfg, client, check=False, out=print):
    """Compara deseado vs. real y aplica solo lo que difiere.

    Devuelve el número de recursos que cambiaron (o cambiarían con check=True).
    """
    changes = 0
    for path, payload in build_items(cfg):
        current = client.get(path)
        if current is not None and is_subset(payload, current):
            out(f"[OK]       sin cambios  -> {path}")
            continue
        changes += 1
        if check:
            out(f"[CAMBIO]   se aplicaría -> {path}")
        else:
            code = client.put(path, payload)
            out(f"[APLICADO] HTTP {code}  -> {path}")
    estado = "pendiente(s)" if check else "aplicado(s)"
    out(f"\nResumen: {changes} cambio(s) {estado}")
    return changes


def main(argv=None, client=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/vars.yml")
    ap.add_argument("--check", action="store_true", help="no modifica el equipo")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    if client is None:
        from restconf_client import RestconfClient
        client = RestconfClient(cfg["host"], cfg.get("port", 443))
    reconcile(cfg, client, check=args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
