"""Fase MONITOR: confirma que el estado real coincide con el deseado.

Sale con código 1 si algún recurso no coincide, para que el pipeline falle.
"""
import argparse
import sys

from deploy import load_config
from payloads import build_items, is_subset


def verify(cfg, client, out=print):
    failed = 0
    for path, payload in build_items(cfg):
        current = client.get(path)
        ok = current is not None and is_subset(payload, current)
        out(f"[{'PASS' if ok else 'FAIL'}] {path}")
        failed += 0 if ok else 1
    out(f"\nResumen: {len(build_items(cfg)) - failed} PASS, {failed} FAIL")
    return failed


def main(argv=None, client=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/vars.yml")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    if client is None:
        from restconf_client import RestconfClient
        client = RestconfClient(cfg["host"], cfg.get("port", 443))
    return 1 if verify(cfg, client) else 0


if __name__ == "__main__":
    sys.exit(main())
