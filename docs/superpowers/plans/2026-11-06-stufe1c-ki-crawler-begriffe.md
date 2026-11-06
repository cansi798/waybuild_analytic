# Waybuild Analytics – Stufe 1c „KI-Crawler und Begriffe“ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** KI-Crawler aus Server-Logs erkennen und prüfen, Crawler-Auswertung mit robots.txt-Abgleich, KI-Referrer-Regeln im Tracking und Suchbegriffe aus der Google Search Console, jeweils mit Abschnitt im Monatsbericht.

**Architecture:** Ein Log-Import liest Access-Logs (manueller Upload oder SFTP), erkennt Bots per User-Agent-Liste, prüft die IP gegen die Listen der Anbieter, speichert nur Bot-Zeilen und gibt Chatbot-Abrufe an Matomo weiter (`recMode=1`). Menschliche Zeilen werden nie gespeichert.

**Tech Stack:** wie 1a/1b, dazu `ssh2-sftp-client` (Apache-2.0), `google-auth-library` (Apache-2.0); Node `zlib`, `dns/promises`, `net`.

**Spec:** `docs/superpowers/specs/2026-11-06-waybuild-analytics-design.md` (4.4, 4.5, 4.8) und `docs/superpowers/plans/2026-11-06-stufe1-uebersicht.md`.

## Global Constraints

- Alle Global Constraints aus 1a und 1b gelten.
- Log-Zeilen ohne Bot-Treffer verlassen nie den Arbeitsspeicher (keine Datei, keine Tabelle, kein Log).
- Gespeicherte IPs nur gekürzt: IPv4 letzte 2 Oktette = 0, IPv6 auf /48. Die volle IP wird nur zur Prüfung im Speicher benutzt.
- Bot-Rohdaten 90 Tage, Tageszusammenfassung 25 Monate.
- Bot-Liste und KI-Referrer-Liste sind Datendateien (`daten/bots.json`, `daten/ki-quellen.json`), Inhalt wie Spec 4.4/4.5; Felder `stand` (Datum) und `quelle` (URL) je Eintrag.
- Die robots.txt einer Website wird nur gelesen und angezeigt, nie geändert.
- Kein echter Kunden-Log ohne Cans „ja“; Tests mit selbst erzeugten oder anonymisierten Zeilen.

## Review Focus

1. Gefälschter User-Agent „GPTBot“ von einer IP außerhalb der OpenAI-Liste: Status `falsch`, getrennt gezählt – Test in Task 2.
2. Rotierte, gzip-komprimierte Logs (`access.log.1.gz`) und Zeilen mit IPv6 – Test in Task 3.
3. Dieselbe Log-Datei wird zweimal importiert: keine doppelten Abrufe – Test in Task 3.
4. Abgeschnittene oder kaputte Zeilen (z. B. letzte Zeile ohne Zeilenende, fehlendes Anführungszeichen): werden gezählt und übersprungen, Import läuft weiter – Test in Task 3.
5. Log-Datei mit 1 Million Zeilen: Import läuft gestreamt mit konstantem Speicher (unter 300 MB) – Test in Task 3.

---

## File Structure

```
daten/bots.json, daten/ki-quellen.json
src/lib/server/crawler/bots.ts          # erkenneBot
src/lib/server/crawler/ip-pruefung.ts   # ladeIpListen, pruefeIp, kuerzeIp
src/lib/server/crawler/log-zeile.ts     # parseZeile
src/lib/server/crawler/import.ts        # importiereLog
src/lib/server/crawler/quellen.ts       # LogQuelle, UploadQuelle, SftpQuelle
src/lib/server/crawler/auswertung.ts    # crawlerUebersicht, robotsStatus
src/lib/server/geheimnisse.ts           # geheimnis(ref)
src/lib/server/ki-quellen.ts            # istKiQuelle
src/lib/server/gsc.ts                   # holeSuchbegriffe
db/migrations/007_crawler.sql, 008_suchbegriffe.sql
src/routes/(team)/websites/[id]/ki-crawler/…
tests/fixtures/logs/*.log, *.log.gz, tests/fixtures/ip-listen/*.json
```

---

### Task 1: Bot-Liste und Erkennung

**Files:**
- Create: `daten/bots.json`, `src/lib/server/crawler/bots.ts`, `tests/unit/bots.test.ts`

**Interfaces:**
- Produces:
  - Eintrag: `{ name: string; muster: string; betreiber: string; gruppe: 'training' | 'suche' | 'nutzer' | 'sonstige'; ipListe?: string; rdns?: string[]; matomoChatbot: boolean; stand: string; quelle: string }`.
  - Einträge mindestens: GPTBot, OAI-SearchBot, ChatGPT-User, OAI-AdsBot, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Googlebot, Google-CloudVertexBot, GoogleOther, Gemini-Deep-Research, Google-NotebookLM, bingbot, Applebot, meta-externalagent, meta-externalfetcher, meta-webindexer, CCBot, MistralAI-User. IP-Listen: `https://openai.com/gptbot.json`, `searchbot.json`, `chatgpt-user.json`, `adsbot.json`; `https://claude.com/crawling/bots.json`; `https://www.perplexity.ai/perplexitybot.json`, `perplexity-user.json`; Google `https://developers.google.com/static/crawling/ipranges/common-crawlers.json` (+ Googlebot-Liste); Apple `applebot.json`. rDNS: Googlebot `googlebot.com`, `google.com`; bingbot `search.msn.com`; Applebot `applebot.apple.com`. `matomoChatbot: true` genau für ChatGPT-User, Claude-User, Perplexity-User, MistralAI-User, Gemini-Deep-Research, Google-NotebookLM.
  - `erkenneBot(userAgent: string): BotEintrag | null` – Teilstring ohne Groß/Klein; das längste passende Muster gewinnt (damit `Claude-SearchBot` nicht als `ClaudeBot` zählt).
- [ ] **Step 1: Failing tests:** echte UA-Beispiele aus der Spec-Quelle (OpenAI `…compatible; GPTBot/1.4; +https://openai.com/gptbot`) → `GPTBot`; `…OAI-SearchBot/1.4…` → `OAI-SearchBot`; `Claude-SearchBot` → nicht `ClaudeBot`; normaler Firefox-UA → `null`; leerer String → `null`; jeder Eintrag hat `stand` und `quelle`.
- [ ] **Step 2:** FAIL → implementieren → PASS. **Step 3: Commit** „feat: KI-Bot-Liste“.

### Task 2: IP-Prüfung und Kürzung

**Files:**
- Create: `src/lib/server/crawler/ip-pruefung.ts`, `tests/fixtures/ip-listen/*.json`, `tests/unit/ip-pruefung.test.ts`, `db/migrations/007_crawler.sql` (Teil `app.ip_listen(url text pk, inhalt jsonb, geladen_am timestamptz)`)

**Interfaces:**
- Consumes: `BotEintrag` (Task 1).
- Produces:
  - `ladeIpListen(sql, urls: string[]): Promise<Map<string, IpBereich[]>>` – lädt höchstens einmal pro 24 h neu, sonst Cache aus `app.ip_listen`; Ladefehler → alter Stand bleibt, `meldeStoerung` nach 3 Tagen ohne Erfolg. Formate: Google/OpenAI/Perplexity/Apple `{"prefixes":[{"ipv4Prefix"|"ipv6Prefix"}]}`; Anthropic-Format beim Umsetzen an der echten Datei prüfen, Fixture davon ablegen, Parser je Format.
  - `type Pruefung = 'geprueft' | 'falsch' | 'nicht_geprueft'`; `pruefeIp(ip: string, bot: BotEintrag, listen): Promise<Pruefung>` – `geprueft` bei Treffer in der Liste oder bestätigtem rDNS (Reverse-Lookup endet auf erlaubter Domain und Vorwärts-Lookup liefert dieselbe IP); `falsch`, wenn der Bot eine Liste oder rDNS hat und nichts passt; `nicht_geprueft`, wenn der Bot keine Prüfmöglichkeit hat oder die IP im Log schon gekürzt ist.
  - `kuerzeIp(ip: string): string` – `203.0.113.77` → `203.0.0.0`; `2001:db8:abcd:12::1` → `2001:db8:abcd::`.
- [ ] **Step 1: Failing tests:** IP in Fixture-Bereich → `geprueft`; IP außerhalb bei GPTBot → `falsch`; bei CCBot ohne Liste → `nicht_geprueft`; bereits gekürzte IP `203.0.0.0` → `nicht_geprueft`; rDNS gemockt (`crawl-66-249-66-1.googlebot.com` + Vorwärts gleiche IP) → `geprueft`, Vorwärts andere IP → `falsch`; `kuerzeIp` wie oben.
- [ ] **Step 2:** FAIL → implementieren → PASS. **Step 3: Commit** „feat: IP-Prüfung der KI-Bots“.

### Task 3: Log-Zeilen und Import

**Files:**
- Create: `src/lib/server/crawler/log-zeile.ts`, `src/lib/server/crawler/import.ts`, `tests/fixtures/logs/*`, `tests/unit/log-zeile.test.ts`, `tests/db/crawler-import.test.ts`, `scripts/log-erzeugen.ts`
- Modify: `db/migrations/007_crawler.sql` (Tabellen unten)

**Interfaces:**
- Consumes: `erkenneBot`, `pruefeIp`, `kuerzeIp`, `matomoApi`.
- Produces:
  - `type LogZeile = { ip: string; zeit: Date; methode: string; pfad: string; status: number; bytes: number; referrer: string | null; userAgent: string }`; `parseZeile(zeile: string): LogZeile | null` für Apache/Nginx „combined“.
  - Tabelle `app.crawler_abrufe(id bigserial, kunde_id uuid not null, website_id uuid not null, zeit timestamptz, bot text, gruppe text, pfad text, status int, ip_gekuerzt text, pruefung text, schluessel text unique)`; `schluessel` = sha256(website_id, zeit, pfad, userAgent, volle IP). RLS über `kunde_id`.
  - `type ImportErgebnis = { zeilen: number; kaputt: number; bots: number; neu: number; doppelt: number; anMatomo: number }`; `importiereLog(sql, websiteId: string, zeilen: AsyncIterable<string>): Promise<ImportErgebnis>` – Einfügen in Blöcken zu 500 mit `on conflict (schluessel) do nothing`; Chatbots (`matomoChatbot`) zusätzlich als `matomo.php`-Anfrage mit `rec=1`, `recMode=1`, `idsite`, `ua`, `url` (`https://<domain><pfad>`), `cdt` (Zeit der Log-Zeile), `http_status` und `token_auth` = `MATOMO_TOKEN_TRACKING`. Standard, änderbar: eigener Matomo-Benutzer `wa-tracking` mit Recht „write“ nur auf die eigenen Sites, weil Matomo ältere `cdt`-Zeitstempel nur mit Token annimmt. `npm run website:anlegen` (1a Task 4) gibt diesem Benutzer zusätzlich das Recht „write“ auf die neue Site. Das Token steht nur in der Server-Umgebung.
  - `gunzipFallsNoetig(datei: Readable, name: string): AsyncIterable<string>`.
- [ ] **Step 1:** `scripts/log-erzeugen.ts` erzeugt Fixture-Logs: Mischung Menschen/Bots, IPv4/IPv6, eine kaputte Zeile, eine Zeile ohne Zeilenende, `.gz`-Variante, eine Datei mit 1.000.000 Zeilen nur zur Laufzeit (nicht ins Repo).
- [ ] **Step 2: Failing tests:** `parseZeile` für eine Apache-Zeile liefert `status 200`, `pfad '/leistungen/'`, UA vollständig; kaputte Zeile → `null`; Import der Fixture: `bots` = Anzahl Bot-Zeilen, Tabelle enthält 0 Zeilen mit Menschen-UA, zweiter Import derselben Datei → `neu 0`, `doppelt = bots`; `.gz` liefert dasselbe Ergebnis wie unkomprimiert; gespeicherte `ip_gekuerzt` enden auf `.0.0` bzw. `::`; jede Chatbot-Zeile → genau ein `fetch` an `matomo.php` mit `recMode=1` und `cdt`; Nicht-Chatbots (GPTBot) → kein `fetch`; 1-Million-Zeilen-Datei: `process.memoryUsage().rss` bleibt unter 300 MB.
- [ ] **Step 3:** FAIL → implementieren (Streams, `readline`) → PASS. **Step 4: Commit** „feat: Log-Import für KI-Crawler“.

### Task 4: Log-Quellen, täglicher Abruf, Aufbewahrung

**Files:**
- Create: `src/lib/server/crawler/quellen.ts`, `src/lib/server/geheimnisse.ts`, `src/routes/(team)/websites/[id]/ki-crawler/upload/+page.server.ts`, `tests/unit/quellen.test.ts`, `tests/db/aufbewahrung.test.ts`
- Modify: `src/lib/server/jobs/zeitplan.ts`, `installation/docker-compose.yml` (Geheimnisdatei schreibgeschützt eingebunden), `installation/.env.beispiel`

**Interfaces:**
- Consumes: `importiereLog`, `starteArbeiter`, `meldeStoerung`.
- Produces:
  - `interface LogQuelle { dateien(seit: Date): AsyncIterable<{ name: string; zeilen: AsyncIterable<string> }> }`; `class UploadQuelle` (eine hochgeladene Datei, bis 200 MB, `.log`/`.gz`); `class SftpQuelle(ref: string, verzeichnis: string, muster: RegExp)`; verarbeitete Dateinamen in `app.log_dateien(website_id, name, groesse, importiert_am)`, damit nichts doppelt gelesen wird.
  - `geheimnis(ref: string): { host: string; benutzer: string; passwort?: string; schluessel?: string }` aus `/run/secrets/wa-geheimnisse.json` (root, 600, nur lesbar eingebunden); fehlender Eintrag → Fehler mit `ref`, ohne Inhalt.
  - Jobs: `crawler-logs` täglich 04:00 für Websites mit `log_zugang = 'sftp'`; `aufbewahrung` täglich 03:30: `crawler_abrufe` älter als 90 Tage in `app.crawler_tage(kunde_id, website_id, tag, bot, gruppe, abrufe, fehler_4xx, fehler_5xx)` zusammenfassen und löschen; `crawler_tage` und `berichte` älter als 25 Monate löschen.
  - Upload-Seite: Datei wählen → Ergebnis `ImportErgebnis` anzeigen.
- [ ] **Step 1: Failing tests:** `SftpQuelle` mit gemocktem Client liefert nur Dateien passend zum Muster und überspringt schon importierte Namen; Upload > 200 MB → Meldung „Die Datei ist zu groß (höchstens 200 MB).“; Aufbewahrung: Abruf von Tag −91 verschwindet aus `crawler_abrufe` und steht als Zähler in `crawler_tage`; Abruf von Tag −89 bleibt.
- [ ] **Step 2:** FAIL → implementieren → PASS.
- [ ] **Step 3:** Erkundung (Controller, mit Can): Welche Logs liefert IONOS für Bauwelt (Pfad, Format, IP gekürzt?) – Ergebnis in `installation/hoster-logs.md`. Ohne Zugang bleibt der manuelle Upload der Weg.
- [ ] **Step 4: Commit** „feat: Log-Quellen und Aufbewahrung“.

### Task 5: Crawler-Auswertung, robots.txt, Bericht-Abschnitt

**Files:**
- Create: `src/lib/server/crawler/auswertung.ts`, `src/routes/(team)/websites/[id]/ki-crawler/+page.svelte|+page.server.ts`, `tests/unit/robots.test.ts`, `tests/db/crawler-auswertung.test.ts`
- Modify: `src/lib/server/bericht/daten.ts`, `src/lib/server/bericht/vorlage.ts` (Abschnitt „KI-Sichtbarkeit“, Teil Crawler)

**Interfaces:**
- Consumes: `crawler_abrufe`, `crawler_tage`, `Zeitraum`.
- Produces:
  - `type CrawlerZeile = { bot: string; gruppe: string; abrufe: number; geprueft: number; falsch: number; seiten: number; fehler4xx: number; fehler5xx: number; zuletzt: string | null; robots: 'erlaubt' | 'gesperrt' | 'unbekannt' }`.
  - `crawlerUebersicht(sql, websiteId, zeitraum): Promise<{ zeilen: CrawlerZeile[]; topSeiten: { pfad: string; abrufe: number; bots: string[] }[]; nieGelesen: string[] }>` – `nieGelesen` = URLs aus `https://<domain>/sitemap.xml` (falls vorhanden, höchstens 500) ohne Abruf einer Gruppe `nutzer` oder `suche` im Zeitraum.
  - `robotsStatus(robotsTxt: string, bot: string, pfad = '/'): 'erlaubt' | 'gesperrt'` (Gruppen nach `User-agent`, längste Regel gewinnt, `Allow` schlägt gleich lange `Disallow`); `holeRobots(domain): Promise<string | null>` mit 10 s Zeitlimit.
  - `type CrawlerUebersicht = Awaited<ReturnType<typeof crawlerUebersicht>>`; `type KiBerichtTeil = { crawler?: CrawlerUebersicht; check?: unknown }` in `bericht/daten.ts`; `BerichtDaten` bekommt `ki?: KiBerichtTeil` (1d ersetzt `unknown` durch `KiSichtbarkeit`).
- [ ] **Step 1: Failing tests:** `robotsStatus` für `User-agent: GPTBot\nDisallow: /` → GPTBot `gesperrt`, ClaudeBot `erlaubt`; `User-agent: *\nDisallow: /intern/` + Pfad `/intern/x` → `gesperrt`, `/` → `erlaubt`; Gruppe mit mehreren `User-agent`-Zeilen; `falsch` geprüfte Abrufe zählen in `falsch`, nicht in `geprueft`; `nieGelesen` enthält eine Sitemap-URL ohne Abruf.
- [ ] **Step 2:** FAIL → implementieren → PASS.
- [ ] **Step 3:** Seite „KI-Crawler“: Tabelle je Bot mit Gruppe und Prüfstatus, Top-Seiten, „nie von KI gelesen“, Hinweis bei Websites ohne Logs: „Für diese Website liegen keine Server-Logs vor.“
- [ ] **Step 4: Commit** „feat: Crawler-Auswertung und robots.txt-Abgleich“.

### Task 6: KI-Referrer-Regeln

**Files:**
- Create: `daten/ki-quellen.json`, `src/lib/server/ki-quellen.ts`, `tests/unit/ki-quellen.test.ts`, `tests/matomo/ki-kanal.test.ts`
- Modify: `src/lib/server/tracking-code.ts`, `tests/unit/tracking-code.test.ts`

**Interfaces:**
- Produces:
  - `daten/ki-quellen.json`: Domains `chatgpt.com`, `chat.openai.com`, `perplexity.ai`, `www.perplexity.ai`, `gemini.google.com`, `copilot.microsoft.com`, `claude.ai`, `chat.mistral.ai`, `meta.ai`, `chat.deepseek.com`, `grok.com`; `utm_source`-Werte gleich den Domains plus `chatgpt`, `perplexity`, `copilot`.
  - `istKiQuelle(host: string | null, utmSource: string | null): string | null` → Domain der KI oder `null`.
  - Tracking-Code (Modus standard) ergänzt: Ist `document.referrer` leer und `utm_source` in der Liste, dann `_paq.push(['setReferrerUrl', 'https://' + domain])` vor `trackPageView`. Die Liste wird als JSON in den Code eingebettet (keine Nachlade-Anfrage).
- [ ] **Step 1: Failing tests:** `istKiQuelle(null, 'chatgpt.com') === 'chatgpt.com'`; `istKiQuelle('www.google.com', null) === null`; Tracking-Code enthält `setReferrerUrl` vor `trackPageView`; `tests/matomo/ki-kanal.test.ts` (Demo, mit Test-Token): ein Tracking-Aufruf mit `urlref=https://chatgpt.com` auf Site „WA-TEST“ landet nach `core:archive` in `Referrers.getReferrerType` als `ai`.
- [ ] **Step 2:** FAIL → implementieren → PASS. **Step 3: Commit** „feat: KI-Referrer-Regeln“.

### Task 7: Google Search Console

**Files:**
- Create: `db/migrations/008_suchbegriffe.sql`, `src/lib/server/gsc.ts`, `tests/unit/gsc.test.ts`, `installation/google-search-console.md`
- Modify: `src/lib/server/jobs/zeitplan.ts`, `src/lib/server/bericht/daten.ts`, `src/lib/server/bericht/vorlage.ts`, Website-Formular (Feld `gsc_property`)

**Interfaces:**
- Produces:
  - `type Suchbegriff = { begriff: string; klicks: number; impressionen: number; ctr: number; position: number }`.
  - `holeSuchbegriffe(property: string, zeitraum: Zeitraum, limit = 10): Promise<Suchbegriff[]>` – `POST https://searchconsole.googleapis.com/webmasters/v3/sites/{property}/searchAnalytics/query`, `dimensions: ['query']`, `rowLimit: limit`, Dienstkonto aus `GSC_DIENSTKONTO_DATEI` (Scope `https://www.googleapis.com/auth/webmasters.readonly`).
  - Tabelle `app.suchbegriffe(kunde_id, website_id, monat, begriff, klicks, impressionen, ctr, position)` mit RLS; Job `gsc-monat` am 2. um 05:00 (vor dem Bericht), füllt den Vormonat.
  - `BerichtDaten` bekommt `suchbegriffe?: Suchbegriff[]`. Bericht-Abschnitt „Suchbegriffe aus Google“: Top 10 mit Klicks und Impressionen; fehlt die Property → Abschnitt entfällt.
  - `installation/google-search-console.md`: Dienstkonto anlegen, E-Mail des Dienstkontos in der Search Console je Property als Nutzer mit Leserecht eintragen (Can).
- [ ] **Step 1: Failing tests:** gemockte Antwort mit 3 Zeilen → 3 `Suchbegriff` mit gerundeter `position` (1 Nachkommastelle); HTTP 403 → Fehler „Kein Zugriff auf die Search Console für <property>.“; Property-URL wird URL-kodiert (`sc-domain:bauwelt-handwerk.de`).
- [ ] **Step 2:** FAIL → implementieren → PASS. **Step 3: Commit** „feat: Suchbegriffe aus der Google Search Console“.
