# Ejercicio 04 - DevOps con RESTCONF (Cisco IOS-XE)

Configura un Loopback de gestión y SNMP en un Catalyst 8000v (IOS XE 17.12.02,
sandbox reservable de Cisco DevNet) **sin tocar la consola**: todo cambio pasa por
Git -> Pull Request -> pipeline -> RESTCONF.

| Recurso | Valor deseado (`config/vars.yml`) |
|---|---|
| Loopback201 | 10.201.201.1/32, descripción MGMT-LOOPBACK-DEVOPS |
| snmp-server community | DEVOPS-RO (solo lectura) |
| snmp-server location | Lab-DevNet |
| snmp-server contact | equipo@ejemplo.com |

## Estructura

    config/vars.yml            configuración deseada (única fuente de verdad)
    src/restconf_client.py     cliente RESTCONF (GET/PUT, YANG + JSON)
    src/payloads.py            arma los payloads YANG y compara deseado vs. real
    src/deploy.py              aplica (PUT idempotente); --check = prueba en seco
    src/verify.py              monitoreo: PASS/FAIL por recurso
    tests/                     38 pruebas pytest con un switch simulado
    .github/workflows/deploy.yml  pipeline CI/CD

## Pipeline

| Job | Dónde corre | Fase |
|---|---|---|
| Build - lint (yamllint, flake8) | GitHub (ubuntu) | Build |
| Test - unitarias (pytest) | GitHub (ubuntu) | Test |
| Test - prueba en seco (`deploy.py --check`) | runner self-hosted | Test |
| Deploy + Operate + Monitor (solo en `main`) | runner self-hosted | Deploy / Operate / Monitor |

El sandbox reservable solo se alcanza por VPN; por eso los jobs que hablan con el
router corren en un **runner self-hosted** conectado a la VPN de DevNet.
Las credenciales viven en GitHub Secrets (`SANDBOX_USER`, `SANDBOX_PASS`).

## Uso local (solo para pruebas)

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/pytest -v
    export SANDBOX_USER=...  SANDBOX_PASS=...
    .venv/bin/python src/deploy.py --check   # prueba en seco
    .venv/bin/python src/deploy.py           # aplica
    .venv/bin/python src/verify.py           # monitoreo

## Controles contra cambios manuales
- Rama `main` protegida: solo se cambia por Pull Request con checks en verde.
- Credenciales solo en GitHub Secrets, nunca en el repositorio.
- Despliegue únicamente desde el pipeline.
- Historial de Git como auditoría de quién cambió qué y cuándo.
