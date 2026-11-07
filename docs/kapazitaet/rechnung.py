#!/usr/bin/env python3
"""Waybuild Analytics – Kapazitätsrechnung 25 bis 1.000 Websites (Schritte von 25).

Auftrag: Can, Talk 63yitbs3, #4889, 07.11.2026 06:26.
Aufruf:  python3 docs/kapazitaet/rechnung.py
Ergebnis: ergebnis.json, ergebnis.csv und kapazitaet.html im selben Ordner.
Das PDF entsteht aus kapazitaet.html mit Chromium (Playwright 1.48.2), siehe pdf.mjs.

Alle Werte mit "Annahme" sind Schätzungen. Werte mit "Messung" stammen vom
Demo-Server (07.11.2026). Werte mit "Quelle" stehen in QUELLEN.
Nur Standardbibliothek, keine Abhängigkeiten.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

HIER = Path(__file__).resolve().parent
STAND = "07.11.2026"

# ---------------------------------------------------------------------------
# 1. Ist-Daten (Messung auf dem Nextcloud-Server, 07.11.2026 ca. 07:30, nur lesend)
# ---------------------------------------------------------------------------
IST = {
    "cpu": "8 vCPU, AMD EPYC (KVM, virtueller Server)",
    "ram_gb": 23.5,
    "ram_belegt_gb": 13.0,
    "ram_verfuegbar_gb": 9.7,
    "swap": "keiner",
    "disk_gb": 290,
    "disk_belegt_gb": 182,
    "disk_frei_gb": 109,
    "last": "0,57 / 0,59 / 0,81 (1 / 5 / 15 Minuten) bei 8 Kernen, CPU zu ca. 92–95 % frei",
    "container": 34,
    "laufzeit": "19 Tage ohne Neustart",
    "ram_grosse": [
        ("Hindsight (KI-Gedächtnis, Test)", 1.96),
        ("Euro-Office (2 Container, Dokumente)", 2.30),
        ("Nextcloud", 1.34),
        ("ClamAV (Virenscanner)", 0.95),
        ("Paperless", 0.71),
        ("CRM-Spracherkennung", 0.53),
        ("Nextcloud-Datenbank", 0.50),
        ("Waybuild-Analytics-Demo (Matomo, MariaDB, Archiv)", 0.57),
    ],
    "disk_grosse": [
        ("Container-Images und Container-Dateien (containerd)", 102),
        ("Nextcloud-Sicherungen (/opt/nextcloud-backup)", 35),
        ("Benutzerordner (/home)", 14),
        ("Docker-Volumes (Datenbanken, Dateien)", 11),
        ("Temporäre Dateien (/tmp)", 9),
        ("Filmwerk (Video-Werkzeug)", 6),
    ],
    # Demo Waybuild Analytics (4 Demo-Websites, Testdaten 07.10.–05.11.2026)
    "demo_db_mb": 26.7,
    "demo_db_platte_mb": 238,
    "demo_rohdaten_mb": 4.4,
    "demo_archive_mb": 21.4,
    "demo_besuche": 2879,
    "demo_aktionen": 9442,
    "demo_archiv_lauf_s": 33,
    "demo_archiv_cpu": 0.5,
    "demo_websites": 4,
}

# ---------------------------------------------------------------------------
# 2. Annahmen
# ---------------------------------------------------------------------------
SZENARIEN = {  # Seitenaufrufe je Website und Monat (Annahme)
    "niedrig": 1_000,
    "mittel": 2_000,
    "hoch": 10_000,
}
BOT_ABRUFE = {  # Bot-Abrufe in den Server-Logs je Website und Monat (Annahme)
    "niedrig": 1_500,
    "mittel": 3_000,
    "hoch": 8_000,
}
A = {
    "treffer_je_aufruf": 1.3,       # Annahme: Seitenaufruf plus Klick-/Ziel-Ereignisse
    "spitzenfaktor": 10,            # Annahme: Spitze = 10 × Durchschnitt pro Sekunde
    "kb_roh_je_treffer": 0.4,       # Messung Demo: 4,4 MB für ~9.400 Aktionen + 2.900 Besuche ≈ 0,41 KB
    "roh_monate": 6,                # Einstellung: Rohdaten 180 Tage (Spec 4.8, Demo)
    "archiv_mb_basis": 1.0,         # Annahme aus Messung: Demo 0,6 MB Nutzdaten / 2,5 MB Platte je Website und Monat
    "archiv_mb_je_1000_aufrufe": 0.1,
    "archiv_monate": 25,            # Spec 4.8: Berichte 25 Monate
    "matomo_gb_je_mio_aufrufe": 0.2,  # Quelle Matomo: ca. 1 GB je 5 Mio. Seitenaufrufe (Gegenprobe)
    # Archivierung
    "archiv_cpu_s_je_website": 4.0,  # Messung Demo: 33 s Laufzeit, 4 Websites, 0,5 CPU ≈ 4 CPU-Sekunden je Website
    "archiv_cpu_s_je_1000_treffer_tag": 2.0,  # Annahme: Mehraufwand für die Tagesdaten
    "archiv_ziel_min": 30,          # Ziel: stündlicher Lauf ist nach 30 Minuten fertig
    "archiv_max_parallel": 3,       # Quelle Matomo: mehr als 2–3 parallele Prozesse bringen wenig
    # Postgres (eigene App)
    "fragen": 30,                   # Plan 1d: höchstens 30 aktive Fragen je Website
    "wiederholungen": 3,            # Plan 1d: jede Frage 3-mal je Anbieter
    "anbieter_mvp": 2,              # Claude + ChatGPT
    "anbieter_v2": 4,               # + Gemini + Perplexity
    "kb_je_ki_antwort": 6.0,        # Annahme: Antworttext, Quellen, Auswertung (ohne volles Roh-JSON)
    "ki_monate": 25,                # Spec 4.8
    "kb_je_bot_zeile": 0.5,         # Annahme
    "bot_roh_monate": 3,            # Spec 4.8: Bot-Rohdaten 90 Tage
    "pg_mb_sonstiges_je_website_monat": 0.2,  # Annahme: Kennzahlen-Cache, Logbuch, Berichte-Metadaten
    "pg_basis_gb": 0.2,
    # Crawler-Logs (Hoster-Logs, werden gestreamt, nicht gespeichert)
    "log_zeilen_je_aufruf": 15,     # Annahme: Seite plus Bilder, CSS, JS
    "bytes_je_logzeile": 250,       # Annahme
    "gzip_anteil": 0.10,            # Annahme: gzip auf ca. 10 %
    # Sicherung
    "backup_faktor": 0.9,           # Annahme: gepackt ~30 % × ~3 Stände (7 täglich, 4 wöchentlich, 6 monatlich, restic)
    # Berichte
    "pdf_s_je_bericht": 5,          # Annahme
}

# KI-Preise (USD) – geprüft am 07.11.2026, siehe QUELLEN
USD_IN_EUR = 0.90  # Annahme wie Plan 1d (WA_USD_IN_EUR), nicht tagesaktuell
KI = {
    "claude": {  # Antwort-Modell Claude Opus 5.5 (Plan 1d), Websuche
        "name": "Claude (Opus 5.5 + Websuche)",
        "ein_usd_mtok": 4.00, "aus_usd_mtok": 20.00, "suche_usd": 0.010,
        "ein_tok": 15_000, "aus_tok": 1_000, "suchen": 2,   # Token und Suchen: Annahme
        "geprueft": True,
    },
    "openai": {  # Modell im Plan offen; Annahme: gpt-5.6-terra
        "name": "ChatGPT (gpt-5.6-terra + web_search, Annahme)",
        "ein_usd_mtok": 2.00, "aus_usd_mtok": 12.00, "suche_usd": 0.010,
        "ein_tok": 8_000, "aus_tok": 1_000, "suchen": 1,
        "geprueft": True,
    },
    "gemini": {  # V2, Preis NICHT geprüft (Spec 4.6, Sekundärquellen)
        "name": "Gemini (Grounding, V2, ungeprüft)",
        "pauschal_usd": 0.040, "geprueft": False,
    },
    "perplexity": {  # V2, Preis NICHT geprüft
        "name": "Perplexity Sonar (V2, ungeprüft)",
        "pauschal_usd": 0.015, "geprueft": False,
    },
    "haiku": {  # Auswertung jeder Antwort
        "name": "Auswertung Claude Haiku 5.5",
        "ein_usd_mtok": 0.10, "aus_usd_mtok": 0.50, "suche_usd": 0.0,
        "ein_tok": 3_000, "aus_tok": 300, "suchen": 0,
        "geprueft": True,
    },
}
KI_BUDGET_EUR_JE_KUNDE = 10.0   # Plan 1d / D5
WEBSITES_JE_KUNDE = 1           # Annahme für die Budget-Rechnung

# Server (Hetzner Cloud, eu-central, netto, abgerufen 07.11.2026; Verfügbarkeit vor Bestellung prüfen)
SERVER_GETEILT = [  # Regular Performance (geteilte vCPU)
    ("CPX22", 2, 4, 80, 19.99),
    ("CPX32", 4, 8, 160, 35.99),
    ("CPX42", 8, 16, 320, 69.99),
    ("CPX52", 12, 24, 480, 100.99),
    ("CPX62", 16, 32, 640, 130.49),
]
SERVER_DB = [  # General Purpose (eigene vCPU) für die getrennte Datenbank
    ("CCX13", 2, 8, 80, 43.49),
    ("CCX23", 4, 16, 160, 86.49),
    ("CCX33", 8, 32, 240, 138.99),
    ("CCX43", 16, 64, 360, 276.49),
]
STORAGE_BOX = [("BX11", 1000, 3.20), ("BX21", 5000, 10.90)]  # Sicherung, GB, € netto

# Ampel-Grenzen (eigene Festlegung, begründet im PDF)
GRUEN = {"ram_gb": 6.0, "vcpu": 3, "disk_gb": 50}   # passt neben Nextcloud (9,7 GB RAM frei, 109 GB Platte frei)
EIN_SERVER = {"ram_gb": 16.0, "vcpu": 8, "treffer_mio": 5.0}  # Quelle Matomo: ab ~1–5 Mio. Treffern/Monat eigene DB

# ---------------------------------------------------------------------------
# 3. Rechnung
# ---------------------------------------------------------------------------

def ki_kosten_usd_je_abfrage(k: dict) -> float:
    if "pauschal_usd" in k:
        return k["pauschal_usd"]
    return (k["ein_tok"] * k["ein_usd_mtok"] + k["aus_tok"] * k["aus_usd_mtok"]) / 1e6 + k["suchen"] * k["suche_usd"]


def ki_je_website() -> dict:
    je = A["fragen"] * A["wiederholungen"]          # 90 Abfragen je Anbieter
    mvp = ["claude", "openai"]
    v2 = mvp + ["gemini", "perplexity"]
    def summe(liste):
        abfragen = je * len(liste)
        usd = sum(je * ki_kosten_usd_je_abfrage(KI[a]) for a in liste)
        usd += abfragen * ki_kosten_usd_je_abfrage(KI["haiku"])   # jede Antwort wird ausgewertet
        return abfragen, usd
    a1, u1 = summe(mvp)
    a2, u2 = summe(v2)
    return {
        "abfragen_mvp": a1, "usd_mvp": u1, "eur_mvp": u1 * USD_IN_EUR,
        "abfragen_v2": a2, "usd_v2": u2, "eur_v2": u2 * USD_IN_EUR,
        "je_abfrage_usd": {k: ki_kosten_usd_je_abfrage(v) for k, v in KI.items()},
    }


KI_W = ki_je_website()


def waehle(liste, ram, vcpu, disk):
    for name, c, r, d, preis in liste:
        if r >= ram and c >= vcpu and d >= disk:
            return {"name": name, "vcpu": c, "ram": r, "disk": d, "eur": preis}
    return None


def stufe(n: int, szenario: str) -> dict:
    pv = SZENARIEN[szenario]
    pv_ges = n * pv
    treffer = pv_ges * A["treffer_je_aufruf"]
    spitze = treffer / (30 * 86_400) * A["spitzenfaktor"]

    # Matomo-Datenbank (MariaDB)
    roh_gb = treffer * A["roh_monate"] * A["kb_roh_je_treffer"] / 1e6
    archiv_mb_monat = A["archiv_mb_basis"] + A["archiv_mb_je_1000_aufrufe"] * pv / 1000
    archiv_gb_jahr = n * archiv_mb_monat * 12 / 1000
    matomo_jahr1 = roh_gb + archiv_gb_jahr
    matomo_dauer = roh_gb + n * archiv_mb_monat * A["archiv_monate"] / 1000
    matomo_regel = pv_ges * 12 / 1e6 * A["matomo_gb_je_mio_aufrufe"]

    # Postgres (eigene App)
    ki_abfragen_w = A["fragen"] * A["wiederholungen"] * A["anbieter_mvp"]
    ki_mb_monat = ki_abfragen_w * A["kb_je_ki_antwort"] / 1000
    bot_mb_monat = BOT_ABRUFE[szenario] * A["kb_je_bot_zeile"] / 1000
    pg_jahr1 = A["pg_basis_gb"] + n * (ki_mb_monat * 12 + bot_mb_monat * A["bot_roh_monate"]
                                       + A["pg_mb_sonstiges_je_website_monat"] * 12) / 1000
    pg_dauer = A["pg_basis_gb"] + n * (ki_mb_monat * A["ki_monate"] + bot_mb_monat * A["bot_roh_monate"]
                                       + A["pg_mb_sonstiges_je_website_monat"] * 25) / 1000

    # Archivierung (stündlich)
    treffer_tag_w = pv * A["treffer_je_aufruf"] / 30
    cpu_s_lauf = n * (A["archiv_cpu_s_je_website"] + A["archiv_cpu_s_je_1000_treffer_tag"] * treffer_tag_w / 1000)
    parallel = 1
    while parallel < A["archiv_max_parallel"] and cpu_s_lauf / parallel > A["archiv_ziel_min"] * 60:
        parallel += 1
    lauf_min = cpu_s_lauf / parallel / 60
    archiv_takt_h = 1 if lauf_min <= 45 else math.ceil(lauf_min / 45)

    # Crawler-Logs
    log_zeilen = n * (pv * A["log_zeilen_je_aufruf"] + BOT_ABRUFE[szenario])
    log_gb_roh = log_zeilen * A["bytes_je_logzeile"] / 1e9
    log_gb_gz = log_gb_roh * A["gzip_anteil"]
    bot_zeilen = n * BOT_ABRUFE[szenario]

    # Redis / Queued Tracking ab 1 Mio. Treffer im Monat (unsere Empfehlung, angelehnt an Matomo Tier 2)
    redis = treffer >= 1_000_000

    # RAM (GB)
    ram_teile = {
        "System, Caddy, Überwachung": 0.7,
        "Matomo Web (Tracking, API)": 0.5 + 0.02 * spitze,
        "Matomo-Archivierung": 0.5 * parallel,
        "MariaDB": 0.5 + 0.30 * matomo_dauer,
        "App (Node) + MCP": 0.3,
        "PDF-Berichte (Chromium)": 0.7,
        "Postgres": 0.3 + 0.10 * pg_dauer,
        "Redis": 0.25 if redis else 0.0,
    }
    ram = sum(ram_teile.values()) * 1.25
    ram_db = (ram_teile["MariaDB"]) * 1.25 + 1.0

    # vCPU
    # Kerne, damit der Archiv-Lauf in 30 Minuten fertig ist (mindestens ein halber Kern), × 1,5 für die Datenbank
    archiv_kerne = max(0.5, cpu_s_lauf / (A["archiv_ziel_min"] * 60))
    vcpu_roh = 1.0 + 0.03 * spitze + 1.5 * archiv_kerne
    vcpu = max(2, math.ceil(vcpu_roh * 1.25))

    disk = 20 + (matomo_dauer + pg_dauer) * 1.5 + 10

    # Ampel
    ram_neben_nc = ram - 0.7 * 1.25
    treffer_mio = treffer / 1e6
    if ram_neben_nc <= GRUEN["ram_gb"] and vcpu <= GRUEN["vcpu"] and disk - 20 <= GRUEN["disk_gb"]:
        ampel = "gruen"
    elif ram <= EIN_SERVER["ram_gb"] and vcpu <= EIN_SERVER["vcpu"] and treffer_mio <= EIN_SERVER["treffer_mio"]:
        ampel = "gelb"
    else:
        ampel = "rot"

    # Server wählen
    if ampel in ("gruen", "gelb"):
        s = waehle(SERVER_GETEILT, ram, vcpu, disk)
        server_text = s["name"]
        server_eur = s["eur"]
        server_detail = f'{s["name"]} ({s["vcpu"]} vCPU, {s["ram"]} GB)'
    else:
        db = waehle(SERVER_DB, ram_db, 2 if matomo_dauer < 40 else 4, 20 + matomo_dauer * 1.5)
        app = waehle(SERVER_GETEILT, ram - ram_teile["MariaDB"] * 1.25 + 0.7, max(2, vcpu - db["vcpu"] // 2),
                     20 + pg_dauer * 1.5 + 10)
        server_text = f'{app["name"]} + {db["name"]}'
        server_eur = app["eur"] + db["eur"]
        server_detail = f'App {app["name"]} ({app["vcpu"]} vCPU, {app["ram"]} GB) + DB {db["name"]} ({db["vcpu"]} vCPU, {db["ram"]} GB)'

    backup_gb = (matomo_dauer + pg_dauer) * A["backup_faktor"]
    box = next(b for b in STORAGE_BOX if b[1] >= backup_gb)
    kosten_infra = server_eur + box[2]

    ki_eur = n * KI_W["eur_mvp"]
    ki_eur_budget = n * min(KI_W["eur_mvp"], KI_BUDGET_EUR_JE_KUNDE / WEBSITES_JE_KUNDE)
    pdf_min = n * A["pdf_s_je_bericht"] / 60

    return {
        "websites": n, "szenario": szenario,
        "aufrufe_monat": pv_ges, "treffer_monat": round(treffer), "spitze_rps": spitze,
        "matomo_gb_jahr1": matomo_jahr1, "matomo_gb_dauer": matomo_dauer, "matomo_gb_regel": matomo_regel,
        "pg_gb_jahr1": pg_jahr1, "pg_gb_dauer": pg_dauer,
        "vcpu": vcpu, "ram_gb": ram, "disk_gb": disk,
        "archiv_cpu_s": cpu_s_lauf, "archiv_parallel": parallel, "archiv_min": lauf_min, "archiv_takt_h": archiv_takt_h,
        "log_gb_gz_monat": log_gb_gz, "log_gb_roh_monat": log_gb_roh, "bot_zeilen_monat": bot_zeilen,
        "ki_abfragen_mvp": n * KI_W["abfragen_mvp"], "ki_abfragen_v2": n * KI_W["abfragen_v2"],
        "ki_eur_mvp": ki_eur, "ki_eur_mit_budget": ki_eur_budget, "ki_eur_v2": n * KI_W["eur_v2"],
        "backup_gb": backup_gb, "backup_box": box[0], "backup_eur": box[2],
        "server": server_text, "server_detail": server_detail, "server_eur": server_eur,
        "infra_eur": kosten_infra, "infra_eur_je_website": kosten_infra / n,
        "gesamt_eur_je_website": (kosten_infra + ki_eur_budget) / n,
        "redis": redis, "pdf_min": pdf_min, "ampel": ampel,
        "ram_teile": {k: round(v * 1.25, 2) for k, v in ram_teile.items()},
    }


STUFEN = list(range(25, 1001, 25))
ERG = {sz: [stufe(n, sz) for n in STUFEN] for sz in SZENARIEN}


def schwelle(sz: str, farbe: str):
    for z in ERG[sz]:
        if z["ampel"] == farbe:
            return z["websites"]
    return None


def erste(sz: str, bedingung):
    for z in ERG[sz]:
        if bedingung(z):
            return z["websites"]
    return None


SCHWELLEN = {
    sz: {
        "gelb_ab": schwelle(sz, "gelb"),
        "rot_ab": schwelle(sz, "rot"),
        "redis_ab": erste(sz, lambda z: z["redis"]),
        "parallel_archiv_ab": erste(sz, lambda z: z["archiv_parallel"] > 1),
        "archiv_takt_ab": erste(sz, lambda z: z["archiv_takt_h"] > 1),
        "cpx42_ab": erste(sz, lambda z: z["server"].startswith("CPX42") or "+" in z["server"]),
    }
    for sz in SZENARIEN
}

# ---------------------------------------------------------------------------
# 4. Ausgabe JSON / CSV
# ---------------------------------------------------------------------------

def schreibe_daten():
    (HIER / "ergebnis.json").write_text(json.dumps({
        "stand": STAND, "ist": IST, "annahmen": A, "szenarien": SZENARIEN, "bot_abrufe": BOT_ABRUFE,
        "ki": KI, "ki_je_website": KI_W, "usd_in_eur": USD_IN_EUR, "schwellen": SCHWELLEN, "stufen": ERG,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    felder = [k for k in ERG["mittel"][0] if k != "ram_teile"]
    with open(HIER / "ergebnis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=felder, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for sz in SZENARIEN:
            for z in ERG[sz]:
                w.writerow(z)


# ---------------------------------------------------------------------------
# 5. HTML
# ---------------------------------------------------------------------------

def de(x, nk=0):
    s = f"{x:,.{nk}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def gb(x):
    if x < 1:
        return de(x * 1000, 0) + " MB"
    return de(x, 1 if x < 10 else 0) + " GB"


AMPEL_TXT = {"gruen": "grün", "gelb": "gelb", "rot": "rot"}
AMPEL_ZEICHEN = {"gruen": "●", "gelb": "▲", "rot": "■"}


def ampel_span(a):
    return f'<span class="amp {a}">{AMPEL_ZEICHEN[a]} {AMPEL_TXT[a]}</span>'


FARBEN = {"niedrig": "#6b4fa0", "mittel": "#00a6a1", "hoch": "#c27c0e"}
STRICH = {"niedrig": "6 4", "mittel": "", "hoch": "2 3"}


def diagramm(titel, feld, einheit, linien=None, w=560, h=300, fmt=lambda v: de(v, 0), ymax=None, ref_links=False):
    """Einfaches Liniendiagramm als SVG (statisch, für das PDF)."""
    l, r, o, u = 56, 92, 34, 44
    pw, ph = w - l - r, h - o - u
    werte = [z[feld] for sz in SZENARIEN for z in ERG[sz]]
    roh = (ymax / 1.05) if ymax else max(werte + [v for v, _ in (linien or [])]) * 1.05
    k = 10 ** math.floor(math.log10(roh / 5))
    schritt = next(f * k for f in (1, 2, 2.5, 5, 10) if f * k * 5 >= roh)
    top = schritt * 5
    def x(n):
        return l + (n - 25) / (1000 - 25) * pw
    def y(v):
        return o + ph - v / top * ph
    teile = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{titel}">',
             f'<text x="{l}" y="18" class="dt">{titel}</text>']
    # Gitter
    schritte = 5
    for i in range(schritte + 1):
        v = top / schritte * i
        teile.append(f'<line x1="{l}" x2="{l + pw}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="gl"/>')
        teile.append(f'<text x="{l - 8}" y="{y(v) + 4:.1f}" class="ax" text-anchor="end">{fmt(v)}</text>')
    for n in (25, 200, 400, 600, 800, 1000):
        teile.append(f'<text x="{x(n):.1f}" y="{o + ph + 18}" class="ax" text-anchor="middle">{de(n)}</text>')
    teile.append(f'<text x="{l + pw / 2}" y="{h - 6}" class="ax" text-anchor="middle">Anzahl Websites</text>')
    teile.append(f'<text x="{l - 44}" y="{o - 12}" class="ax">{einheit}</text>')
    # Referenzlinien
    for v, txt in (linien or []):
        teile.append(f'<line x1="{l}" x2="{l + pw}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="ref"/>')
        if ref_links:
            teile.append(f'<text x="{l + 4}" y="{y(v) + 13:.1f}" class="reft">{txt}</text>')
        else:
            teile.append(f'<text x="{l + pw - 4}" y="{y(v) + 13:.1f}" class="reft" text-anchor="end">{txt}</text>')
    # Linien
    labels = []
    for sz in SZENARIEN:
        pts = " ".join(f"{x(z['websites']):.1f},{y(z[feld]):.1f}" for z in ERG[sz])
        dash = f' stroke-dasharray="{STRICH[sz]}"' if STRICH[sz] else ""
        teile.append(f'<polyline points="{pts}" fill="none" stroke="{FARBEN[sz]}" stroke-width="2"{dash} '
                     f'stroke-linejoin="round" stroke-linecap="round"/>')
        letzte = ERG[sz][-1]
        labels.append([y(letzte[feld]), sz, letzte[feld]])
    # Beschriftungen am Ende, Abstand mindestens 14 px
    labels.sort()
    for i in range(1, len(labels)):
        if labels[i][0] - labels[i - 1][0] < 14:
            labels[i][0] = labels[i - 1][0] + 14
    for yy, sz, v in labels:
        teile.append(f'<circle cx="{x(1000):.1f}" cy="{y(v):.1f}" r="4" fill="{FARBEN[sz]}" stroke="#fff" stroke-width="2"/>')
        teile.append(f'<text x="{x(1000) + 8:.1f}" y="{yy + 4:.1f}" class="lab">{sz}: {fmt(v)}</text>')
    teile.append("</svg>")
    return "\n".join(teile)


def tabelle_mittel():
    kopf = ("<tr><th>Web&shy;sites</th><th>Seiten&shy;aufrufe pro Monat</th><th>Spitze Anfragen pro s</th>"
            "<th>Matomo-DB Wachstum 1. Jahr</th><th>Postgres Wachstum 1. Jahr</th><th>vCPU</th><th>RAM</th>"
            "<th>Archi&shy;vierung je Lauf</th><th>Crawler-Logs pro Monat (gepackt)</th>"
            "<th>KI-Abfragen pro Monat</th><th>KI-Kosten pro Monat</th><th>Sicherung</th>"
            "<th>Server-Vorschlag</th><th>Server + Sicherung pro Monat</th><th>je Website (Server)</th><th>Ampel</th></tr>")
    zeilen = []
    for z in ERG["mittel"]:
        archiv = f'{de(z["archiv_min"], 0 if z["archiv_min"] >= 10 else 1)} min'
        if z["archiv_parallel"] > 1:
            archiv += f' ({z["archiv_parallel"]} parallel)'
        zeilen.append(
            f'<tr class="{z["ampel"]}"><td class="n">{z["websites"]}</td><td class="n">{de(z["aufrufe_monat"])}</td>'
            f'<td class="n">{de(z["spitze_rps"], 1)}</td><td class="n">{gb(z["matomo_gb_jahr1"])}</td>'
            f'<td class="n">{gb(z["pg_gb_jahr1"])}</td><td class="n">{z["vcpu"]}</td><td class="n">{de(z["ram_gb"], 1)} GB</td>'
            f'<td class="n">{archiv}</td><td class="n">{gb(z["log_gb_gz_monat"])}</td>'
            f'<td class="n">{de(z["ki_abfragen_mvp"])}</td><td class="n">{de(z["ki_eur_mvp"])} €</td>'
            f'<td class="n">{gb(z["backup_gb"])}</td><td class="s">{z["server"]}</td>'
            f'<td class="n">{de(z["infra_eur"], 2)} €</td><td class="n">{de(z["infra_eur_je_website"], 2)} €</td>'
            f'<td>{ampel_span(z["ampel"])}</td></tr>')
    return f'<table class="gross"><thead>{kopf}</thead><tbody>{"".join(zeilen)}</tbody></table>'


def tabelle_kurz(sz):
    kopf = ("<tr><th>Websites</th><th>Seitenaufrufe pro Monat</th><th>Spitze Anfragen pro s</th>"
            "<th>Matomo-DB 1. Jahr</th><th>vCPU</th><th>RAM</th><th>Archivierung je Lauf</th>"
            "<th>Crawler-Logs pro Monat</th><th>Server-Vorschlag</th><th>Server + Sicherung</th>"
            "<th>je Website</th><th>Ampel</th></tr>")
    zeilen = []
    for z in ERG[sz]:
        archiv = f'{de(z["archiv_min"], 0 if z["archiv_min"] >= 10 else 1)} min'
        if z["archiv_parallel"] > 1:
            archiv += f' ({z["archiv_parallel"]}×)'
        if z["archiv_takt_h"] > 1:
            archiv += f', alle {z["archiv_takt_h"]} h'
        zeilen.append(
            f'<tr class="{z["ampel"]}"><td class="n">{z["websites"]}</td><td class="n">{de(z["aufrufe_monat"])}</td>'
            f'<td class="n">{de(z["spitze_rps"], 1)}</td><td class="n">{gb(z["matomo_gb_jahr1"])}</td>'
            f'<td class="n">{z["vcpu"]}</td><td class="n">{de(z["ram_gb"], 1)} GB</td><td class="n">{archiv}</td>'
            f'<td class="n">{gb(z["log_gb_gz_monat"])}</td><td class="s">{z["server"]}</td>'
            f'<td class="n">{de(z["infra_eur"], 2)} €</td><td class="n">{de(z["infra_eur_je_website"], 2)} €</td>'
            f'<td>{ampel_span(z["ampel"])}</td></tr>')
    return f'<table class="gross"><thead>{kopf}</thead><tbody>{"".join(zeilen)}</tbody></table>'


def html() -> str:
    S = SCHWELLEN
    m = {z["websites"]: z for z in ERG["mittel"]}
    hh = {z["websites"]: z for z in ERG["hoch"]}
    nn = {z["websites"]: z for z in ERG["niedrig"]}
    kw = KI_W
    jq = kw["je_abfrage_usd"]

    def ab(v):
        return f"ab {v} Websites" if v else "bis 1.000 Websites nie"

    ram_diag = diagramm("Bild 1a: Benötigter Arbeitsspeicher (RAM)", "ram_gb", "GB",
                        linien=[(GRUEN["ram_gb"] + 0.875, "Grenze neben Nextcloud (ca. 7 GB)"),
                                (EIN_SERVER["ram_gb"], "Grenze ein Server (16 GB)")],
                        fmt=lambda v: de(v, 0))
    cpu_diag = diagramm("Bild 1b: Benötigte Rechenkerne (vCPU)", "vcpu", "vCPU",
                        linien=[(GRUEN["vcpu"], "Grenze neben Nextcloud (3)"), (EIN_SERVER["vcpu"], "Grenze ein Server (8)")],
                        fmt=lambda v: de(v, 0), ymax=10, ref_links=True)
    kost_diag = diagramm("Bild 2a: Server + Sicherung pro Monat (Schätzung)", "infra_eur", "€/Monat",
                         fmt=lambda v: de(v, 0))
    jew_diag = diagramm("Bild 2b: Server-Kosten je Website pro Monat", "infra_eur_je_website", "€",
                        fmt=lambda v: de(v, 2))

    ist_ram = "".join(f"<tr><td>{a}</td><td class='n'>{de(b, 2)} GB</td></tr>" for a, b in IST["ram_grosse"])
    ist_disk = "".join(f"<tr><td>{a}</td><td class='n'>ca. {b} GB</td></tr>" for a, b in IST["disk_grosse"])

    schwellen_zeilen = ""
    for sz in SZENARIEN:
        s = S[sz]
        schwellen_zeilen += (
            f"<tr><td>{sz} ({de(SZENARIEN[sz])} Aufrufe je Website)</td>"
            f"<td>{'bis ' + str(s['gelb_ab'] - 25) + ' Websites' if s['gelb_ab'] and s['gelb_ab'] > 25 else ('bis 1.000' if not s['gelb_ab'] and not s['rot_ab'] else '–')}</td>"
            f"<td>{ab(s['gelb_ab'])}</td><td>{ab(s['rot_ab'])}</td><td>{ab(s['redis_ab'])}</td>"
            f"<td>{ab(s['parallel_archiv_ab'])}</td></tr>")

    def ki_zeile(k):
        d = KI[k]
        if "pauschal_usd" in d:
            detail = "Pauschale je Abfrage (Annahme aus der Spec, Preis nicht geprüft)"
        else:
            detail = (f"{de(d['ein_tok'])} Eingabe-Token × {de(d['ein_usd_mtok'], 2)} $ + {de(d['aus_tok'])} Ausgabe-Token × "
                      f"{de(d['aus_usd_mtok'], 2)} $ je 1 Mio." + (f"; {d['suchen']} Suche(n) × {de(d['suche_usd'] * 1000)} $ je 1.000" if d['suchen'] else ""))
        return (f"<tr><td>{d['name']}</td><td>{detail}</td><td class='n'>{de(jq[k] * 100, 2)} US-Cent</td>"
                f"<td>{'Preis geprüft 07.11.2026; Token-Menge geschätzt' if d['geprueft'] else 'ungeprüft – vor V2 prüfen'}</td></tr>")

    ki_tab = "".join(ki_zeile(k) for k in KI)

    m1000, h1000 = m[1000], hh[1000]
    budget_anteil = KI_BUDGET_EUR_JE_KUNDE / kw["eur_mvp"] * 100

    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Waybuild Analytics – Server-Auslastung 25 bis 1.000 Websites</title>
<style>
  @page {{ size: A4 landscape; margin: 13mm 14mm 15mm 14mm; }}
  :root {{ --t:#00a6a1; --td:#006b68; --hell:#e6f6f5; --text:#1d2b2b; --grau:#5d6b6b; --linie:#b9e3e1;
          --gruen:#1f8a4c; --gelb:#b07400; --rot:#c0392b; }}
  html, body {{ background:#fff; }}
  body {{ font-family:"DejaVu Sans","Liberation Sans",Arial,sans-serif; color:var(--text); font-size:10.5pt;
         line-height:1.7; margin:0; }}
  .text {{ max-width:none; }}
  h1 {{ font-size:20pt; line-height:1.3; color:var(--td); margin:0 0 6px; }}
  h2 {{ font-size:14pt; line-height:1.35; color:var(--td); margin:0 0 14px; border-bottom:2px solid var(--t); padding-bottom:4px; }}
  h3 {{ font-size:11.5pt; color:var(--td); margin:24px 0 10px; }}
  p {{ margin:0 0 20px; }}
  ul, ol {{ margin:0 0 20px; padding-left:22px; }} li {{ margin-bottom:8px; }}
  .meta {{ color:var(--grau); font-size:9.5pt; margin-bottom:22px; }}
  .kasten {{ border-left:5px solid var(--t); background:var(--hell); padding:14px 18px; margin:0 0 20px; }}
  .kasten p:last-child, .kasten ol:last-child {{ margin-bottom:0; }}
  .hinweis {{ border-left:5px solid #C9A227; background:#FFF8E1; padding:12px 16px; margin:0 0 20px; }}
  .seite {{ break-before:page; }}
  table {{ border-collapse:collapse; width:100%; margin:4px 0 20px; font-size:9pt; line-height:1.5; }}
  th, td {{ border-bottom:1px solid var(--linie); padding:5px 6px; text-align:left; vertical-align:top; }}
  th {{ background:var(--td); color:#fff; font-weight:bold; }}
  td.s {{ white-space:nowrap; }}
  td.n {{ text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }}
  table.gross {{ font-size:7.9pt; line-height:1.35; }}
  table.gross th {{ font-size:7.6pt; padding:5px 4px; vertical-align:bottom; }}
  table.gross td {{ padding:3.5px 4px; }}
  thead {{ display:table-header-group; }}
  tr {{ break-inside:avoid; }}
  tr.gruen td {{ background:#eaf6ee; }} tr.gelb td {{ background:#fdf4e1; }} tr.rot td {{ background:#fbe9e7; }}
  .amp {{ font-weight:bold; white-space:nowrap; }}
  .amp.gruen {{ color:var(--gruen); }} .amp.gelb {{ color:var(--gelb); }} .amp.rot {{ color:var(--rot); }}
  .zwei h3 {{ margin-top:4px; }}
  .zwei td {{ padding-top:3px; padding-bottom:3px; }}
  .zwei {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
  .klein {{ font-size:8.8pt; color:var(--grau); }}
  svg .dt {{ font-size:13px; font-weight:bold; fill:#006b68; }}
  svg .ax {{ font-size:10.5px; fill:#5d6b6b; }}
  svg .lab {{ font-size:10.5px; fill:#1d2b2b; font-weight:bold; }}
  svg .gl {{ stroke:#e3ecec; stroke-width:1; }}
  svg .ref {{ stroke:#9aa5a5; stroke-width:1; stroke-dasharray:4 3; }}
  svg .reft {{ font-size:10px; fill:#5d6b6b; }}
  .legende span {{ display:inline-block; margin-right:22px; }}
  .strich {{ display:inline-block; width:26px; height:0; border-top:3px solid; vertical-align:middle; margin-right:6px; }}
  a {{ color:var(--td); }}
  .quellen li {{ font-size:9pt; line-height:1.55; margin-bottom:6px; word-break:break-all; }}
</style>
</head>
<body>

<div class="text">
<h1>Waybuild Analytics – Server-Auslastung 25 bis 1.000 Websites</h1>
<p class="meta">Kapazitätsplanung · Stand {STAND} · Auftrag Can, Talk SW-0004 (#4889) · Weg B: Matomo 5.14.2 + MariaDB 11.4 + eigene App (SvelteKit/Node + Postgres) · Alle Zukunftswerte sind <b>Schätzungen</b></p>

<h2>Kurzfassung</h2>
<div class="kasten">
<ol>
<li>Bei normalem Verkehr (2.000 Seitenaufrufe je Website und Monat) reicht ein eigener Server für alle Stufen bis {S['mittel']['rot_ab'] - 25 if S['mittel']['rot_ab'] else '1.000'} Websites. Neben Nextcloud würde es technisch nur bis etwa {S['mittel']['gelb_ab'] - 25 if S['mittel']['gelb_ab'] else '1.000'} Websites passen. Laut Spec läuft der echte Betrieb aber sowieso auf einem eigenen Server.</li>
<li>Der Start-Server aus der Spec (4 vCPU, 8 GB) reicht bei normalem Verkehr bis etwa {erste('mittel', lambda z: z['ram_gb'] > 8 or z['vcpu'] > 4) - 25 if erste('mittel', lambda z: z['ram_gb'] > 8 or z['vcpu'] > 4) else 1000} Websites. Danach braucht es 8 vCPU und 16 GB.</li>
<li>{'Ab ' + str(S['mittel']['rot_ab']) + ' Websites' if S['mittel']['rot_ab'] else 'Erst über 1.000 Websites'} (normaler Verkehr) bzw. ab {S['hoch']['rot_ab']} Websites (hoher Verkehr, 10.000 Aufrufe) sollte die Datenbank auf einen eigenen Server. Der Grund ist der Arbeitsspeicher, den MariaDB für die wachsenden Matomo-Daten braucht.</li>
<li>Die Rechenlast steigt vor allem durch die stündliche Matomo-Archivierung. Ab {S['mittel']['parallel_archiv_ab']} Websites laufen dafür mehrere Prozesse gleichzeitig. Ab {S['mittel']['redis_ab'] or S['hoch']['redis_ab']} Websites ({'normal' if S['mittel']['redis_ab'] else 'hoch'}{', bei hohem Verkehr ab ' + str(S['hoch']['redis_ab']) if S['mittel']['redis_ab'] else ''}) empfehlen wir Redis mit Warteschlange für die Besuchsdaten.</li>
<li>Die Serverkosten bleiben klein: etwa {de(m[25]['infra_eur'], 0)} € im Monat bei 25 Websites und etwa {de(m1000['infra_eur'], 0)} € bei 1.000 Websites (normaler Verkehr). Pro Website sind das {de(m[25]['infra_eur_je_website'], 2)} € bzw. {de(m1000['infra_eur_je_website'], 2)} €.</li>
<li>Der größte Kostenblock ist der KI-Check: mit 30 Fragen × 3 Wiederholungen × 2 Anbietern etwa <b>{de(kw['eur_mvp'], 2)} € je Website und Monat</b>, ab V2 mit 4 Anbietern etwa {de(kw['eur_v2'], 2)} €. Das liegt über dem Budget von 10 € je Kunde. Der Budget-Wächter würde den Lauf bei etwa {de(budget_anteil, 0)} % der Abfragen stoppen.</li>
<li>Empfehlung: KI-Check vor dem Start günstiger einstellen (z. B. 1 statt 3 Wiederholungen oder ein kleineres Antwort-Modell), Server in Stufen wachsen lassen und die Datenbank erst bei Bedarf trennen.</li>
</ol>
</div>
<p class="klein">Ampel in diesem Dokument: <span class="amp gruen">● grün</span> = würde technisch neben Nextcloud passen · <span class="amp gelb">▲ gelb</span> = eigener Server nötig · <span class="amp rot">■ rot</span> = größerer Server bzw. getrennte Datenbank nötig. Farbe und Zeichen sagen dasselbe.</p>
</div>

<div class="seite text">
<h2>Ist-Zustand des Nextcloud-Servers (Messung am {STAND}, nur gelesen, nichts verändert)</h2>
<table>
<tr><th style="width:20%">Punkt</th><th>Messwert</th></tr>
<tr><td>Prozessor</td><td>{IST['cpu']}</td></tr>
<tr><td>Arbeitsspeicher (RAM)</td><td>{de(IST['ram_gb'], 1)} GB gesamt, davon {de(IST['ram_belegt_gb'], 0)} GB belegt, <b>{de(IST['ram_verfuegbar_gb'], 1)} GB verfügbar</b>, Auslagerung (Swap): {IST['swap']}</td></tr>
<tr><td>Festplatte</td><td>{IST['disk_gb']} GB, davon {IST['disk_belegt_gb']} GB belegt (63 %), <b>{IST['disk_frei_gb']} GB frei</b></td></tr>
<tr><td>Auslastung</td><td>{IST['last']}</td></tr>
<tr><td>Dienste</td><td>{IST['container']} Container, Laufzeit {IST['laufzeit']}</td></tr>
<tr><td>Spielraum neben Nextcloud</td><td>Der Server ist ruhig, aber der Arbeitsspeicher ist gut zur Hälfte belegt. Für eine neue Dauerlast setzen wir höchstens ca. 6–7 GB RAM, 3 vCPU und 50 GB Platte an (Festlegung für die Ampel). Der Rest bleibt Reserve für Nextcloud, Office und Sicherungen.</td></tr>
<tr><td>Demo Waybuild Analytics</td><td>4 Demo-Websites, {de(IST['demo_besuche'])} Besuche und {de(IST['demo_aktionen'])} Aktionen (Testdaten 07.10.–05.11.2026). Datenbank {de(IST['demo_db_mb'], 1)} MB, davon Rohdaten {de(IST['demo_rohdaten_mb'], 1)} MB und Berichts-Archive {de(IST['demo_archive_mb'], 1)} MB. Auf der Platte belegt der Datenbank-Ordner {IST['demo_db_platte_mb']} MB (meist feste Grundgröße von MariaDB). Ein stündlicher Archivierungs-Lauf dauert ca. {IST['demo_archiv_lauf_s']} Sekunden mit einem halben Prozessorkern.</td></tr>
</table>
<div class="zwei">
<div><h3>Wer braucht wie viel Arbeitsspeicher? (grob)</h3>
<table><tr><th>Dienst</th><th>RAM</th></tr>{ist_ram}</table></div>
<div><h3>Wer belegt wie viel Platte? (grob)</h3>
<table><tr><th>Bereich</th><th>Platte</th></tr>{ist_disk}</table></div>
</div>
</div>

<div class="seite text">
<h2>Annahmen</h2>
<p>Jede Zahl in diesem Abschnitt ist entweder gemessen (Demo), aus einer Quelle (siehe Quellen) oder eine <b>Annahme</b>. Alle Annahmen stehen im Rechenskript <code>docs/kapazitaet/rechnung.py</code> und lassen sich dort ändern.</p>
<table>
<tr><th style="width:17%">Bereich</th><th>Annahme</th><th style="width:19%">Herkunft</th></tr>
<tr><td>Verkehr je Website</td><td>niedrig {de(SZENARIEN['niedrig'])}, <b>mittel {de(SZENARIEN['mittel'])}</b>, hoch {de(SZENARIEN['hoch'])} Seitenaufrufe pro Monat. Je Aufruf 1,3 Matomo-Anfragen (Seite plus Klick- und Ziel-Ereignisse).</td><td>Annahme (typische KMU-Website)</td></tr>
<tr><td>Spitzenlast</td><td>In der Spitze kommen 10-mal so viele Anfragen pro Sekunde wie im Durchschnitt.</td><td>Annahme</td></tr>
<tr><td>Rohdaten Matomo</td><td>0,4 KB je Anfrage, aufbewahrt 6 Monate (danach gelöscht).</td><td>Messung Demo; Spec 4.8</td></tr>
<tr><td>Berichts-Archive Matomo</td><td>1,0 MB je Website und Monat plus 0,1 MB je 1.000 Seitenaufrufe, aufbewahrt 25 Monate. Viele kleine Websites brauchen dadurch mehr Platz als die Matomo-Faustregel. Gegenprobe Matomo: 1 GB je 5 Mio. Seitenaufrufe – für 1.000 Websites (mittel) wären das nur {gb(m1000['matomo_gb_regel'])} im Jahr. Wir rechnen bewusst vorsichtiger.</td><td>Schätzung aus Messung Demo; Quelle Matomo</td></tr>
<tr><td>Archivierung</td><td>Stündlich per Cron (wie Demo). Je Website und Lauf 4 Prozessor-Sekunden plus 2 Sekunden je 1.000 Anfragen des Tages. Ziel: Lauf nach 30 Minuten fertig, höchstens 3 Prozesse gleichzeitig.</td><td>Messung Demo; Quelle Matomo (2–3 parallel)</td></tr>
<tr><td>Postgres (eigene App)</td><td>Je KI-Antwort 6 KB (Text, Quellen, Auswertung), 25 Monate. Bot-Zeilen 0,5 KB, 90 Tage. Dazu 0,2 MB je Website und Monat für Kennzahlen und Logbuch.</td><td>Annahme; Spec 4.8</td></tr>
<tr><td>KI-Crawler-Logs</td><td>Hoster-Logs werden täglich gelesen und nur gestreamt, nicht gespeichert. 15 Logzeilen je Seitenaufruf (Seite, Bilder, CSS) plus Bot-Abrufe (niedrig 1.500 / mittel 3.000 / hoch 8.000 je Website und Monat), 250 Byte je Zeile, gepackt auf 10 %. Gespeichert werden nur Bot-Zeilen.</td><td>Annahme; Plan 1c</td></tr>
<tr><td>KI-Check</td><td>Je Website 30 Fragen × 3 Wiederholungen × Anbieter. MVP: Claude und ChatGPT = {kw['abfragen_mvp']} Abfragen je Website und Monat. V2: plus Gemini und Perplexity = {kw['abfragen_v2']}. Jede Antwort wertet Claude Haiku 5.5 aus. Budget 10 € je Kunde und Monat; wir rechnen mit 1 Website je Kunde. Kurs 1 $ = 0,90 €.</td><td>Plan 1d; Kurs: Annahme wie Plan 1d</td></tr>
<tr><td>Arbeitsspeicher</td><td>Grundbedarf je Dienst (System 0,7 GB, Matomo 0,5 GB, App 0,3 GB, Chromium für PDF 0,7 GB, Postgres 0,3 GB, Archiv-Prozess je 0,5 GB). MariaDB: 0,5 GB plus 30 % der Matomo-Datenbank als Zwischenspeicher. Postgres: plus 10 % seiner Daten. Auf alles 25 % Reserve. Gerechnet wird mit dem Dauerzustand nach 25 Monaten.</td><td>Annahme; Matomo-Speicherhinweis 512 MB je Archiv-Prozess</td></tr>
<tr><td>Rechenkerne</td><td>Grundlast 1 vCPU (App, Postgres, System). Dazu so viele Kerne, dass der Archiv-Lauf in 30 Minuten fertig ist (mindestens 0,5), mal 1,5 für die Datenbank. 0,03 vCPU je Anfrage pro Sekunde in der Spitze. 25 % Reserve, mindestens 2 vCPU.</td><td>Annahme</td></tr>
<tr><td>Platte</td><td>20 GB System, Datenbanken × 1,5 (Platz für Dump und Wachstum), 10 GB für Logs und Zwischendateien.</td><td>Annahme</td></tr>
<tr><td>Sicherung</td><td>Nächtlich, gepackt, 7 tägliche, 4 wöchentliche, 6 monatliche Stände (restic). Belegter Platz etwa 0,9 × Datenbanken.</td><td>Spec 5.5; Faktor Annahme</td></tr>
<tr><td>Serverpreise</td><td>Hetzner Cloud, Standort Deutschland, netto, Preise der Website am 07.11.2026. Shared-vCPU-Server „Regular Performance“ (CPX) für einen Server; für eine getrennte Datenbank „General Purpose“ (CCX, eigene Kerne). Sicherung auf einer Storage Box. Die Website zeigte bei CPX „zurzeit nicht verfügbar“ – <b>Verfügbarkeit und Preis vor einer Bestellung prüfen</b>. IPv4-Adresse und Steuer sind nicht enthalten.</td><td>Quelle Hetzner (Website)</td></tr>
</table>

<h3>Kosten je KI-Abfrage</h3>
<table><tr><th style="width:24%">Anbieter</th><th>Rechnung</th><th style="width:12%">je Abfrage</th><th style="width:20%">Stand</th></tr>{ki_tab}</table>
<p class="klein">Preise Anthropic und OpenAI am 07.11.2026 auf den offiziellen Preisseiten geprüft. Wie viele Token und Suchen eine Antwort wirklich braucht, ist geschätzt und muss im ersten Probelauf gemessen werden. Das ChatGPT-Modell ist im Plan noch offen; wir haben gpt-5.6-terra angenommen.</p>
</div>

<div class="seite">
<h2>Alle 40 Stufen – normaler Verkehr (mittel, 2.000 Seitenaufrufe je Website und Monat)</h2>
<p class="klein">Datenbank-Werte: Wachstum im 1. Jahr. RAM und Platte sind für den Dauerzustand nach 25 Monaten bemessen. KI-Kosten ohne Budget-Deckel (MVP, 2 Anbieter). Server + Sicherung: Hetzner-Preise netto. Alles Schätzungen.</p>
{tabelle_mittel()}
</div>

<div class="seite">
<h2>Alle 40 Stufen – hoher Verkehr (10.000 Seitenaufrufe je Website und Monat)</h2>
<p class="klein">KI-Abfragen und KI-Kosten hängen nicht vom Verkehr ab und sind wie in der Tabelle „mittel“. „alle 2 h“ bedeutet: Die Archivierung sollte nur noch alle 2 Stunden laufen, sonst wird sie nicht rechtzeitig fertig.</p>
{tabelle_kurz('hoch')}
</div>

<div class="seite text">
<h2>Wo liegen die Schwellen? (alle drei Szenarien)</h2>
<table>
<tr><th>Szenario</th><th>Neben Nextcloud möglich (grün)</th><th>Eigener Server nötig (gelb)</th><th>Getrennte Datenbank nötig (rot)</th><th>Redis + Warteschlange</th><th>Mehrere Archiv-Prozesse</th></tr>
{schwellen_zeilen}
</table>
<p>Bei niedrigem Verkehr (1.000 Aufrufe) sieht es fast so aus wie bei „mittel“. Der Verkehr spielt bei kleinen Websites eine kleinere Rolle als die Anzahl der Websites, weil Matomo für jede Website eigene Berichte rechnet und speichert.</p>
<p>Zum Vergleich mit Matomo: Matomo empfiehlt ab etwa 1–5 Mio. Anfragen im Monat einen eigenen Datenbank-Server. Bei 1.000 Websites sind es bei „mittel“ {de(m1000['treffer_monat'] / 1e6, 1)} Mio., bei „hoch“ {de(h1000['treffer_monat'] / 1e6, 1)} Mio. Anfragen im Monat.</p>
<p class="klein">Bei 1.000 Websites (mittel) setzt sich der RAM-Bedarf so zusammen: {', '.join(f'{k} {de(v, 1)} GB' for k, v in m1000['ram_teile'].items() if v)}.</p>
</div>

<div class="seite">
<h2>Diagramme</h2>
<p class="legende klein"><span><i class="strich" style="border-color:{FARBEN['niedrig']};border-top-style:dashed"></i>niedrig (1.000 Aufrufe)</span><span><i class="strich" style="border-color:{FARBEN['mittel']}"></i>mittel (2.000 Aufrufe)</span><span><i class="strich" style="border-color:{FARBEN['hoch']};border-top-style:dotted"></i>hoch (10.000 Aufrufe)</span> · gestrichelte graue Linien = Grenzen</p>
<div class="zwei"><div>{ram_diag}</div><div>{cpu_diag}</div></div>
<div class="zwei"><div>{kost_diag}</div><div>{jew_diag}</div></div>
<p class="klein">Bild 2 zeigt nur Server und Sicherung. Die KI-Kosten wachsen gleichmäßig mit: etwa {de(kw['eur_mvp'], 2)} € je Website (MVP), also {de(m[100]['ki_eur_mvp'], 0)} € bei 100 und {de(m1000['ki_eur_mvp'], 0)} € bei 1.000 Websites. Sie stehen nicht im selben Bild, weil sie etwa 50-mal größer sind und die Serverkurve sonst flach aussähe. Die Zahlen stehen in den Tabellen.</p>
</div>

<div class="seite text">
<h2>Empfehlung und Stufenplan (normaler Verkehr)</h2>
<table>
<tr><th style="width:18%">Ab</th><th>Schritt</th><th style="width:22%">Grund</th></tr>
<tr><td>Start (bis ca. {erste('mittel', lambda z: z['ram_gb'] > 8 or z['vcpu'] > 4) - 25} Websites)</td><td>Eigener Server mit 4 vCPU und 8 GB (wie Spec, z. B. Hetzner CPX32, ca. {de(SERVER_GETEILT[1][4], 2)} € netto). Alles auf einem Server: Matomo, MariaDB, App, Postgres, Warteschlange für Jobs in Postgres (pg-boss, schon im Plan). Archivierung stündlich. Sicherung auf Storage Box (ca. 3,20 €).</td><td>Vorgabe V3 (getrennt von Nextcloud). Neben Nextcloud ginge es technisch nur bis ca. {S['mittel']['gelb_ab'] - 25} Websites.</td></tr>
<tr><td>{erste('mittel', lambda z: z['ram_gb'] > 8 or z['vcpu'] > 4)} Websites</td><td>Auf 8 vCPU und 16 GB vergrößern (z. B. CPX42, ca. {de(SERVER_GETEILT[2][4], 2)} €). Cloud-Server lassen sich meist nachträglich vergrößern (beim Anbieter prüfen).</td><td>MariaDB braucht mehr Zwischenspeicher, Archivierung braucht mehr Kerne.</td></tr>
<tr><td>{S['mittel']['redis_ab'] or S['hoch']['redis_ab']} Websites{'' if S['mittel']['redis_ab'] else ' (nur hoher Verkehr)'}</td><td>Redis plus das kostenlose Matomo-Plugin QueuedTracking. Besuchsdaten gehen erst in eine Warteschlange und dann in die Datenbank.</td><td>Ab ca. 1 Mio. Anfragen im Monat; schützt bei Lastspitzen (Matomo Tier 2).</td></tr>
<tr><td>{S['mittel']['parallel_archiv_ab']} Websites</td><td>Archivierung mit 2–3 parallelen Prozessen. Monatsberichte (PDF) mit 2 Prozessen erzeugen, damit sie bis 08:00 fertig sind ({de(m[1000]['pdf_min'], 0)} Minuten bei 1.000 Websites mit einem Prozess). KI-Check über mehrere Tage verteilen statt alles am 25.</td><td>Laufzeit; bei 1.000 Websites sind es {de(m1000['ki_abfragen_mvp'])} KI-Abfragen im Monat.</td></tr>
<tr><td>{S['mittel']['rot_ab'] or 'über 1.000'} Websites (hoch: {S['hoch']['rot_ab']})</td><td>Datenbank auf einen eigenen Server mit eigenen Kernen (z. B. CCX23/CCX33) und App-Server daneben. Archivierung bei Bedarf alle 2–3 Stunden statt stündlich.</td><td>RAM über 16 GB; Matomo empfiehlt ab 1–5 Mio. Anfragen eine eigene Datenbank.</td></tr>
<tr><td>sofort, vor dem Start</td><td>KI-Check-Kosten senken: z. B. 1 Wiederholung statt 3 (dann ca. {de(kw['eur_mvp'] / 3, 2)} € je Website) oder Claude Sonnet 5.5 statt Opus 5.5 als Antwort-Modell. Danach einen echten Probelauf mit 2 Fragen machen und Token, Suchen und Dauer messen.</td><td>{de(kw['eur_mvp'], 2)} € je Website liegt über dem Budget von 10 € je Kunde.</td></tr>
<tr><td>laufend</td><td>Überwachung (RAM, Platte, Dauer der Archivierung) mit Warnung im Talk. Diese Rechnung mit echten Messwerten nach 25 Websites neu laufen lassen.</td><td>Viele Werte sind Schätzungen.</td></tr>
</table>

</div>

<div class="seite text">
<h2>Kosten pro Website und Monat (normaler Verkehr, netto, Schätzung)</h2>
<table>
<tr><th>Websites</th><th>Server + Sicherung gesamt</th><th>Server je Website</th><th>KI-Check je Website ohne Deckel</th><th>KI-Check je Website mit Budget-Deckel 10 €</th><th>Gesamt je Website (mit Deckel)</th></tr>
{''.join(f"<tr><td class='n'>{n}</td><td class='n'>{de(m[n]['infra_eur'], 2)} €</td><td class='n'>{de(m[n]['infra_eur_je_website'], 2)} €</td><td class='n'>{de(m[n]['ki_eur_mvp'] / n, 2)} €</td><td class='n'>{de(m[n]['ki_eur_mit_budget'] / n, 2)} €</td><td class='n'><b>{de(m[n]['gesamt_eur_je_website'], 2)} €</b></td></tr>" for n in (25, 50, 100, 150, 200, 250, 400, 500, 600, 750, 1000))}
</table>
<p>Die Server werden pro Website schnell billig: Ab {erste('mittel', lambda z: z['infra_eur_je_website'] < 1)} Websites liegen sie unter 1 € je Website und Monat, ab {erste('mittel', lambda z: z['infra_eur_je_website'] < 0.25)} Websites unter 0,25 €. Fast die ganzen laufenden Kosten pro Website sind der KI-Check. Ohne Budget-Deckel wären es {de(kw['eur_mvp'], 2)} € (MVP) bzw. {de(kw['eur_v2'], 2)} € (V2) je Website. Nicht enthalten: Arbeitszeit, Domain, Steuer, Google-Search-Console (kostenlos) und eine IPv4-Adresse.</p>
</div>

<div class="seite text">
<h2>Quellen (abgerufen am 07.11.2026)</h2>
<ol class="quellen">
<li>Matomo – Server-Anforderungen (Größen je Verkehr: bis 1 Mio. Aufrufe 4 CPU / 8 GB / 250 GB; bis 10 Mio. zwei Server): https://matomo.org/faq/on-premise/matomo-requirements/</li>
<li>Matomo – How to configure Matomo for speed (ca. 1 GB Datenbank je 5 Mio. Seitenaufrufe; Rohdaten älter als 6 Monate löschen; innodb_buffer_pool_size): https://matomo.org/faq/on-premise/how-to-configure-matomo-for-speed/</li>
<li>Matomo – Archivierung per Cron (stündlich, Browser-Archivierung aus, memory_limit 512 MB als Start, parallele Archiv-Prozesse): https://matomo.org/faq/on-premise/how-to-set-up-auto-archiving-of-your-reports/</li>
<li>Matomo – Running Matomo in High-Traffic Environments (Tier 1 unter 1 Mio. Anfragen ein Server; Tier 2 1–10 Mio. eigene Datenbank, Redis bei QueuedTracking; mehr als 2–3 parallele Archiv-Prozesse bringen wenig): https://matomo.org/faq/on-premise/running-matomo-in-high-traffic-environments/</li>
<li>Matomo – QueuedTracking-Plugin: https://matomo.org/faq/on-premise/how-to-use-the-queuedtracking-plugin/</li>
<li>Anthropic – Preise (Opus 5.5: 4 $ / 20 $, Haiku 5.5: 0,10 $ / 0,50 $ je 1 Mio. Token; Websuche 10 $ je 1.000 Suchen): https://platform.claude.com/docs/en/about-claude/pricing</li>
<li>OpenAI – API-Preise (web_search 10 $ je 1.000 Aufrufe; gpt-5.6-terra 2 $ / 12 $ je 1 Mio. Token): https://developers.openai.com/api/docs/pricing</li>
<li>Hetzner Cloud – Regular Performance (CPX22 19,99 €, CPX32 35,99 €, CPX42 69,99 €, CPX52 100,99 €, CPX62 130,49 €): https://www.hetzner.com/cloud/regular-performance/</li>
<li>Hetzner Cloud – General Purpose (CCX13 43,49 €, CCX23 86,49 €, CCX33 138,99 €, CCX43 276,49 €): https://www.hetzner.com/cloud/general-purpose/</li>
<li>Hetzner Storage Box (BX11 1 TB 3,20 €, BX21 5 TB 10,90 €): https://www.hetzner.com/storage/storage-box/</li>
<li>Northflank – Bericht zur Preiserhöhung bei Hetzner Cloud 2026 (Sekundärquelle): https://northflank.com/blog/hetzner-cloud-server-price-increases</li>
<li>Gemini und Perplexity: Preise <b>nicht</b> geprüft, Annahmen aus der Spec (Abschnitt 4.6, Sekundärquellen). Vor V2 prüfen.</li>
<li>Eigene Unterlagen: Spec docs/superpowers/specs/2026-11-06-waybuild-analytics-design.md (4.6, 4.8, 5.4, 5.5), Plan 1c und 1d; Messung Demo /opt/waybuild-analytics-demo am 07.11.2026.</li>
</ol>
<div class="hinweis"><p><b>Hinweis zu den Serverpreisen:</b> Die Spec nennt für 4 vCPU / 8 GB „etwa 10–20 € netto“. Laut Fachberichten hat Hetzner die Cloud-Preise 2026 deutlich erhöht. Die Hetzner-Website nennt für CPX32 (4 vCPU, 8 GB) jetzt 35,99 € netto. Am 07.11.2026 standen die Reihen CX und CPX dort mit dem Hinweis „zurzeit nicht verfügbar“. Vor der Bestellung Preis und Verfügbarkeit prüfen, eventuell auch andere deutsche Anbieter vergleichen.</p></div>
<p class="klein">Rechenskript und HTML-Quelle: Repo waybuild_analytic, Ordner docs/kapazitaet/ (rechnung.py, kapazitaet.html, ergebnis.json, ergebnis.csv). Neu rechnen: <code>python3 docs/kapazitaet/rechnung.py</code>.</p>
</div>

</body>
</html>
"""


if __name__ == "__main__":
    schreibe_daten()
    (HIER / "kapazitaet.html").write_text(html(), encoding="utf-8")
    for sz in SZENARIEN:
        print(sz, SCHWELLEN[sz])
    print("KI je Website:", {k: round(v, 2) for k, v in KI_W.items() if not isinstance(v, dict)})
    for n in (25, 100, 250, 500, 1000):
        z = next(z for z in ERG["mittel"] if z["websites"] == n)
        print(n, z["vcpu"], round(z["ram_gb"], 1), z["server"], round(z["infra_eur"], 2), round(z["archiv_min"], 1), z["ampel"])
