# Waybuild Analytics – Stufe 1b „Kennzahlen und Berichte“ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kennzahlen aus Matomo, Maßnahmen-Logbuch mit Vorher-nachher, Exporte (CSV/XLSX/JSON), Monatsbericht als PDF mit Entwurf und Freigabe, Zeitpläne und Störungsmeldungen.

**Architecture:** Ein Kennzahlen-Baustein (`src/lib/server/kennzahlen/`) ist der einzige Ort für Rechenwege; Bericht, Export und später MCP nutzen ihn. PDFs entstehen aus einer HTML-Vorlage mit Chromium (Playwright). Zeitpläne laufen über eine Job-Warteschlange in Postgres.

**Tech Stack:** wie 1a, dazu `playwright-core` 1.48.2 + Chromium, `exceljs`, `pg-boss` (exakte Version beim Installieren fest eintragen).

**Spec:** `docs/superpowers/specs/2026-11-06-waybuild-analytics-design.md` (4.2, 4.3, 5.3, 5.6) und `docs/superpowers/plans/2026-11-06-stufe1-uebersicht.md`.

## Global Constraints

- Alle Global Constraints aus Plan 1a gelten.
- Berichte werden nie automatisch an Kunden geschickt. Ablage in Nextcloud erst bei „freigegeben“.
- Monatsbericht für den Vormonat: Job am 2. Kalendertag um 06:00 Europe/Berlin; spätestens 08:00 fertig.
- Vorher-nachher: Fenster 28 Tage vor (Tag −28 bis −1) und 28 Tage nach (Tag +1 bis +28) dem Maßnahmen-Datum; der Tag selbst zählt nicht.
- Unter 100 Besuchen in einem der beiden Fenster: Hinweis „zu wenig Daten für eine sichere Aussage“.
- „Eindeutige Besucher“ erscheinen nur mit der Fußnote „Schätzung: ohne Cookies erkennt die Messung wiederkehrende Besucher nur innerhalb eines Tages.“
- JSON-Exporte tragen `"schema": "wa.kennzahlen.v1"`.
- CSV: Trennzeichen `;`, UTF-8 mit BOM, Dezimalkomma, Datum `TT.MM.JJJJ` (für deutsches Excel).

## Review Focus

1. Monatsgrenzen und Zeitumstellung (letzter Sonntag im Oktober/März): Oktober hat 31 volle Tage in Europe/Berlin, keine Lücke, keine Doppelung – Test in Task 1.
2. Website ohne Besuche: Konversionsrate `null`, im Bericht „–“, nie `NaN` oder „Infinity“ – Test in Task 2.
3. Seitentitel mit `;`, `"`, Zeilenumbruch, Umlauten und `=` am Anfang im CSV/XLSX: korrekt maskiert, keine Formel-Ausführung in Excel – Test in Task 4.
4. Bericht für einen Monat neu erzeugen, der schon freigegeben ist: der freigegebene bleibt unverändert, Meldung „Dieser Bericht ist schon freigegeben.“ – Test in Task 6.
5. Maßnahme liegt weniger als 28 Tage zurück oder in der Zukunft: Status „läuft noch, X Tage“ statt einer Zahl – Test in Task 3.

---

## File Structure

```
src/lib/server/zeit.ts                        # Zeiträume Europe/Berlin
src/lib/server/kennzahlen/typen.ts            # Kennzahlen, Kanal, Vergleich
src/lib/server/kennzahlen/matomo-kennzahlen.ts# holeKennzahlen
src/lib/server/kennzahlen/vergleich.ts        # vergleiche
src/lib/server/logbuch.ts                     # Maßnahmen + vorherNachher
src/lib/server/export/{csv,xlsx,json}.ts
src/lib/server/bericht/{daten,vorlage,pdf,ablauf,nextcloud}.ts
src/lib/server/jobs/{warteschlange,zeitplan,stoerung}.ts
db/migrations/004_logbuch.sql, 005_berichte.sql, 006_jobs.sql
src/routes/(team)/websites/[id]/{kennzahlen,logbuch,export,berichte}/…
tests/fixtures/matomo/*.json                  # aufgezeichnete Matomo-Antworten
```

---

### Task 1: Zeiträume

**Files:**
- Create: `src/lib/server/zeit.ts`, `tests/unit/zeit.test.ts`

**Interfaces:**
- Produces: `type Zeitraum = { von: string; bis: string }` (ISO-Datum `YYYY-MM-DD`, beide inklusive); `monatsZeitraum(monat: string): Zeitraum` (`'2026-10'` → `{von:'2026-10-01', bis:'2026-10-31'}`); `vormonat(heute: Date): string`; `fensterVorNach(datum: string): { vor: Zeitraum; nach: Zeitraum }`; `tageZwischen(a: string, b: string): number`; `heuteBerlin(jetzt?: Date): string`.

- [ ] **Step 1: Failing tests:** `monatsZeitraum('2026-10').bis === '2026-10-31'`; `monatsZeitraum('2028-02').bis === '2028-02-29'`; `vormonat(new Date('2026-11-02T05:30:00Z')) === '2026-10'`; `heuteBerlin(new Date('2026-10-31T23:30:00Z')) === '2026-11-01'`; `fensterVorNach('2026-10-15')` → vor `2026-09-17…2026-10-14`, nach `2026-10-16…2026-11-12`; `tageZwischen('2026-10-24','2026-10-26') === 2` (über die Zeitumstellung).
- [ ] **Step 2:** FAIL → **Step 3:** implementieren (ohne Zeitzonen-Bibliothek: `Intl.DateTimeFormat` mit `timeZone: 'Europe/Berlin'`) → **Step 4:** PASS.
- [ ] **Step 5: Commit** „feat: Zeiträume“.

### Task 2: Kennzahlen-Baustein

**Files:**
- Create: `src/lib/server/kennzahlen/typen.ts`, `matomo-kennzahlen.ts`, `vergleich.ts`, `tests/fixtures/matomo/*.json`, `tests/unit/kennzahlen.test.ts`, `tests/matomo/kennzahlen-vertrag.test.ts`, `scripts/fixtures-aufnehmen.ts`

**Interfaces:**
- Consumes: `matomoApi` (1a Task 4), `holeWebsite`, `ZIELE`, `app.ziele` (1a), `Zeitraum` (Task 1).
- Produces:
  - `type Kanal = 'suche' | 'direkt' | 'social' | 'verweis' | 'kampagne' | 'ki'`.
  - `type Kennzahlen = { websiteId: string; zeitraum: Zeitraum; besuche: number; eindeutigeBesucherSchaetzung: number; seitenaufrufe: number; durchschnittDauerSek: number; kanaele: Record<Kanal, number>; topSeiten: { url: string; titel: string; aufrufe: number }[]; einstiegsseiten: { url: string; besuche: number }[]; geraete: { handy: number; tablet: number; pc: number; sonstige: number }; regionen: { name: string; besuche: number }[]; ziele: Record<ZielSchluessel, number>; konversionsrate: number | null; ladezeitMs: number | null; vollstaendig: boolean; fehlendeTage: string[] }`.
  - `holeKennzahlen(sql: TransactionSql, websiteId: string, zeitraum: Zeitraum): Promise<Kennzahlen>` – Matomo-Methoden: `VisitsSummary.get`, `Referrers.getReferrerType`, `Actions.getPageUrls` (flat, Top 10), `Actions.getEntryPageUrls` (flat, Top 10), `DevicesDetection.getType`, `UserCountry.getRegion` (Top 10; ohne GeoIP-Datenbank nur grob), `Goals.get` je `matomo_goal_id`, `PagePerformance.get`. Zuordnung `referrerType`: `search`→suche, `direct`→direkt, `social`→social, `website`→verweis, `campaign`→kampagne, `ai`→ki. `vollstaendig=false`, wenn `VisitsSummary.get` mit `period=day` für einen Tag einen Fehler liefert (Tag in `fehlendeTage`).
  - `konversionsrate = Summe(ziele) / besuche`, bei `besuche === 0` → `null`.
  - `type Vergleich = { a: Kennzahlen; b: Kennzahlen; delta: { besuche: number | null; ziele: number | null; konversionsrate: number | null; ki: number | null }; zuWenigDaten: boolean }`; `vergleiche(a, b): Vergleich` – Delta relativ in Prozent (`(b-a)/a*100`, bei `a === 0` → `null`); `zuWenigDaten = a.besuche < 100 || b.besuche < 100`.
- [ ] **Step 1:** `scripts/fixtures-aufnehmen.ts` nimmt die Antworten der Demo-Site 2 für `2026-10-07…2026-11-05` auf und speichert sie unter `tests/fixtures/matomo/` (ohne Token).
- [ ] **Step 2: Failing tests** `tests/unit/kennzahlen.test.ts` (fetch liefert Fixtures): `besuche` = Wert aus `VisitsSummary.get`; Summe der `kanaele` = `besuche`; `kanaele.ki > 0` (Demo enthält KI-Besuche); Website mit 0 Besuchen → `konversionsrate === null`; `vergleiche` mit a.besuche 0 → `delta.besuche === null`; a.besuche 99 → `zuWenigDaten === true`. `tests/matomo/kennzahlen-vertrag.test.ts`: echte Demo-Antworten haben die Felder, die der Baustein liest (`nb_visits`, `nb_actions`, `avg_time_on_site`, `label`, `nb_conversions`).
- [ ] **Step 3:** FAIL → implementieren → `npm test && npm run test:matomo` PASS.
- [ ] **Step 4:** Seite `(team)/websites/[id]/kennzahlen` zeigt Monat wählbar, Kacheln Besuche/Ziele/Konversionsrate, Kanäle, Top-Seiten; Fußnote für Besucher-Schätzung.
- [ ] **Step 5: Commit** „feat: Kennzahlen-Baustein“.

### Task 3: Maßnahmen-Logbuch und Vorher-nachher

**Files:**
- Create: `db/migrations/004_logbuch.sql`, `src/lib/server/logbuch.ts`, `src/routes/(team)/websites/[id]/logbuch/…`, `tests/db/logbuch.test.ts`

**Interfaces:**
- Consumes: `holeKennzahlen`, `vergleiche`, `fensterVorNach`, `heuteBerlin`.
- Produces:
  - Tabelle `app.massnahmen(id uuid pk, kunde_id uuid not null, website_id uuid not null, datum date not null, titel text not null, kategorie text check in ('text','design','technik','seo','ki_geo'), erwartete_wirkung text, kennzahl text check in ('besuche','ziele','konversionsrate','ki_besuche','ki_crawler'), angelegt_von uuid, angelegt_am timestamptz default now())`, RLS über `kunde_id`.
  - `legeMassnahmeAn(sql, daten): Promise<Massnahme>`, `listeMassnahmen(sql, websiteId): Promise<Massnahme[]>`.
  - `type VorherNachher = { status: 'fertig'; vergleich: Vergleich } | { status: 'laeuft'; restTage: number }`; `vorherNachher(sql, massnahmeId, heute?: string): Promise<VorherNachher>` – `laeuft`, solange `heute <= nach.bis`.
- [ ] **Step 1: Failing tests:** Maßnahme am `heute − 10` → `{status:'laeuft', restTage: 19}`; Maßnahme in der Zukunft (+3) → `laeuft`, `restTage: 31`; Maßnahme am `heute − 40` → `fertig`, `vergleich.a.zeitraum.von` = Datum −28; Kunde B sieht Maßnahmen von A nicht.
- [ ] **Step 2:** FAIL → implementieren (Kennzahlen gemockt) → PASS.
- [ ] **Step 3:** Seite Logbuch: Liste, „Maßnahme eintragen“, je Eintrag Vorher-nachher-Kärtchen mit Hinweis bei `zuWenigDaten`.
- [ ] **Step 4: Commit** „feat: Maßnahmen-Logbuch mit Vorher-nachher“.

### Task 4: Exporte

**Files:**
- Create: `src/lib/server/export/csv.ts`, `xlsx.ts`, `json.ts`, `src/routes/(team)/websites/[id]/export/+server.ts`, `tests/unit/export.test.ts`

**Interfaces:**
- Consumes: `Kennzahlen` (Task 2).
- Produces: `exportiere(k: Kennzahlen, format: 'csv' | 'xlsx' | 'json'): Promise<{ dateiname: string; mime: string; inhalt: Buffer }>`; Dateiname `wa-<domain>-<von>-<bis>.<endung>`; `GET …/export?von=…&bis=…&format=…` nur für Team.
- [ ] **Step 1: Failing tests:** CSV beginnt mit BOM `﻿`, nutzt `;`; Titel `Preise; "neu"` → `"Preise; ""neu"""`; Titel `=SUMME(A1)` → beginnt im CSV und XLSX mit `'` (Formelschutz); Konversionsrate 0.0523 → CSV `5,23 %`; JSON hat `schema: 'wa.kennzahlen.v1'` und dieselbe `besuche`-Zahl wie das Objekt; XLSX lässt sich mit `exceljs` wieder lesen, Blatt „Kennzahlen“, Zelle B2 = `besuche`.
- [ ] **Step 2:** FAIL → implementieren → PASS.
- [ ] **Step 3:** Download-Knöpfe auf der Kennzahlen-Seite.
- [ ] **Step 4: Commit** „feat: Exporte CSV, XLSX, JSON“.

### Task 5: Berichtsdaten, Vorlage und PDF

**Files:**
- Create: `src/lib/server/bericht/daten.ts`, `vorlage.ts`, `pdf.ts`, `static/schriften/*`, `tests/unit/bericht-vorlage.test.ts`, `tests/unit/bericht-pdf.test.ts`
- Modify: `installation/Dockerfile` (Chromium: `npx playwright@1.48.2 install --with-deps chromium`), `installation/entwicklung/docker-compose.dev.yml` (gleiches im Dev-Image)

**Interfaces:**
- Consumes: `holeKennzahlen`, `vergleiche`, `listeMassnahmen`, `vorherNachher`, `monatsZeitraum`.
- Produces:
  - `type BerichtDaten = { kunde: Kunde; website: Website; monat: string; aktuell: Kennzahlen; vormonat: Kennzahlen; vorjahr: Kennzahlen | null; massnahmen: { massnahme: Massnahme; ergebnis: VorherNachher }[]; vorschlaege: string[] }`. Plan 1c ergänzt die optionalen Felder `suchbegriffe?: Suchbegriff[]` und `ki?: KiBerichtTeil`, Plan 1d füllt `ki.check`; fehlt ein Feld, entfällt der Abschnitt.
  - `baueBerichtDaten(sql, websiteId, monat): Promise<BerichtDaten>` (`vorschlaege` kommen aus einem Textfeld am Bericht, das das Team ausfüllt; leer = Abschnitt „Was wir als Nächstes vorschlagen“ entfällt).
  - `berichtHtml(d: BerichtDaten): string` – Abschnitte in dieser Reihenfolge: „Das Wichtigste in 3 Sätzen“, „Besucher und Anfragen“, „Woher die Besucher kommen“, „Suchbegriffe aus Google“, „KI-Sichtbarkeit“, „Was wir verbessert haben“, „Was wir als Nächstes vorschlagen“. Alle Werte HTML-escaped. Wenn `aktuell.vollstaendig === false`: rotes Band „Unvollständig: Für einige Tage fehlen Daten.“
  - `htmlZuPdf(html: string): Promise<Buffer>` – A4, Ränder 18/16 mm, Fußzeile „<PRODUKTNAME> – Monatsbericht <Monat> – Seite X von Y“.
  - „Das Wichtigste in 3 Sätzen“ wird aus Regeln gebaut (keine KI): Satz 1 Besuche und Veränderung zum Vormonat, Satz 2 Ziele und Konversionsrate, Satz 3 stärkster Kanal.
- [ ] **Step 1: Failing tests:** HTML enthält die Abschnittsüberschriften in genau dieser Reihenfolge (ohne die Abschnitte 4 und 5, solange `suchbegriffe`/`ki` fehlen); Seitentitel `<script>` erscheint escaped; Vormonat mit 0 Besuchen → Satz 1 ohne Prozentangabe; `vollstaendig=false` → Band vorhanden; PDF beginnt mit `%PDF-` und hat ≥ 1 Seite.
- [ ] **Step 2:** FAIL → implementieren → PASS.
- [ ] **Step 3: Commit** „feat: Monatsbericht als PDF“.

### Task 6: Bericht-Ablauf mit Freigabe und Nextcloud-Ablage

**Files:**
- Create: `db/migrations/005_berichte.sql`, `src/lib/server/bericht/ablauf.ts`, `src/lib/server/bericht/nextcloud.ts`, `src/routes/(team)/websites/[id]/berichte/…`, `tests/db/bericht-ablauf.test.ts`, `tests/unit/nextcloud.test.ts`

**Interfaces:**
- Consumes: Task 5.
- Produces:
  - Tabelle `app.berichte(id uuid pk, kunde_id uuid not null, website_id uuid not null, monat text not null, status text check in ('entwurf','unvollstaendig','fehler','freigegeben'), pdf bytea, daten jsonb, vorschlaege text, fehlergrund text, erstellt_am timestamptz, freigegeben_von uuid, freigegeben_am timestamptz, nextcloud_pfad text, unique (website_id, monat))`, RLS über `kunde_id`.
  - `erzeugeBericht(sql, websiteId, monat): Promise<Bericht>` – Status `entwurf`, `unvollstaendig` (wenn Kennzahlen unvollständig) oder `fehler` mit Grund; bei vorhandenem `freigegeben` → Fehler „Dieser Bericht ist schon freigegeben.“
  - `gibBerichtFrei(sql, berichtId, benutzerId): Promise<Bericht>` – nur aus `entwurf` (aus `unvollstaendig` nur mit Bestätigung `trotzUnvollstaendig: true`); lädt das PDF per WebDAV nach `<kunde.nextcloud_ordner>/Waybuild Analytics/<website.domain>/<monat>.pdf`. Upload-Fehler → Status bleibt `entwurf`, Meldung „Ablage in Nextcloud hat nicht geklappt.“
  - `ladeNachNextcloud(pfad: string, inhalt: Buffer): Promise<void>` mit `NC_WEBDAV_URL`, `NC_BENUTZER`, `NC_APP_PASSWORT` (ein eigener Nextcloud-Dienstbenutzer mit Schreibrecht nur auf die Kundenordner).
- [ ] **Step 1: Failing tests:** zweites `erzeugeBericht` für denselben Monat ersetzt einen `entwurf`; nach Freigabe wirft es „Dieser Bericht ist schon freigegeben.“; Freigabe eines `fehler`-Berichts → Fehler; Upload gemockt mit HTTP 507 → Status bleibt `entwurf`; Pfad mit Leerzeichen und Umlauten wird URL-kodiert.
- [ ] **Step 2:** FAIL → implementieren → PASS.
- [ ] **Step 3:** Seite „Berichte“: Liste je Monat mit Status, PDF ansehen, Feld „Vorschläge“, Knopf „Freigeben“. Kein Knopf zum Versenden.
- [ ] **Step 4: Commit** „feat: Bericht-Ablauf mit Freigabe“.

### Task 7: Zeitpläne, Störungsmeldungen, Gesundheitsprüfung

**Files:**
- Create: `db/migrations/006_jobs.sql`, `src/lib/server/jobs/warteschlange.ts`, `zeitplan.ts`, `stoerung.ts`, `scripts/arbeiter.ts`, `tests/db/jobs.test.ts`, `tests/unit/stoerung.test.ts`
- Modify: `src/routes/api/gesundheit/+server.ts`, `installation/docker-compose.yml` (Dienst `wa-arbeiter`, gleiches Image, Befehl `node build/arbeiter.js`), `installation/.env.beispiel`

**Interfaces:**
- Consumes: `erzeugeBericht`, `vormonat`.
- Produces:
  - `starteArbeiter(): Promise<void>` mit pg-boss, Zeitzone Europe/Berlin; Job `bericht-monat` Cron `0 6 2 * *` → für jede Website mit Kunde `aktiv` und `matomo_site_id` ein Job `bericht-website` (3 Versuche, 10 Minuten Pause).
  - `meldeStoerung(titel: string, text: string): Promise<void>` – schreibt in `app.stoerungen(id, zeit, titel, text, erledigt)` und, wenn `TALK_BOT_URL` und `TALK_BOT_GEHEIMNIS` gesetzt sind, eine Nachricht an einen Nextcloud-Talk-Bot (HMAC-SHA256-Signatur über Zufallswert + Text, Header `X-Nextcloud-Talk-Bot-Random`/`-Signature`). Text ohne Token, ohne Passwörter.
  - `GET /api/gesundheit` → `{ ok, datenbank: boolean, matomo: boolean, letzterBerichtslauf: string | null }`; `ok=false` → HTTP 503.
  - Oberfläche: Band „Störungen“ oben, solange unerledigte Einträge existieren.
- [ ] **Step 1: Failing tests:** Zeitplan berechnet für `2026-11-01T23:00:00Z` als nächsten Lauf `2026-11-02T05:00:00Z` (06:00 Berlin, Winterzeit); fehlgeschlagener `bericht-website` nach 3 Versuchen → genau ein Eintrag in `stoerungen`; Signatur entspricht einer bekannten Test-Signatur (fester Zufallswert, festes Geheimnis); Talk-Text enthält kein `token`.
- [ ] **Step 2:** FAIL → implementieren → PASS.
- [ ] **Step 3:** In der Entwicklung: Talk-Bot „Waybuild Analytics Meldungen“ (Controller, `occ talk:bot:install`, nur für einen internen Raum) eintragen; Testmeldung kommt an.
- [ ] **Step 4: Commit** „feat: Zeitpläne und Störungsmeldungen“.
