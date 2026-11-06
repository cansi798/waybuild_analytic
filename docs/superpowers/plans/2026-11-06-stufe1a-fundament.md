# Waybuild Analytics – Stufe 1a „Fundament“ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lauffähiges Grundgerüst: Entwicklungsumgebung, Postgres mit Kundentrennung, Kunden und Websites, Matomo-Anbindung mit Zielen, Team-Anmeldung (Kunden-Login vorhanden, gesperrt), Oberfläche mit Tracking-Code, Vorschau und Installationspaket.

**Architecture:** SvelteKit-App (adapter-node, Port 3000). Postgres 16 mit RLS: die App verbindet sich als Rolle `wa_app`; jede Anfrage läuft in einer Transaktion mit `app.team` bzw. `app.kunde_id` (set_config lokal). Matomo nur über HTTP-API; zur Laufzeit mit einem Lese-Token, Anlegen von Sites nur per CLI mit einem Admin-Token, das beim Aufruf übergeben und nie gespeichert wird.

**Tech Stack:** Node 22, SvelteKit 2, Svelte 5, TypeScript, `postgres` 3.x, `@node-rs/argon2`, `otpauth`, Vitest, Playwright 1.48.2, Postgres 16, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-11-06-waybuild-analytics-design.md` (Abschnitte 4.1, 4.2, 4.8, 5) und `docs/superpowers/plans/2026-11-06-stufe1-uebersicht.md`.

## Global Constraints

- Gemeinsame Umgebung und Standard-Entscheidungen aus der Übersicht gelten.
- Matomo-Code wird nie ins Repo kopiert und nie verändert; Zugriff nur über `index.php?module=API` und `matomo.php`.
- Kein „Matomo“ in Produktname, Logo oder Seitentitel der App. Produktname nur aus `src/lib/marke.ts` (`PRODUKTNAME = 'Waybuild Analytics'`).
- Jede fachliche Tabelle hat `kunde_id uuid not null` (außer reinen Team-Tabellen) plus `ENABLE` und `FORCE ROW LEVEL SECURITY`.
- Die App läuft zur Laufzeit nie als Postgres-Superuser.
- Der Matomo-Lese-Token (`MATOMO_TOKEN_LESEN`) verlässt nie den Server: nicht in HTML, nicht in Logs, nicht in Fehlermeldungen.
- Kunden-Login: Konten können angelegt werden, Anmeldung ist gesperrt, solange `WA_KUNDEN_LOGIN` nicht `1` ist **und** `kunden.kunden_login_aktiv` nicht `true` ist (beides nötig).
- Oberfläche Deutsch, leichte Sprache, `line-height: 1.7`, Absatzabstand 20 px, Farben Türkis `#00a6a1`, Text-Türkis `#006b68`, mobil ab 360 px ohne seitliches Scrollen.
- Keine ausgehenden Mails.
- Abhängigkeiten nur mit Lizenz MIT, BSD, ISC oder Apache-2.0; exakte Versionen in `package.json`.
- Zeitzone Europe/Berlin für alle Datumslogik.
- Jede Änderung an Diensten oder Umgebungsvariablen hält `installation/` lauffähig.

## Review Focus

1. Domain-Eingabe in vielen Formen („https://www.Bauwelt-Handwerk.de/“, „bauwelt-handwerk.de “, mit Pfad) muss zu einer einheitlichen Domain werden, doppelte Domains abgelehnt – Test in Task 3.
2. Matomo nicht erreichbar oder antwortet mit `{"result":"error"}` beim Anlegen einer Website: keine halb angelegte Website in Postgres, klare Meldung – Test in Task 4.
3. Kunde versucht sich anzumelden, obwohl der Kunden-Login aus ist: gleiche Meldung „Der Kunden-Zugang ist noch nicht freigeschaltet.“, keine Sitzung – Test in Task 5.
4. Team-Benutzer wird deaktiviert, während er angemeldet ist: nächste Anfrage führt zur Anmeldeseite – Test in Task 5.
5. Ein Kunden-Kontext liest Daten eines anderen Kunden über eine direkte SQL-Abfrage: 0 Zeilen, auch bei vergessenem `where` – Test in Task 2.

---

## File Structure

```
/work/wa  (= /home/can/projekte/waybuild_analytic)
├── package.json, svelte.config.js, vite.config.ts, tsconfig.json, .env.example
├── db/migrations/001_rollen.sql, 002_kunden_websites.sql, 003_auth.sql
├── scripts/migrate.ts, scripts/seed-dev.ts, scripts/website-anlegen.ts, scripts/team-anlegen.ts
├── src/hooks.server.ts
├── src/lib/marke.ts                         # PRODUKTNAME, Farben
├── src/lib/server/db.ts                     # Pools, mitTeam, mitKunde
├── src/lib/server/kunden.ts                 # Kunden + Websites
├── src/lib/server/domain.ts                 # normalisiereDomain
├── src/lib/server/matomo/client.ts          # matomoApi, MatomoFehler
├── src/lib/server/matomo/einrichten.ts      # legeMatomoSiteAn, legeMatomoZieleAn
├── src/lib/server/ziele.ts                  # ZIELE-Katalog
├── src/lib/server/tracking-code.ts          # trackingCode(website)
├── src/lib/server/auth/{passwort,sitzung,ratelimit,totp}.ts
├── src/routes/api/gesundheit/+server.ts
├── src/routes/anmelden/…, src/routes/(team)/kunden/…, src/routes/(team)/websites/[id]/…
├── tests/unit/*.test.ts, tests/db/*.test.ts, tests/matomo/*.test.ts, tests/e2e/*.spec.ts
├── installation/  (Dockerfile, docker-compose.yml, Caddyfile, .env.beispiel, 1-…10-*.sh,
│                   WaybuildAnalytics-Installation.sh, ANLEITUNG.md, paket-erstellen.sh, entwicklung/)
└── THIRD-PARTY-NOTICES (erzeugt)
```

---

### Task 1: Entwicklungsumgebung und Grundgerüst

**Files:**
- Create: `installation/entwicklung/docker-compose.dev.yml`, `installation/entwicklung/LIESMICH.md`, SvelteKit-Skeleton, `src/lib/marke.ts`, `src/routes/api/gesundheit/+server.ts`, `tests/unit/gesundheit.test.ts`, `.gitignore`, `.env.example`

**Interfaces:**
- Produces: Container `wa-dev` (node:22-bookworm, Benutzer 1001:1001, Repo unter `/work/wa`, Netze `wa-dev_intern` + extern `waybuild-analytics-demo_wa-aussen`), Container `wa-pg` (postgres:16-alpine, nur `wa-dev_intern`, Volume `wa_pg`), Skripte `npm run dev|build|check|test|test:db|test:matomo|migrate`, `GET /api/gesundheit` → `200 {"ok":true}`.

- [ ] **Step 1:** `docker-compose.dev.yml` schreiben (Projektname `wa-dev`, keine `ports:`, `mem_limit` 2g App / 1g DB, `no-new-privileges`), nach `/opt/wa-dev/` kopieren, dort `.env` (root, chmod 600) mit zufälligen Passwörtern für `wa`, `wa_app`, `wa_auth` anlegen, `sudo -n docker compose -p wa-dev up -d`. Prüfen: `sudo -n docker exec wa-dev node -v` → `v22.…`; `sudo -n docker exec wa-dev getent hosts wa-matomo` liefert eine Adresse.
- [ ] **Step 2:** SvelteKit (TypeScript, Svelte 5, adapter-node, Vitest) im Repo anlegen, ohne `docs/`, `LICENSE`, `README.md` zu überschreiben. `vite dev` lauscht auf `0.0.0.0:3000`.
- [ ] **Step 3: Failing test** `tests/unit/gesundheit.test.ts`: `GET()` liefert Status 200, Body `{ ok: true }`.
- [ ] **Step 4:** `npm test` → FAIL. Endpunkt implementieren. `npm test` → PASS, `npm run build` → erfolgreich.
- [ ] **Step 5: Commit** „chore: Entwicklungsumgebung und Grundgerüst“.

### Task 2: Datenbank, Rollen, Kundentrennung

**Files:**
- Create: `scripts/migrate.ts`, `db/migrations/001_rollen.sql`, `src/lib/server/db.ts`, `tests/db/setup.ts`, `tests/db/trennung.test.ts`

**Interfaces:**
- Produces:
  - Rollen `wa_app`, `wa_auth` (login, nosuperuser, nobypassrls), Schema `app`, Testdatenbank `wa_test`.
  - `mitTeam<T>(fn: (sql: TransactionSql) => Promise<T>): Promise<T>` setzt `app.team = '1'`.
  - `mitKunde<T>(kundeId: string, fn: (sql: TransactionSql) => Promise<T>): Promise<T>` setzt `app.kunde_id`, `app.team = '0'`.
  - SQL-Funktion `app.darf_kunde(kunde uuid) returns boolean` = `current_setting('app.team', true) = '1' or kunde = nullif(current_setting('app.kunde_id', true), '')::uuid`. Jede RLS-Policy nutzt sie.
  - Start verweigert, wenn eine URL den Superuser `wa` nutzt (Meldung nennt nur den Variablennamen).

- [ ] **Step 1: Failing tests** `tests/db/trennung.test.ts` (Testtabelle `app.test_daten(kunde_id uuid, wert text)` mit RLS, in `setup.ts` angelegt):
  - `mitKunde(A)` + `select * from app.test_daten` → nur Zeilen von A.
  - `mitKunde(A)` + `insert … kunde_id = B` → Fehler (Policy `with check`).
  - ohne Kontext (reine Verbindung als `wa_app`) → 0 Zeilen.
  - `mitTeam` → alle Zeilen.
  - Kontext gilt nur in der Transaktion: direkt danach auf derselben Verbindung `current_setting('app.kunde_id', true)` = `''` oder `null`.
- [ ] **Step 2:** `npm run test:db` → FAIL.
- [ ] **Step 3:** Migrations-Runner (Tabelle `app.migrationen`, Dateien nach Namen sortiert, jede in einer Transaktion, setzt Rollen-Passwörter aus der Umgebung), `001_rollen.sql`, `db.ts` implementieren.
- [ ] **Step 4:** `npm run migrate && npm run test:db` → PASS.
- [ ] **Step 5: Commit** „feat: Datenbank mit Kundentrennung (RLS)“.

### Task 3: Kunden und Websites

**Files:**
- Create: `db/migrations/002_kunden_websites.sql`, `src/lib/server/domain.ts`, `src/lib/server/kunden.ts`, `tests/unit/domain.test.ts`, `tests/db/kunden.test.ts`

**Interfaces:**
- Consumes: `mitTeam`, `mitKunde` (Task 2).
- Produces:
  - Tabelle `app.kunden(id uuid pk, name text not null, paket text check in ('fundament','wegweiser','wahrzeichen'), vertrag_beginn date, ansprechperson text, status text check in ('aktiv','pausiert','beendet') default 'aktiv', kunden_login_aktiv boolean not null default false, nextcloud_ordner text, angelegt_am timestamptz default now())`; RLS über `id`.
  - Tabelle `app.websites(id uuid pk, kunde_id uuid not null references app.kunden, domain text not null unique, name text not null, matomo_site_id int unique, hoster text check in ('ionos','allinkl','github_pages','sonstiger'), log_zugang text check in ('keiner','sftp','upload') default 'upload', log_zugang_ref text, tracking_modus text check in ('standard','streng') default 'standard', gsc_property text, angelegt_am timestamptz default now())`; RLS über `kunde_id`. `log_zugang_ref` ist nur der Name eines Geheimnis-Eintrags, nie ein Passwort.
  - `normalisiereDomain(eingabe: string): string` – Kleinbuchstaben, ohne Schema, ohne Pfad, ohne Port, ohne Punkt am Ende, Leerzeichen getrimmt; `www.` bleibt erhalten. Ungültig → `Error('Ungültige Domain')`.
  - `type Kunde`, `type Website` (Felder wie Tabellen, camelCase); `NeuerKunde`, `NeueWebsite` = dieselben Felder ohne `id` und `angelegt_am`, Pflicht sind `name` bzw. `kundeId`, `domain`, `name`.
  - `legeKundeAn(sql, daten: NeuerKunde): Promise<Kunde>`, `listeKunden(sql): Promise<Kunde[]>`, `holeKunde(sql, id): Promise<Kunde | null>`, `aendereKunde(sql, id, daten: Partial<NeuerKunde>): Promise<Kunde>`.
  - `legeWebsiteAn(sql, daten: NeueWebsite): Promise<Website>` (domain normalisiert, `matomo_site_id` darf zuerst `null` sein), `setzeMatomoSiteId(sql, websiteId, siteId)`, `listeWebsites(sql, kundeId?)`, `holeWebsite(sql, id)`.

- [ ] **Step 1: Failing tests** `tests/unit/domain.test.ts`: `'https://www.Bauwelt-Handwerk.de/'` → `'www.bauwelt-handwerk.de'`; `' bauwelt-handwerk.de '` → `'bauwelt-handwerk.de'`; `'http://kerim.de:8080/a/b?x=1'` → `'kerim.de'`; `'bäckerei-müller.de'` → gleich `new URL('http://bäckerei-müller.de').hostname` (Punycode, beginnt mit `xn--`); `'nicht eine domain'` wirft. `tests/db/kunden.test.ts`: Website mit bereits vorhandener Domain (andere Schreibweise) → Fehler „Diese Domain gibt es schon.“; Kunde A sieht in `mitKunde(A)` keine Websites von B; `kunden_login_aktiv` ist nach dem Anlegen `false`.
- [ ] **Step 2:** Tests → FAIL.
- [ ] **Step 3:** Migration und Funktionen implementieren. Den Postgres-Fehler `23505` auf `websites.domain` in die Meldung „Diese Domain gibt es schon.“ übersetzen.
- [ ] **Step 4:** `npm test && npm run test:db` → PASS.
- [ ] **Step 5: Commit** „feat: Kunden und Websites“.

### Task 4: Matomo-Anbindung, Ziele, Lese-Benutzer

**Files:**
- Create: `db/migrations/002b_ziele.sql`, `src/lib/server/matomo/client.ts`, `src/lib/server/matomo/einrichten.ts`, `src/lib/server/ziele.ts`, `scripts/website-anlegen.ts`, `tests/unit/matomo-client.test.ts`, `tests/matomo/einrichten.test.ts`, `installation/matomo-lesebenutzer.md`

**Interfaces:**
- Consumes: `legeWebsiteAn`, `setzeMatomoSiteId` (Task 3).
- Produces:
  - `class MatomoFehler extends Error { methode: string }` – Meldung ohne Token und ohne URL-Parameter.
  - `matomoApi<T>(methode: string, params: Record<string, string>, token?: string): Promise<T>` – POST an `${MATOMO_URL}/index.php`, Body `module=API&method=…&format=JSON&token_auth=…`; Standard-Token `MATOMO_TOKEN_LESEN`; Zeitlimit 15 s; Antwort `{result:'error'}` oder HTTP ≠ 200 → `MatomoFehler`.
  - `type ZielSchluessel = 'anfrage' | 'buchen' | 'anruf' | 'mail' | 'whatsapp'`; `ZIELE`: Liste mit `schluessel: ZielSchluessel`, Name und Ereignis-Aktion: `anfrage` „Anfrage gesendet“ / „Formular gesendet“; `buchen` „Buchen geklickt“ / „Buchen geklickt“; `anruf` „Anruf geklickt“ / „Anruf geklickt“; `mail` „Mail geklickt“ / „Mail geklickt“; `whatsapp` „WhatsApp geklickt“ / „WhatsApp geklickt“. Ziel-Auslöser: Event-Aktion, Muster „exact“.
  - Tabelle `app.ziele(website_id uuid, kunde_id uuid, schluessel text, matomo_goal_id int, primary key (website_id, schluessel))` mit RLS (Migration `002b_ziele.sql`).
  - `legeMatomoSiteAn(adminToken: string, website: Website): Promise<number>` – `SitesManager.addSite` (Name, `https://<domain>`, Zeitzone Europe/Berlin, Währung EUR), danach `UsersManager.setUserAccess` für den Lese-Benutzer `MATOMO_LESEBENUTZER` mit `view` und für den Tracking-Benutzer `MATOMO_TRACKINGBENUTZER` mit `write` (gebraucht ab 1c für Chatbot-Abrufe aus Logs).
  - `legeMatomoZieleAn(adminToken: string, siteId: number): Promise<Record<ZielSchluessel, number>>` – `Goals.addGoal` je Ziel, idempotent (vorhandene Ziele gleichen Namens werden wiederverwendet).
  - CLI `npm run website:anlegen -- --website <uuid>`: liest das Admin-Token aus der Standardeingabe (nie als Argument, nie gespeichert), legt Site und Ziele an, schreibt IDs in Postgres. Schlägt Matomo fehl, bleibt die Website ohne `matomo_site_id` und die Meldung sagt das.
  - Bestehende Demo-Sites 1–4 verknüpft `scripts/seed-dev.ts` direkt mit ihren IDs (ohne `addSite`).
- Einmalig (Controller, nicht Teil der Tests): In der Demo den Matomo-Benutzer `wa-lesen` mit `view` auf die Sites 1–4 anlegen und sein Token als `MATOMO_TOKEN_LESEN` in `/opt/wa-dev/.env` eintragen. Ablauf in `installation/matomo-lesebenutzer.md` (ohne Token-Werte).

- [ ] **Step 1: Failing tests** `tests/unit/matomo-client.test.ts` (fetch gemockt): Antwort `{"result":"error","message":"x"}` → `MatomoFehler`; Fehlertext enthält weder `token_auth` noch den Token-Wert; Zeitüberschreitung → `MatomoFehler`; Token steht im Body, nicht in der URL. `tests/matomo/einrichten.test.ts` (gegen die Demo, nur wenn `MATOMO_TOKEN_ADMIN_TEST` gesetzt): legt Site „WA-TEST <Zeit>“ an, zweimal `legeMatomoZieleAn` liefert dieselben Goal-IDs, Lese-Benutzer sieht die Site per `SitesManager.getSiteFromId`; danach `SitesManager.deleteSite`. Zusätzlich (gemockt): `website:anlegen`, wenn `SitesManager.addSite` einen Fehler liefert → Website bleibt ohne `matomo_site_id`, Meldung beginnt mit „Matomo:“.
- [ ] **Step 2:** Tests → FAIL.
- [ ] **Step 3:** Implementieren.
- [ ] **Step 4:** `npm test` → PASS; `npm run test:matomo` mit Test-Admin-Token (vom Controller per stdin, danach Token in Matomo löschen) → PASS.
- [ ] **Step 5: Commit** „feat: Matomo-Anbindung und Ziele“.

### Task 5: Team-Anmeldung, Kunden-Login gesperrt

**Files:**
- Create: `db/migrations/003_auth.sql`, `src/lib/server/auth/{passwort,sitzung,ratelimit,totp}.ts`, `src/hooks.server.ts`, `src/routes/anmelden/+page.svelte`, `src/routes/anmelden/+page.server.ts`, `src/routes/abmelden/+server.ts`, `scripts/team-anlegen.ts`, `tests/unit/auth.test.ts`, `tests/db/anmeldung.test.ts`

**Interfaces:**
- Consumes: `db.ts` (Task 2), `app.kunden` (Task 3).
- Produces:
  - Tabellen `app.benutzer(id uuid pk, email citext unique, name text, rolle text check in ('team','kunde'), kunde_id uuid null references app.kunden, passwort_hash text, totp_geheimnis text null, aktiv boolean default true)` mit Check „rolle='kunde' ⇔ kunde_id not null“; `app.sitzungen(id text pk (sha256 des Cookie-Werts), benutzer_id uuid, laeuft_ab timestamptz, angelegt_am timestamptz)`. Zugriff nur über SECURITY-DEFINER-Funktionen, die `wa_auth` ausführen darf.
  - `meldeAn(email: string, passwort: string, totp?: string): Promise<{ ok: true; sitzungsCookie: string } | { ok: false; meldung: string }>`.
  - `locals.benutzer: { id: string; rolle: 'team' | 'kunde'; kundeId: string | null; name: string } | null` in `hooks.server.ts`; Seiten unter `(team)` verlangen `rolle === 'team'`.
  - Cookie `wa_sitzung`: HttpOnly, Secure, SameSite=Lax, 12 Stunden. Team-Konten verlangen TOTP.
  - CLI `npm run team:anlegen -- --email … --name …` gibt Startpasswort und TOTP-QR einmalig auf der Konsole aus.
- Meldungen (genau so): falsche Daten „E-Mail, Passwort oder Code stimmt nicht.“; zu viele Versuche „Zu viele Versuche. Bitte in 15 Minuten erneut versuchen.“; Kunde gesperrt „Der Kunden-Zugang ist noch nicht freigeschaltet.“

- [ ] **Step 1: Failing tests:** unbekannte E-Mail und falsches Passwort → identische Meldung; 6. Fehlversuch in 15 Minuten je E-Mail → Meldung „Zu viele Versuche …“; Kunde mit richtigem Passwort, `WA_KUNDEN_LOGIN` nicht gesetzt → „Der Kunden-Zugang ist noch nicht freigeschaltet.“, keine Zeile in `sitzungen`; Kunde mit `WA_KUNDEN_LOGIN=1`, aber `kunden_login_aktiv=false` → dieselbe Meldung; Team-Benutzer mit gültiger Sitzung wird auf `aktiv=false` gesetzt → nächste Sitzungsprüfung liefert `null`; abgelaufene Sitzung → `null`.
- [ ] **Step 2:** Tests → FAIL.
- [ ] **Step 3:** Implementieren (argon2id, TOTP mit `otpauth`, 30 s, ±1 Fenster).
- [ ] **Step 4:** `npm test && npm run test:db` → PASS.
- [ ] **Step 5: Commit** „feat: Team-Anmeldung, Kunden-Login gesperrt“.

### Task 6: Oberfläche Kunden, Websites, Tracking-Code

**Files:**
- Create: `src/lib/server/tracking-code.ts`, `src/lib/stil.css`, `src/routes/(team)/+layout.svelte`, `src/routes/(team)/kunden/+page.svelte|+page.server.ts`, `src/routes/(team)/kunden/[id]/…`, `src/routes/(team)/websites/[id]/…`, `tests/unit/tracking-code.test.ts`, `tests/e2e/kunden.spec.ts`

**Interfaces:**
- Consumes: Funktionen aus Task 3, `ZIELE` (Task 4), `locals.benutzer` (Task 5).
- Produces:
  - `trackingCode(website: Website, trackerUrl: string): string`. Inhalt bei Modus `standard`: `_paq.push(['disableCookies'])`, `_paq.push(['disableBrowserFeatureDetection'])`, `setSiteId`, `setTrackerUrl` = `${trackerUrl}/matomo.php`; ein Klick-Helfer, der bei `a[href^="tel:"]` → Ereignis (`Kontakt`, `Anruf geklickt`), `a[href^="mailto:"]` → (`Kontakt`, `Mail geklickt`), `a[href*="wa.me"], a[href*="whatsapp"]` → (`Kontakt`, `WhatsApp geklickt`), `[data-wa-ziel="buchen"]` → (`Termin`, `Buchen geklickt`) sendet; Hinweistext, dass das Formular-Ziel per `_paq.push(['trackEvent','Formular','Formular gesendet'])` nach erfolgreichem Senden ausgelöst wird. Bei Modus `streng` liefert die Funktion keinen Browser-Code, sondern den Text „Diese Website wird nur serverseitig gemessen. Es wird kein Skript eingebunden.“
  - Seiten: Kundenliste, Kunde anlegen/bearbeiten, Kundenseite mit Websites, Website-Seite mit Matomo-Status („verbunden“ / „noch nicht in Matomo angelegt“) und Tracking-Code zum Kopieren. Gelöscht wird nichts (kein Lösch-Knopf in Stufe 1). Unter dem Tracking-Code steht der Opt-out-Baustein für die Datenschutzerklärung: `<div id="matomo-opt-out"></div><script src="<trackerUrl>/index.php?module=CoreAdminHome&action=optOutJS&divId=matomo-opt-out&language=auto&showIntro=1"></script>`.
- [ ] **Step 1: Failing tests** `tests/unit/tracking-code.test.ts`: Standard enthält `disableCookies` und `disableBrowserFeatureDetection` und `setSiteId', '7'` für Site 7; Standard enthält weder `setUserId` noch `enableHeartBeatTimer`; Streng enthält kein `<script`; Domain mit `"` oder `<` im Namen wird im Code escaped. `tests/e2e/kunden.spec.ts`: Team-Login → Kunde „Test GmbH“ anlegen → Website „test.invalid“ anlegen → Website-Seite zeigt „noch nicht in Matomo angelegt“; Ansicht 360 px ohne seitliches Scrollen.
- [ ] **Step 2:** Tests → FAIL.
- [ ] **Step 3:** Implementieren (reines CSS, Schriften lokal, Formulare mit SvelteKit-Actions).
- [ ] **Step 4:** `npm test` → PASS; E2E im Playwright-Container gegen die Vorschau (nach Task 7) oder gegen `vite preview` → PASS.
- [ ] **Step 5: Commit** „feat: Oberfläche Kunden, Websites, Tracking-Code“.

### Task 7: Vorschau unter wa-app.169-58-147-249.sslip.io

**Files:**
- Create: `scripts/start-vorschau.sh`, `installation/entwicklung/vorschau-wache.sh`
- Modify: `/opt/nextcloud-stack/Caddyfile` (nur ein neuer Block, Controller-Aufgabe)

**Interfaces:**
- Produces: `https://wa-app.169-58-147-249.sslip.io` → `wa-dev:3000` (`node build`, `ORIGIN` = diese URL), Header `X-Robots-Tag: noindex, nofollow`, HSTS, `nosniff`; `GET /api/gesundheit` von außen → 200.

- [ ] **Step 1:** `scripts/start-vorschau.sh`: baut im Container und startet `node build` im Hintergrund mit `ORIGIN`, `PORT=3000`; schreibt `vorschau.log` (gitignored).
- [ ] **Step 2:** Caddy-Block „# Waybuild Analytics App (Entwicklung) BEGIN/END“ nach dem Demo-Block einfügen. Ablauf: Sicherung `Caddyfile.bak-<datum>-wa-app`, `caddy validate` im Caddy-Container, `caddy reload` nur, wenn gerade keine Talk-Anrufe laufen. Caddy ist bereits im Netz `waybuild-analytics-demo_wa-aussen`; `wa-dev` hängt dort auch.
- [ ] **Step 3:** `vorschau-wache.sh` (Cron alle 5 Minuten): startet `node build`, wenn kein Prozess auf Port 3000 läuft.
- [ ] **Step 4:** Prüfen: `curl -s https://wa-app.169-58-147-249.sslip.io/api/gesundheit` → `{"ok":true}`; `curl -sI …` enthält `x-robots-tag: noindex`.
- [ ] **Step 5: Commit** „chore: Vorschau“.

### Task 8: Installationspaket und Lizenzhinweise

**Files:**
- Create: `installation/Dockerfile`, `installation/docker-compose.yml`, `installation/Caddyfile`, `installation/.env.beispiel`, `installation/1-voraussetzungen-pruefen.sh` … `installation/10-sicherung-wiederherstellen.sh`, `installation/WaybuildAnalytics-Installation.sh`, `installation/ANLEITUNG.md`, `installation/paket-erstellen.sh`, `installation/VERSION`, `scripts/lizenzen.ts`, `THIRD-PARTY-NOTICES`, `tests/unit/installation.test.ts`

**Interfaces:**
- Produces:
  - Produktions-Compose (Projekt `waybuild-analytics`): `wa-app` (Image aus `installation/Dockerfile`, node:22-bookworm, Benutzer nicht root), `wa-pg` (postgres:16), `wa-matomo` + `wa-archiv` (matomo:5.14.2-apache, Digest wie in der Demo), `wa-db` (mariadb:11.4.13, Digest wie in der Demo), `wa-caddy` (caddy:2, einzige Ports 80/443). Netze `intern` (internal) und `aussen`.
  - Skripte: `1-voraussetzungen-pruefen`, `2-installieren`, `3-starten`, `4-stoppen`, `5-aktualisieren`, `6-status-und-logs`, `7-matomo-einrichten` (setzt dieselben Datenschutz-Einstellungen wie die Demo: IP-Kürzung 2 Bytes auch für Standort, Tracking ohne Cookies erzwungen, Do-Not-Track beachten, Rohdaten nach 180 Tagen löschen, Browser-Archivierung aus, Internet-Funktionen aus), `8-team-benutzer-anlegen`, `9-sicherung-erstellen` (pg_dump + mariadb-dump + Konfiguration nach `/root/waybuild-analytics-sicherung/<datum>/`, letzte 7 bleiben; optional restic, wenn `RESTIC_REPOSITORY` gesetzt), `10-sicherung-wiederherstellen`, `11-deinstallieren` (fragt zweimal nach). Menü `WaybuildAnalytics-Installation.sh` ruft sie per Nummer auf.
  - `npm run lizenzen` schreibt `THIRD-PARTY-NOTICES` (Name, Version, Lizenz je Paket) und bricht mit Fehler ab, wenn ein Paket eine Lizenz außerhalb von MIT, BSD-2-Clause, BSD-3-Clause, ISC, Apache-2.0, 0BSD hat.
  - Abschnitt „Matomo“ in `THIRD-PARTY-NOTICES`: GPL-3.0-or-later, JS-Tracker BSD-3-Clause, wird als eigenes Image betrieben, kein Code im Repo.
- [ ] **Step 1: Failing test** `tests/unit/installation.test.ts`: jedes Skript 1–11 existiert und ist ausführbar; `.env.beispiel` enthält jede Variable, die `src/` per `process.env.X` liest (Liste per Regex aus dem Quellcode); `docker-compose.yml` veröffentlicht Ports nur bei `wa-caddy`; `THIRD-PARTY-NOTICES` enthält „Matomo“ und „GPL-3.0“.
- [ ] **Step 2:** Test → FAIL.
- [ ] **Step 3:** Implementieren. `docker compose -f installation/docker-compose.yml config` muss ohne Fehler laufen (mit `.env.beispiel`).
- [ ] **Step 4:** `npm test` → PASS; `bash installation/paket-erstellen.sh` erzeugt `dist-paket/waybuild-analytics-<VERSION>.zip` ohne `.env`.
- [ ] **Step 5: Commit** „chore: Installationspaket und Lizenzhinweise“.
