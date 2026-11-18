"""
generar_pdf.py
U4ACT04 - Ciclo de vida DevOps con RESTCONF (Cisco IOS-XE)
Autor: Sebastian Villegas Arredondo

Genera el PDF de entrega: portada, mapeo DevOps, pruebas desarrolladas,
evidencias por fase (capturas de evidencias/) y anexo con el código.

Uso:  pip install reportlab pillow  &&  python3 scripts/generar_pdf.py
Si falta una captura, en su lugar aparece un recuadro "Captura pendiente".
"""
import os

from PIL import Image as PI
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(BASE, "evidencias")
OUT = os.path.join(BASE, "U4ACT04_DevOps_RESTCONF_Sebastian_Villegas_Arredondo.pdf")

ALUMNO = "Sebastian Villegas Arredondo"
FECHA = "18/11/2026"
REPO_URL = "github.com/1225100374sva-stack/LABORATORIOS-NUEVA-UNIDAD_ultimop-lab"
AZUL = colors.HexColor("#0B4FA0")

# (archivo en evidencias/, fase, pie de figura)
FIGURAS = [
    ("01_plan_issue.png", "Plan",
     "Issue <b>#1</b> con los requisitos: Loopback201 10.201.201.1/32, comunidad SNMP DEVOPS-RO (RO), "
     "location y contact, y los criterios de aceptación."),
    ("04a_pr_checks_corriendo.png", "Build / Test",
     "Pull Request <b>#2</b> (feature/loopback-snmp → main) recién abierto: el pipeline arranca solo "
     "con el job Build - lint."),
    ("04_release_pr_checks.png", "Build / Test / Release",
     "PR #2 con <b>All checks have passed</b>: lint, pruebas unitarias y prueba en seco contra el "
     "router (en el runner self-hosted). Deploy queda <i>skipped</i> porque solo corre en main."),
    ("05b_run_rojo_resumen.png", "Deploy",
     "Primer pipeline en <b>main</b> tras el merge del PR #2: build, test y dry-run en verde; el job "
     "<b>Deploy + Operate + Monitor</b> termina en rojo."),
    ("05c_verify_fail.png", "Monitor",
     "El deploy sí aplicó la configuración, pero <b>verify.py</b> marcó 2 FAIL (Loopback201 y "
     "community). Causa: IOS-XE responde los nodos lista como <b>[{...}]</b> y la comparación esperaba "
     "un objeto. El pipeline detuvo la entrega: la fase Monitor funcionó."),
    ("05_pr3_fix_creado.png", "Code",
     "Corrección en la rama <b>fix/verify-listas-yang</b>: is_subset acepta nodos lista y se agregan "
     "2 pruebas con la forma real de la respuesta (38 en total). Nunca se tocó la consola del router."),
    ("06b_pr3_checks.png", "Test / Release", "PR <b>#3</b> con todos los checks en verde."),
    ("06c_pr3_merged.png", "Release", "PR #3 con merge a main."),
    ("06_actions_main.png", "Deploy",
     "Historial en Actions: el run rojo del primer deploy y el run verde después del fix."),
    ("07a_deploy_pasos.png", "Deploy",
     "Job <b>Deploy + Operate + Monitor</b> en verde, con sus pasos: Deploy (PUT RESTCONF), Operate "
     "(segunda corrida) y Monitor (verify.py)."),
    ("07_log_deploy.png", "Operate / Monitor",
     "Operate: la corrida muestra <b>[OK] sin cambios</b> en los 4 recursos (PUT idempotente, "
     "0 cambios). Monitor: <b>verify.py</b> da <b>4 PASS, 0 FAIL</b>."),
    ("08_tag_release.png", "Release", "Release con el tag <b>v1.0</b> sobre main."),
    ("10_runner_self_hosted.png", "Control de cambios",
     "Runner <b>self-hosted</b> mac-sebas (mi Mac conectada a la VPN del sandbox)."),
    ("11_secrets.png", "Control de cambios",
     "Credenciales guardadas solo en <b>GitHub Secrets</b> (SANDBOX_USER, SANDBOX_PASS)."),
    ("12_branch_protection.png", "Control de cambios",
     "Protección de la rama <b>main</b>: cambios solo por Pull Request con checks en verde."),
]

SUP = "/System/Library/Fonts/Supplemental/"
for nombre, archivo in [("AR", "Arial.ttf"), ("AR-B", "Arial Bold.ttf"),
                        ("AR-I", "Arial Italic.ttf"), ("AR-BI", "Arial Bold Italic.ttf")]:
    pdfmetrics.registerFont(TTFont(nombre, SUP + archivo))
pdfmetrics.registerFontFamily("AR", normal="AR", bold="AR-B", italic="AR-I", boldItalic="AR-BI")
F, MONO = "AR", "Courier"

T = ParagraphStyle("T", fontName=F, fontSize=24, leading=30, textColor=AZUL, spaceAfter=10)
H1 = ParagraphStyle("H1", fontName=F, fontSize=16, leading=20, textColor=AZUL, spaceBefore=4,
                    spaceAfter=10)
H2 = ParagraphStyle("H2", fontName=F, fontSize=12, leading=15, spaceBefore=8, spaceAfter=5)
P = ParagraphStyle("P", fontName=F, fontSize=10.5, leading=15, spaceAfter=6)
CELL = ParagraphStyle("C", fontName=F, fontSize=9, leading=11.5)
CAP = ParagraphStyle("CAP", parent=P, fontSize=9, leading=12, textColor=colors.HexColor("#4b5563"))
CODE = ParagraphStyle("CODE", fontName=MONO, fontSize=7.2, leading=9.2,
                      backColor=colors.HexColor("#f3f4f6"), borderPadding=6)

ANCHO = letter[0] - 2 * 0.8 * inch


def tabla(filas, anchos):
    datos = [[Paragraph(str(c), CELL) for c in f] for f in filas]
    t = Table(datos, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3b5b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2f7")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5cfdb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    for i in range(len(filas[0])):
        datos[0][i] = Paragraph(f"<font color='white'><b>{filas[0][i]}</b></font>", CELL)
    return t


def figura(n, archivo, fase, pie):
    ruta = os.path.join(EVID, archivo)
    cab = Paragraph(f"<b>Figura {n}.</b> [{fase}] {pie}", CAP)
    if not os.path.exists(ruta):
        caja = Table([[Paragraph(f"Captura pendiente: {archivo}", CELL)]],
                     colWidths=[ANCHO], rowHeights=[1.2 * inch])
        caja.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.red),
                                  ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        return KeepTogether([caja, cab, Spacer(1, 10)])
    w, h = PI.open(ruta).size
    alto_max = 6.6 * inch
    esc = min(ANCHO / w, alto_max / h)
    img = Image(ruta, width=w * esc, height=h * esc)
    return KeepTogether([img, Spacer(1, 4), cab, Spacer(1, 14)])


def codigo(rel):
    with open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return [Paragraph(f"<b>{rel}</b>", H2), Preformatted(f.read(), CODE), Spacer(1, 8)]


def pie_pagina(c, doc):
    c.saveState()
    c.setFont(F, 8)
    c.setFillColor(colors.HexColor("#6b7280"))
    c.drawString(0.8 * inch, 0.5 * inch, f"U4ACT04 DevOps con RESTCONF · {ALUMNO}")
    c.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, f"Página {doc.page}")
    c.restoreState()


def main():
    h = []
    h += [Spacer(1, 1.6 * inch),
          Paragraph("U4ACT04 · Ciclo de vida DevOps con RESTCONF", T),
          Paragraph("Loopback de gestión y SNMP en un Cisco Catalyst 8000v (IOS XE 17.12.02) "
                    "sin cambios manuales por consola: Git → Pull Request → pipeline → RESTCONF.", P),
          Spacer(1, 0.4 * inch),
          tabla([["Dato", "Valor"],
                 ["Alumno", ALUMNO],
                 ["Fecha", FECHA],
                 ["Repositorio", REPO_URL],
                 ["Equipo", "Sandbox reservable DevNet Catalyst 8000v, 10.10.20.48 (VPN)"],
                 ["Herramientas", "Python 3, requests, PyYAML, pytest, flake8, yamllint, GitHub Actions"]],
                [1.6 * inch, ANCHO - 1.6 * inch]),
          PageBreak()]

    h += [Paragraph("1. Mapeo del escenario al ciclo DevOps", H1),
          tabla([["Fase", "Qué se hizo", "Evidencia"],
                 ["Plan", "Requisitos de Loopback201 y SNMP", "Issue #1 (Fig. 1)"],
                 ["Code", "config/vars.yml + src/*.py en Git, ramas feature/ y fix/", "Fig. 6"],
                 ["Build", "yamllint y flake8 en el pipeline", "Fig. 2, 3"],
                 ["Test", "38 pruebas pytest + deploy.py --check contra el router", "Fig. 3, 7, sec. 4"],
                 ["Release", "PR #2 (cierra #1) y PR #3 (fix), merge a main, tag v1.0", "Fig. 3, 8, 12"],
                 ["Deploy", "El pipeline aplica por RESTCONF (PUT) desde main", "Fig. 4, 9, 10"],
                 ["Operate", "Corrida idempotente: [OK] sin cambios", "Fig. 11"],
                 ["Monitor", "verify.py detectó un FAIL real (Fig. 5) y tras el fix da 4 PASS", "Fig. 5, 11"]],
                [0.9 * inch, 3.9 * inch, ANCHO - 4.8 * inch]),
          Spacer(1, 12),
          Paragraph("2. Configuración deseada (config/vars.yml)", H1),
          tabla([["Recurso", "Ruta YANG (RESTCONF)", "Valor"],
                 ["Loopback201", "native/interface/Loopback=201", "10.201.201.1 255.255.255.255, "
                  "MGMT-LOOPBACK-DEVOPS"],
                 ["Community", "native/snmp-server/Cisco-IOS-XE-snmp:community=DEVOPS-RO",
                  "DEVOPS-RO, solo lectura (RO)"],
                 ["Location", "native/snmp-server/Cisco-IOS-XE-snmp:location", "Lab-DevNet"],
                 ["Contact", "native/snmp-server/Cisco-IOS-XE-snmp:contact", "equipo@ejemplo.com"]],
                [1.0 * inch, 3.4 * inch, ANCHO - 4.4 * inch]),
          Spacer(1, 12),
          Paragraph("3. Pipeline (.github/workflows/deploy.yml)", H1),
          Paragraph("El sandbox reservable solo se alcanza por VPN, así que los runners de GitHub no "
                    "llegan al router. Por eso los jobs que hablan con el equipo corren en un "
                    "<b>runner self-hosted</b> (mi Mac conectada a la VPN), mientras que el lint y las "
                    "pruebas unitarias corren en ubuntu-latest. El job deploy solo corre en "
                    "<b>main</b> y solo si los anteriores pasaron.", P),
          tabla([["Job", "Runner", "Qué hace"],
                 ["Build - lint", "ubuntu-latest", "yamllint config .github · flake8 src tests"],
                 ["Test - unitarias", "ubuntu-latest", "pytest -v (38 pruebas, switch simulado)"],
                 ["Test - prueba en seco", "self-hosted", "deploy.py --check contra 10.10.20.48"],
                 ["Deploy + Operate + Monitor", "self-hosted",
                  "deploy.py · deploy.py otra vez ([OK]) · verify.py"]],
                [1.9 * inch, 1.1 * inch, ANCHO - 3.0 * inch]),
          PageBreak()]

    h += [Paragraph("4. Pruebas desarrolladas", H1),
          Paragraph("Además de las 3 pruebas del ejemplo, desarrollé una batería de <b>38 pruebas</b>. "
                    "Usan un <b>switch simulado</b> (FakeSwitch) que guarda la configuración en un "
                    "diccionario, así se prueban deploy.py y verify.py sin red ni credenciales.", P),
          tabla([["Archivo", "Pruebas", "Qué valida"],
                 ["test_vars.py", "7", "vars.yml completo; IP válida, privada y /32; ID de Loopback "
                  "válido; comunidad distinta de public/private; contacto con @; puerto 443"],
                 ["test_payloads.py", "12", "4 recursos; rutas bajo native; JSON del Loopback, community "
                  "RO, location y contact; raíz del JSON igual al último nodo de la URL; is_subset con "
                  "diccionarios, anidados, listas, números como texto y nodos lista [{...}] de IOS-XE"],
                 ["test_deploy.py", "8", "--check no modifica el equipo; deploy aplica 4 recursos; "
                  "idempotencia (2a corrida = 0 cambios); corrige una desviación manual; campos extra "
                  "del equipo no cuentan como cambio; códigos 201/204; CLI; respuesta real de IOS-XE con listas"],
                 ["test_verify.py", "3", "equipo vacío = 4 FAIL; tras deploy = 0 FAIL; código de salida "
                  "1/0 para que el pipeline falle o pase"],
                 ["test_restconf_client.py", "8", "URL base, credenciales desde variables de entorno, "
                  "cabeceras yang-data+json, 404 → None, 401/400 lanzan error, PUT devuelve código"]],
                [1.5 * inch, 0.6 * inch, ANCHO - 2.1 * inch]),
          Spacer(1, 12),
          Paragraph("5. Controles contra cambios manuales", H1),
          Paragraph("• Rama <b>main</b> protegida: solo cambia por Pull Request con los checks en verde. "
                    "Como trabajé solo, no se exige aprobación de un segundo revisor (GitHub no permite "
                    "aprobar el PR propio).<br/>"
                    "• Credenciales solo en <b>GitHub Secrets</b>; el repositorio no tiene contraseñas.<br/>"
                    "• El despliegue solo ocurre desde el pipeline; nunca entré a la consola del router.<br/>"
                    "• El runner self-hosted solo ejecuta PRs del propio repositorio (no de forks).<br/>"
                    "• VERIFY_SSL=false solo por el certificado autofirmado del sandbox.<br/>"
                    "• El historial de Git registra quién cambió qué y cuándo.", P),
          Paragraph("Salida local de pytest -v y lint", H2),
          Preformatted(open(os.path.join(EVID, "pytest_local.txt"), encoding="utf-8").read(), CODE),
          PageBreak(),
          Paragraph("6. Evidencias", H1)]
    for n, (archivo, fase, pie) in enumerate(FIGURAS, 1):
        h.append(figura(n, archivo, fase, pie))

    h += [PageBreak(), Paragraph("Anexo. Código", H1)]
    for rel in ["config/vars.yml", ".github/workflows/deploy.yml", "src/restconf_client.py",
                "src/payloads.py", "src/deploy.py", "src/verify.py", "tests/conftest.py",
                "tests/test_deploy.py", "tests/test_payloads.py"]:
        h += codigo(rel)

    SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.8 * inch, bottomMargin=0.8 * inch,
                      title="U4ACT04 DevOps con RESTCONF", author=ALUMNO).build(
        h, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    print(OUT)


if __name__ == "__main__":
    main()
