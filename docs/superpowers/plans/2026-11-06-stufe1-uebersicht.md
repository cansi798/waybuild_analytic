# Waybuild Analytics – Stufe 1 (MVP) Übersicht der Teilpläne

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Das MVP aus der Spec (Abschnitt 4.0, Spalte „MVP“) in vier nacheinander gebauten Teilplänen umsetzen.

**Architecture:** Weg B (von Can am 06.11.2026, 22:58, Talk #4860 freigegeben: „Weg B entwickeln.“): Matomo 5.14.2 läuft unverändert als Datensammler. Daneben läuft die eigene App „Waybuild Analytics“ (SvelteKit, Node 22, Postgres 16), die nur über die Matomo-Reporting-API und die Tracking-API mit Matomo spricht.

**Tech Stack:** Node 22, SvelteKit 2 + Svelte 5 + TypeScript, `postgres` (porsager), Postgres 16 mit Row-Level-Security, Vitest, Playwright 1.48.2, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-11-06-waybuild-analytics-design.md`

## Teilpläne und Reihenfolge

| Teil | Datei | Inhalt | Was man danach sieht | Grobe Dauer |
|---|---|---|---|---|
| 1a | `2026-11-06-stufe1a-fundament.md` | Entwicklungsumgebung, Datenbank mit Kundentrennung, Kunden und Websites, Matomo-Anbindung, Ziele, Team-Anmeldung, Vorschau, Installationspaket | Anmelden unter https://wa-app.169-58-147-249.sslip.io, Kunden und Websites anlegen, Tracking-Code pro Website ansehen | 8–10 Arbeitstage |
| 1b | `2026-11-06-stufe1b-berichte.md` | Kennzahlen-Baustein, Maßnahmen-Logbuch mit Vorher-nachher, Exporte, Monatsbericht als PDF mit Freigabe, Zeitpläne, Störungsmeldungen | Zahlen der Demo-Websites, Logbuch-Eintrag mit Vergleich, Export herunterladen, Monats-PDF als Entwurf ansehen und freigeben | 8–10 Arbeitstage |
| 1c | `2026-11-06-stufe1c-ki-crawler-begriffe.md` | KI-Bot-Liste, Log-Import mit IP-Prüfung, Crawler-Auswertung, robots.txt-Abgleich, KI-Referrer-Regeln, Google Search Console | Log-Datei hochladen und sehen, welche KI-Bots welche Seiten lesen; KI-Besuche im Kanal; Suchbegriffe im Bericht | 8–10 Arbeitstage |
| 1d | `2026-11-06-stufe1d-ki-check-mcp.md` | Test-Fragen pro Kunde, AI-Visibility-Check mit Claude und ChatGPT, Budget-Wächter, MCP-Server mit Token pro Kunde | Monatlicher KI-Check mit Tabelle „genannt ja/nein, Begriffe“; Claude Code liest die Zahlen per MCP | 10–12 Arbeitstage |

Jeder Teilplan baut auf dem vorherigen auf und endet mit lauffähiger, getesteter Software. Gesamt grob 35–45 Arbeitstage (KI-gestützt), wie in der Spec geschätzt.

## Standard-Entscheidungen (Standard, änderbar)

Can hat die offenen Entscheidungen D1–D12 nicht einzeln beantwortet. Bis er oder Jamil etwas anderes sagt, gelten die Empfehlungen aus der Spec:

| Nr. | Standard, änderbar |
|---|---|
| D1 | Arbeitstitel „Waybuild Analytics“. Im Code nur an einer Stelle (`src/lib/marke.ts`, `PRODUKTNAME`), damit eine Umbenennung leicht ist. |
| D2 | Weg B (freigegeben). |
| D3 | MVP-Umfang wie Spec 4.0. Pilot: Demo-Websites aus Matomo (IDs 1–4), danach Bauwelt. |
| D4 | Entwicklung und Test auf diesem Server neben der Demo. Produktion später auf einem eigenen Server in Deutschland (4 vCPU / 8 GB / 160 GB), Subdomains auf waybuild-software.de, über das Installationspaket. |
| D5 | KI-Check im MVP mit Claude und ChatGPT; Budget 10 € netto pro Kunde und Monat; Can legt die API-Konten an; Schlüssel nur auf dem Server. |
| D6 | Tracking-Modus „Standard“ (cookieless JS). „Streng“ (nur serverseitig) ist laut Spec 4.0 erst V2; in Stufe 1 nur als Einstellung vorbereitet: die Website zeigt dann keinen Browser-Code. |
| D7 | Crawler-Messung nur für Websites mit Log-Zugang oder manuellem Log-Upload; GitHub Pages hat keine. |
| D8 | Kein Cloudflare im MVP. |
| D9 | Anwaltliche Prüfung vor dem ersten Kundenbericht. Bis dahin kein Einbau in Live-Websites ohne Cans „ja“. |
| D10 | Rechteübertragung Can und Jamil auf die UG schriftlich (außerhalb dieses Plans). |
| D11 | Geschäftsmodell offen; die Software hängt davon nicht ab. |
| D12 | robots.txt bleibt bei Jamil und Can; die App zeigt nur an. |

## Gemeinsame Umgebung (gilt für alle Teilpläne)

- Repo auf dem Host: `/home/can/projekte/waybuild_analytic`. Dateien dort direkt bearbeiten, git auf dem Host.
- Entwicklungs-Container `wa-dev` (aus Plan 1a, Task 1), Repo eingebunden als `/work/wa`. **Alle** npm- und Test-Befehle laufen im Container: `sudo -n docker exec wa-dev sh -lc 'cd /work/wa && …'`. Nie `npm` direkt auf dem Host.
- Matomo: die vorhandene Demo (`/opt/waybuild-analytics-demo`, Matomo 5.14.2), intern erreichbar als `http://wa-matomo` im Docker-Netz `waybuild-analytics-demo_wa-aussen`. An der Demo selbst wird nichts geändert, außer dem in 1a Task 4 beschriebenen Lese-Benutzer.
- Vorschau: https://wa-app.169-58-147-249.sslip.io über den Nextcloud-Caddy (1a Task 7).
- Geheimnisse nur in `/opt/wa-dev/.env` (root, chmod 600). Nie im Repo, nie im Chat.
- Commits: Autor „Can Siebert“ (repo-lokal eingestellt), Trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Nach jedem Teilplan: Gesamt-Review des Branches, Screenshots nach Nextcloud `Projekte/waybuild/Waybuild Analytics`, eine kurze Meldung in Talk 63yitbs3 mit Vorschau-Link. Merge nach `main` nur nach Cans „ja“.
- Branches: `stufe-1a`, `stufe-1b`, `stufe-1c`, `stufe-1d`, jeweils vom vorherigen abgezweigt.

## Ausführung

Wartet auf die Freigabe des Plans und auf die Wahl der Ausführungsart durch Can (Talk 63yitbs3):

- **Subagent-driven** (Empfehlung): Für jede Aufgabe ein frischer Umsetzer und danach ein frischer Prüfer, am Ende eine Gesamtprüfung. Die Teilpläne hängen über gemeinsame Schnittstellen eng zusammen (Kundentrennung, Kennzahlen-Baustein, Token), und ein Fehler bei der Kundentrennung wäre teuer.
- **Native**: Ein Agent setzt alle Aufgaben selbst um, eine Gesamtprüfung am Ende. Schneller und günstiger, aber ohne Prüfung nach jeder Aufgabe.

Vor dieser Freigabe wird nicht programmiert.
