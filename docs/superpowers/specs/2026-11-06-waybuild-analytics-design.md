# Waybuild Analytics – Konzept und Spezifikation (Design-Spec)

| | |
|---|---|
| Produkt | Waybuild Analytics (Arbeitstitel; Can sagte „Waybuild Analytic“, Name noch offen) |
| Firma | Waybuild UG (haftungsbeschränkt) – Can Siebert, Jamil Iqbal |
| Stand | 06.11.2026, Version 1.0 (Entwurf zur Prüfung) |
| Status | **Wartet auf Freigabe durch Can und Jamil.** Vor der Freigabe wird nicht programmiert. |
| Prozess | Brainstorming-Skill, Pfad „architectural“: Spec → Freigabe → Umsetzungsplan (writing-plans) → Freigabe → Umsetzung |
| Talk | SW-0004 Waybuild Analytics (63yitbs3) |
| Repo | github.com/cansi798/waybuild_analytic (privat) |

Hinweis zum Ablauf: Normalerweise stimmen wir die Design-Abschnitte einzeln im Chat ab. Can hat am 06.11. um 22:10 „Leg los“ gesagt. Deshalb kommen hier alle Abschnitte gesammelt in einem Dokument. Jeder Abschnitt kann einzeln geändert werden.

---

## 1. Zielbild und Erfolgskriterien

### 1.1 Was Can gesagt hat (06.11.2026, Talk)

| Zeit | Aussage (gekürzt) |
|---|---|
| 21:54 | „Ja, ich möchte Matomo, aber entwickle selbst die fehlenden Sachen, und dann nennen wir die Software Waybuild Analytic. Ich werde ein Repo privat machen …“ |
| 22:01 | „Erweitere Sachen mit den neuesten Standards, sodass wir auch KI-Optimierung machen: AEO, GEO oder was es gibt. Es soll auch MCP-freundlich sein.“ |
| 22:01 | „Die Lizenz muss so sein, dass es ohne Gebühren und Erlaubnis unsererseits nicht erlaubt ist. Bitte schau nach dem neuesten Standard.“ |
| 22:01 | „Wir wollen auch, dass analysiert wird, wie KI-Bots uns gesucht und gefunden haben, damit wir Begriffe sammeln.“ |
| 22:02 | Eigener Talk mit Jamil. „Wir werden es aber auf einem anderen Server laufen lassen.“ |
| 22:10 | Liefermodell: „A) nur als Dienst von uns. Du kannst einen Kunden-Zugang mit einbringen, aber der soll erstmal inaktiv sein. Eher, dass wir jeden Kunden dort strukturiert haben und jede Website uns ansehen können, und automatisierte Berichte und Exporte, sodass wir auch eine Optimierung der Website machen und Verbesserungen sehen können.“ |
| 22:10 | „Leg los, und beachte bitte alle Standard-KI-Modelle und zeig uns, was du kannst.“ |

Daraus folgen diese festen Vorgaben:

- V1: Matomo ist die Basis. Fehlende Funktionen bauen wir selbst.
- V2: Betrieb nur als Dienst der Waybuild UG. Wir geben die Software nicht an Kunden heraus.
- V3: Eigener Server, getrennt vom Nextcloud-Server.
- V4: Struktur Kunde → Websites. Ein Kunden-Login ist vorbereitet, aber ausgeschaltet.
- V5: Automatische Berichte und Exporte. Wir sehen, ob unsere Verbesserungen wirken.
- V6: KI-Sichtbarkeit (AEO = Answer Engine Optimization, GEO = Generative Engine Optimization): Wie finden KI-Bots und KI-Assistenten die Websites? Welche Begriffe spielen eine Rolle?
- V7: MCP-freundlich, also nutzbar für Claude und andere KI-Assistenten.
- V8: Unser Code darf ohne unsere Erlaubnis und ohne Gebühr nicht genutzt werden.
- V9: Alle gängigen KI-Modelle berücksichtigen (ChatGPT, Claude, Gemini, Perplexity, Copilot und weitere).

### 1.2 Annahmen (bitte prüfen)

| Nr. | Annahme |
|---|---|
| A1 | Nutzer sind zuerst Can und Jamil (Team). Kunden sehen in Stufe 1 nur die Berichte, die wir ihnen schicken. |
| A2 | Es geht um unsere eigenen Websites (waybuild Website, Hauptseite, Bauwelt, Kerim, Funkelfilm, Personal Branding) und um Kundenwebsites aus den Paketen Fundament, Wegweiser und Wahrzeichen. |
| A3 | Der Monatsbericht aus „Wegweiser“ („Besucher, Anfragen, Suchbegriffe“) wird mit Waybuild Analytics erstellt. Das Versprechen „Suchbegriffe“ braucht dafür Daten aus der Google Search Console. |
| A4 | Datenschutz bleibt wie bisher: keine Cookies, kein Banner, Server in Deutschland oder der EU. |
| A5 | Wir bleiben beim Technik-Stack des CRM: TypeScript, SvelteKit, Node 22, Postgres, Docker. Dann können wir Wissen und Bausteine teilen. |
| A6 | Am Anfang reichen bis zu etwa 50 Websites und bis zu etwa 2 Millionen Seitenaufrufe pro Monat. |
| A7 | Berichte werden nicht automatisch an Kunden gemailt. Sie landen als Entwurf bei uns. Wir prüfen und geben frei (Regel: keine externe Mail ohne Cans „ja“). |
| A8 | Die Kosten für KI-Abfragen sollen pro Kunde und Monat klein bleiben (Vorschlag: höchstens 10 € netto). |
| A9 | Die Matomo-Demo des anderen Agenten (analytics.169-58-147-249.sslip.io) ist nur zum Anschauen. Der echte Betrieb läuft später auf dem neuen Server. |

### 1.3 Zielbild in einem Absatz

Waybuild Analytics ist unser eigener Analyse-Dienst. Matomo sammelt die Besucherdaten ohne Cookies. Daneben läuft unsere eigene Anwendung. Sie ordnet jede Website einem Kunden zu, rechnet Ziele wie „Anfrage gesendet“ oder „Buchen geklickt“ aus und erstellt jeden Monat einen Bericht als PDF im Waybuild-Design. Sie misst außerdem, welche KI-Crawler die Seiten lesen und welche Besucher über ChatGPT, Perplexity und andere Assistenten kommen. Einmal im Monat fragt sie die großen KI-Modelle mit Test-Fragen ab: Wird die Firma genannt, und mit welchen Begriffen? Jede Verbesserung an einer Website tragen wir in ein Logbuch ein. Die Anwendung zeigt dann, was sich vorher und nachher verändert hat. Über einen MCP-Server können Claude und andere Assistenten diese Zahlen lesen und Berichtsentwürfe anstoßen.

### 1.4 Erfolgskriterien

| Nr. | Kriterium | Messung |
|---|---|---|
| E1 | Jede unserer Websites ist einem Kunden zugeordnet und liefert Daten. | Übersicht „Kunden → Websites“ ist vollständig. Jede Website hat in den letzten 24 Stunden Daten. |
| E2 | Ziele werden gezählt. | „Anfrage gesendet“ und „Buchen/Anrufen/Mail geklickt“ erscheinen in einem Test innerhalb von 1 Stunde im Bericht. |
| E3 | Der Monatsbericht entsteht automatisch. | Am 2. Kalendertag des Monats um 08:00 liegt für jede aktive Website ein PDF-Entwurf bereit. Kein Fehler, oder der Fehler ist sichtbar markiert. |
| E4 | Exporte funktionieren. | CSV, XLSX und JSON für einen beliebigen Zeitraum, gleiche Zahlen wie im Bericht. |
| E5 | Vorher-nachher ist sichtbar. | Zu jeder Maßnahme im Logbuch gibt es einen Vergleich von 28 Tagen davor und 28 Tagen danach. |
| E6 | KI-Crawler werden erkannt. | Für jede Website mit Server-Logs: Liste der KI-Bots mit Seiten und Anzahl, mit Hinweis „IP geprüft“ oder „nicht geprüft“. |
| E7 | KI-Sichtbarkeit wird gemessen. | Pro Kunde gibt es eine Monatstabelle: Modell × Test-Frage → genannt ja/nein, zitierte Seite, Begriffe. |
| E8 | MCP funktioniert sicher. | Claude Code kann mit einem Kunden-Token nur die Daten dieses Kunden lesen. Ein automatischer Test beweist das. |
| E9 | Datenschutz ohne Banner bleibt möglich. | Keine Cookies, keine Speicherung voller IP-Adressen, Opt-out funktioniert. Rechtliche Prüfung ist dokumentiert. |
| E10 | Unser Code bleibt geschützt. | Unser Code steht in keinem öffentlichen Repo, hat eine Lizenz „Alle Rechte vorbehalten“ und ist sauber von Matomo getrennt. |

### 1.5 Nicht-Ziele (erst einmal nicht)

- Kein Verkauf oder Download der Software an Kunden (siehe V2).
- Keine Heatmaps und keine Sitzungsaufzeichnung. Das ginge nur mit Einwilligung und Banner.
- Keine Werbe-Analyse (Google Ads, Meta Ads).
- Kein Selbstbedienungs-Portal mit Bezahlung. Das ist frühestens etwas für später.
- Kein Nachbau der kostenpflichtigen Matomo-Premium-Plugins.

---

## 2. Lösungswege

### 2.1 Was Matomo heute schon kann (Stand November 2026)

Wichtig für die Entscheidung: Matomo hat seit 2025 und 2026 selbst KI-Funktionen eingebaut. Die aktuelle Version ist **Matomo 5.14.2** (veröffentlicht am 22.10.2026, GitHub Releases).

| Funktion | Seit | Wo | Bedeutung für uns |
|---|---|---|---|
| Kanal „AI Assistants“ (Besucher über ChatGPT, Copilot, Gemini, Claude, Le Chat, Meta AI, iAsk, Perplexity) | 5.5.0 | Kern (Referrers) | Den KI-Referrer-Kanal müssen wir nicht selbst bauen. |
| AI-Chatbot-Tracking (Plugin `BotTracking`) | 5.8.0 (04.03.2026), ab 5.12.0 auch Inhaltsberichte | Kern-Plugin, muss aktiviert werden | Matomo erkennt **nur Nutzer-Abrufe**: `ChatGPT-User`, `Claude-User`, `Perplexity-User`, `MistralAI-User`, `Gemini-Deep-Research`, `Google-NotebookLM`. Die Daten kommen über die HTTP-Tracking-API (`recMode=1`) oder fertige Anbindungen für Cloudflare, Amazon CloudFront und WordPress. |
| Berichte „AI Agents“ (Plugin `AIAgents`) | 5.x | Kern | Erkennt KI-Agenten, die selbst durch Seiten klicken. |
| KI-Anbieter (Plugin `AIProviders`: Anthropic, OpenAI, Google, Bedrock, eigene) | 5.x-Entwicklungszweig | Kern | Matomo bindet selbst KI-Modelle an. Für uns zunächst nicht nötig. |
| MCP-Server (Plugin `McpServer`) | Plugin 5.1.2, braucht Matomo ab 5.8 | Kostenlos, GPL v3 oder später, „early preview“ | Liest Berichte. Kann aber auf Wunsch auch rohe API-Methoden ausführen. Darum nicht öffentlich freigeben. |
| E-Mail-Berichte mit PDF (`ScheduledReports`) | lange | Kern | Technisch vorhanden, aber nicht in unserem Design und ohne Erklärungen oder Vorher-nachher. |

**Was fehlt und unsere Eigenleistung ist:**

1. Klassische KI-**Crawler** (GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, CCBot, Applebot, Bingbot, Meta-ExternalAgent usw.). Matomo zählt diese nicht.
2. Die Struktur Kunde → Websites mit Waybuild-Logik, Kunden-Login (ausgeschaltet) und Rechten pro Kunde.
3. Monatsbericht im Waybuild-Design, in einfacher Sprache, mit Vorher-nachher und Maßnahmen-Logbuch.
4. AI-Visibility-Check: regelmäßige Test-Fragen an ChatGPT, Claude, Gemini, Perplexity, mit Auswertung „genannt ja/nein, mit welchen Begriffen“.
5. Suchbegriffe aus der Google Search Console und KI-Daten aus den Bing Webmaster Tools. Bei Matomo ist das nur als kostenpflichtiges Premium-Plugin verfügbar.
6. Ein MCP-Server mit Token pro Kunde und klaren, sicheren Werkzeugen.

### 2.2 Weg A – Matomo-Kern plus eigene Matomo-Plugins plus Theme

Alles läuft **innerhalb von Matomo**: eigene PHP-Plugins (Kunden-Struktur, Crawler-Import, Berichte, Prompt-Check, MCP) und ein eigenes Theme, das Matomo wie „Waybuild Analytics“ aussehen lässt.

- Vorteile: eine einzige Oberfläche. Wir nutzen Matomo-Rechte, Segmente und Archivierung direkt.
- Nachteile:
  - Neue Sprache (PHP, Twig, Vue im Matomo-Stil) neben unserem TypeScript-Stack.
  - Plugin-Schnittstellen ändern sich bei großen Versionen. Matomo 6 ist in Arbeit, das McpServer-Plugin begrenzt sich schon heute auf „unter 6.0.0“. Nach jedem großen Update müssen wir unsere Plugins anpassen.
  - Kunden-Struktur und Kunden-Login müssten wir in das Matomo-Rechtesystem einbauen. Das ist aufwendig und anfällig.
- Lizenzfolge (GPL-3.0): Plugins laufen im selben PHP-Prozess wie Matomo. Nach Sicht der Free Software Foundation ist das in der Regel ein „kombiniertes Werk“ (GPL-FAQ „GPLPlugins“). Solange wir die Software **nur als Dienst betreiben**, geben wir keine Kopie weiter. Dann müssen wir den Quellcode nicht offenlegen (siehe 3.2). Wenn wir die Plugins aber **jemals weitergeben** (an einen Kunden, Partner oder Käufer der Firma), müssen sie unter der GPL stehen. Dann wäre „Alle Rechte vorbehalten“ für diese Teile nicht haltbar.
- Marke: Ein eigenes Theme ist erlaubt. Wir dürfen aber nicht „Matomo“ als Produktnamen nutzen (siehe 3.4).
- Aufwand MVP: grob 30–40 Arbeitstage (KI-gestützt), davon viel Einarbeitung in Matomo-Interna.
- Risiko: mittel bis hoch (Update-Brüche, Lizenzbindung, zweiter Tech-Stack).

### 2.3 Weg B – Matomo als Datensammler plus eigene Waybuild-Analytics-Anwendung daneben (Empfehlung)

Matomo läuft **unverändert** (nur offizielle, kostenlose Matomo-Plugins und Einstellungen, kein eigener Code darin). Daneben läuft unsere eigene Anwendung. Sie spricht mit Matomo nur über die offizielle **Reporting-API** (HTTP) und die **Tracking-API** (HTTP). Die Anwendung enthält Kunden-Struktur, Berichte, Exporte, Logbuch, Crawler-Import, AI-Visibility-Check und MCP-Server.

- Vorteile:
  - Matomo-Updates bleiben einfach: Matomo ist ein fremdes Programm, das wir nur einstellen.
  - Unser Code ist ein **eigenständiges Programm**, das über eine Netzwerk-Schnittstelle mit Matomo spricht. Die GPL erfasst ihn nicht, auch nicht bei einer späteren Weitergabe. Das gilt, solange wir keinen Matomo-Code hineinkopieren. Kommunikation „auf Armlänge“ (Netzwerk, API) gilt nach der GPL-FAQ in der Regel als getrennte Programme („aggregate“, „MereAggregation“).
  - Gleicher Stack wie das CRM (SvelteKit, Node, Postgres). Bausteine und Design können wir teilen.
  - Kunden-Struktur, Kunden-Login und MCP-Rechte bauen wir so, wie wir sie brauchen, mit Postgres Row-Level-Security wie im CRM.
  - Wenn Matomo eines Tages nicht mehr passt, tauschen wir nur den Datensammler.
- Nachteile:
  - Zwei Systeme betreiben (Matomo mit MariaDB, unsere App mit Postgres).
  - Kennzahlen kommen über die API. Für ganz neue Auswertungen müssen wir eventuell eigene Rohdaten-Abfragen bauen.
  - Die Matomo-Oberfläche bleibt für interne Detailanalysen sichtbar, mit Matomo-Namen. Das ist intern unproblematisch.
- Lizenzfolge (GPL-3.0): Wir betreiben Matomo unverändert als Dienst. Wir geben keine Kopie von Matomo weiter, also gibt es keine Pflicht zur Offenlegung. Unser eigener Code ist ein getrenntes Werk und kann proprietär bleiben. Den Matomo-JavaScript-Tracker liefern wir an die Browser der Besucher aus (das ist eine Weitergabe). Er steht aber unter der **BSD-3-Clause-Lizenz** (Kopf von `js/piwik.js`). Wir müssen nur den Lizenzhinweis im Code stehen lassen.
- Aufwand MVP: grob 35–45 Arbeitstage (KI-gestützt).
- Risiko: niedrig bis mittel.

### 2.4 Weg C – Komplett eigene Analyse-Software

Wir bauen Tracker, Datensammlung, Speicherung und Auswertung selbst, zum Beispiel mit Postgres oder ClickHouse und eigenem Tracker-Skript.

- Vorteile: 100 % eigener Code, keine GPL-Frage, keine fremde Marke.
- Nachteile: Wir bauen nach, was Matomo seit über 15 Jahren kann: Geräte- und Browser-Erkennung, Bot-Filter, Kanäle, Archivierung, Opt-out, Kampagnen, Datenschutz-Funktionen. Sicherheit und Pflege liegen allein bei uns.
- Lizenzfolge: keine GPL-Bindung. Bei Bibliotheken mit permissiver Lizenz (MIT, BSD, Apache) nur Lizenzhinweise.
- Aufwand bis zum gleichen Stand wie Weg B: grob 4–6 Monate.
- Risiko: hoch (Zeit, Datenqualität, Fehler in der Zählung).

### 2.5 Vergleich

| Kriterium | A: Plugins im Matomo | B: Matomo + eigene App (Empfehlung) | C: alles selbst |
|---|---|---|---|
| Zeit bis MVP | mittel | mittel | lang |
| Matomo-Updates | aufwendig | einfach | entfällt |
| Schutz unseres Codes | nur solange keine Weitergabe | stark (getrenntes Programm) | stark |
| Tech-Stack | PHP (neu) | TypeScript (wie CRM) | TypeScript |
| Kunden-Struktur und Login | schwer | einfach | einfach |
| MCP mit Rechten pro Kunde | schwer | einfach | einfach |
| Datenqualität | Matomo | Matomo | eigenes Risiko |
| Abhängigkeit von Matomo | hoch | mittel (austauschbar) | keine |

### 2.6 Empfehlung

**Weg B.** Er erfüllt Cans Wunsch „Matomo nutzen und das Fehlende selbst bauen“. Er hält unseren Code rechtlich sauber getrennt und passt zu unserem CRM-Stack. Matomo bleibt unverändert und lässt sich leicht aktualisieren. Wenn wir später doch etwas tief in Matomo brauchen, schreiben wir ein kleines Plugin und veröffentlichen es dann bewusst unter der GPL. Es darf aber nichts enthalten, was unser Geschäftsgeheimnis ist.

---

## 3. Lizenz und Schutz unseres Codes

Hinweis: Dieser Abschnitt ist eine technische Einordnung, **keine Rechtsberatung**. Vor dem Start des Kundenbetriebs sollte eine Anwältin oder ein Anwalt für IT-Recht die Punkte in 3.6 prüfen.

### 3.1 Lizenz von Matomo (geprüft am 06.11.2026)

- `LICENSE` im Repo matomo-org/matomo (Zweig 5.x-dev): GNU General Public License **Version 3** vom 29.06.2007.
- `composer.json`, Feld `license`: **„GPL-3.0+“**, also GPL-3.0 oder später.
- JavaScript-Tracker `js/piwik.js` (matomo.js): **BSD-3-Clause** (Kopfzeile `@license … BSD-3 Clause`, siehe `js/LICENSE.txt`).
- Plugin `McpServer`: GPL v3 oder später, kostenlos (plugins.matomo.org/McpServer).
- **Matomo ist GPL, nicht AGPL.** Die AGPL hat eine zusätzliche Klausel (§ 13 „Remote Network Interaction“). Sie verlangt den Quellcode auch dann, wenn Nutzer das Programm nur über ein Netzwerk benutzen. Diese Klausel gibt es in der GPL-3.0 nicht.

### 3.2 Was die GPL-3.0 bei reinem Dienst-Betrieb bedeutet

GPL-3.0, Abschnitt 0: *„To ‘convey’ a work means any kind of propagation that enables other parties to make or receive copies. Mere interaction with a user through a computer network, with no transfer of a copy, is not conveying.“*

Auf Deutsch: Wer nur einen Dienst über das Netz anbietet und keine Kopie herausgibt, „überträgt“ (conveys) das Programm nicht. Die Pflichten der GPL (Quellcode mitliefern, gleiche Lizenz) gelten nur beim Übertragen.

| Situation | GPL-Pflicht? |
|---|---|
| Wir betreiben Matomo (auch verändert) auf unserem Server, Kunden sehen nur Berichte oder eine Weboberfläche | Nein |
| Wir liefern den Matomo-JS-Tracker an Besucher-Browser aus | BSD-3-Clause: nur Lizenzhinweis behalten |
| Wir geben Matomo oder Matomo-Plugins an einen Kunden oder Partner weiter (Download, Installation beim Kunden) | Ja: Quellcode und GPL für Matomo und für damit kombinierte Plugins |
| Unsere eigene App (Weg B) spricht nur per HTTP-API mit Matomo | Nein, getrenntes Programm, auch bei späterer Weitergabe |
| Wir kopieren Matomo-Quellcode in unsere App | Ja, dann wird dieser Teil GPL-pflichtig. **Darum: nie Matomo-Code in unser Repo kopieren.** |

### 3.3 Schutz unseres eigenen Codes

1. **Lizenz „Alle Rechte vorbehalten“** (proprietär) für unser Repo. Die Datei `LICENSE` liegt bei. Ohne schriftliche Erlaubnis der Waybuild UG ist jede Nutzung verboten, auch gegen Gebühr nur mit Vertrag. Das erfüllt Cans Vorgabe V8 am direktesten.
2. **Nutzung nur als Dienst.** Kunden bekommen keine Software, sondern eine Leistung nach unseren AGB und dem Wegweiser- oder Wahrzeichen-Vertrag. Ein späterer Kunden-Login wird über Nutzungsbedingungen geregelt (Zugang nicht übertragbar, kein Auslesen per Bot, kein Nachbau).
3. **Privates Repo**, Zugang nur Can, Jamil und unsere Agenten. Geheimnisse (API-Schlüssel) nie im Repo.
4. **Rechtekette klären.** Urheber sind die Menschen, die den Code schreiben. Bei Arbeitnehmern gehen die Rechte am Programm nach § 69b UrhG an den Arbeitgeber (Jamil als Minijobber: im Rahmen seiner Aufgaben). Can ist Geschäftsführer. Dafür und für freie Mitarbeit braucht es eine **schriftliche Übertragung der Nutzungsrechte auf die UG**.
5. **KI-erzeugter Code.** Code, den eine KI ohne prägende menschliche Gestaltung erzeugt, ist in Deutschland eventuell nicht urheberrechtlich geschützt (§ 2 Abs. 2 UrhG: „persönliche geistige Schöpfung“). Zweiter Schutz deshalb: **Geschäftsgeheimnis** nach dem GeschGehG. Das braucht „angemessene Geheimhaltungsmaßnahmen“: privates Repo, Zugriffsrechte, Vertraulichkeit in Verträgen, Protokoll, wer Zugang hat. Diese Maßnahmen setzen wir bewusst um und dokumentieren sie.
6. **„Neueste Standards“ bei Lizenzen.** Es gibt moderne „source-available“-Lizenzen, die den Code zeigen, aber kommerzielle Konkurrenz verbieten: Functional Source License (FSL-1.1, seit 2023), Business Source License (BUSL-1.1), Elastic License 2.0, PolyForm (z. B. PolyForm Shield oder Noncommercial). Die sind nur sinnvoll, wenn wir den Code **zeigen** wollen. Weil wir ihn privat halten, ist „Alle Rechte vorbehalten“ einfacher und strenger. Empfehlung: jetzt „Alle Rechte vorbehalten“. Falls wir später Teile veröffentlichen wollen, ist FSL-1.1 eine gute Wahl.
7. **Dritt-Komponenten** behalten ihre Lizenzen. Wir führen eine Datei `THIRD-PARTY-NOTICES` mit allen Paketen und Lizenzen (automatisch erzeugt beim Build). Kein Paket mit AGPL oder GPL in unserer eigenen App ohne bewusste Entscheidung.

### 3.4 Marke „Matomo“ und White-Label

Quelle: Matomo Trademark Policy (matomo.org/trademark, abgerufen am 06.11.2026). Kurzfassung:

- **Kommerzielle Nutzung der Marke** braucht eine Lizenz von Matomo. Das gilt auch für Software mit kommerziellem Zweck, die auf Matomo aufbaut, und für zugehörige Dienste.
- Namen wie „Matomo Analytics“, „MyMatomo“ oder „MatomoXYZ“ werden praktisch nie erlaubt.
- Bei stark veränderten Versionen ist der Hinweis „based on Matomo“ oder „derived from Matomo“ als Beschreibung vorgesehen, nicht als Produktname.
- White-Label erwähnt die Policy nicht ausdrücklich. Matomo verkauft selbst ein kostenpflichtiges White-Label-Plugin.

Für uns heißt das:

1. Produktname, Logo, Domain und Werbung enthalten **kein „Matomo“**.
2. Unsere Oberfläche (Weg B) ist unser eigenes Programm und braucht kein Matomo-Logo. Die interne Matomo-Oberfläche lassen wir unverändert (nur Team-Zugang).
3. Sachliche Nennung als eingesetzte Software, zum Beispiel in der Datenschutzerklärung, im AV-Vertrag und in den Lizenzhinweisen („Zur Datenerhebung nutzen wir die Open-Source-Software Matomo, GPL-3.0“). Eine solche beschreibende Nennung ist markenrechtlich normalerweise zulässig (§ 23 MarkenG). Der Anwalt soll das bestätigen.
4. Wir werben nicht mit „Powered by Matomo“, solange wir keine Markenlizenz haben.

### 3.5 Unser eigener Name

- „Analytics“ ist ein beschreibendes Wort und kaum schützbar. Schützbar ist der Teil „Waybuild“.
- Vor der Veröffentlichung: Recherche bei DPMA und EUIPO (Klassen 9, 35, 42), ob „Waybuild“ frei ist. Dann eventuell die Wortmarke „Waybuild“ anmelden.
- Schreibweise: „Waybuild Analytics“ (englisch üblich, Mehrzahl) oder „Waybuild Analytic“ (wie Can geschrieben hat, Repo-Name). Jamil hat nach dem Namen gefragt. Entscheidung siehe D1.

### 3.6 Prüfliste für die Anwältin oder den Anwalt

1. Passt unsere Einordnung GPL-3.0 und Dienst-Betrieb und ist die Trennung in Weg B tragfähig?
2. Darf „Matomo“ beschreibend in Datenschutzerklärung, AV-Vertrag und Lizenzhinweisen stehen?
3. Ist der JS-Tracker ohne Cookies nach § 25 TDDDG ohne Einwilligung zulässig? Oder brauchen wir den strengen Modus „nur Server-Logs“ (siehe 4.8)?
4. Auftragsverarbeitung: AV-Vertrag mit jedem Kunden, technische und organisatorische Maßnahmen (TOM), Liste der Unterauftragsverarbeiter.
5. Server-Logs mit Bot-Daten: Rechtsgrundlage und Aufbewahrung.
6. Rechteübertragung von Can und Jamil auf die UG, Schutz von KI-erzeugtem Code (Geschäftsgeheimnis).
7. Nutzungsbedingungen für den späteren Kunden-Login.

---

## 4. Funktionsblöcke

### 4.0 Übersicht und Priorität

| Block | MVP (Stufe 1) | V2 (Stufe 2) | Später |
|---|---|---|---|
| 4.1 Kunden-Struktur | Kunde → Websites, Team-Login, Kunden-Login vorhanden und ausgeschaltet | Kunden-Login einschalten (pro Kunde), Rechte „nur lesen“ | Agentur-Mandanten, Selbstbedienung |
| 4.2 Kern-Kennzahlen und Ziele | Besuche, Seiten, Quellen, Geräte, Region, Ziele (Anfrage, Buchen, Anruf, Mail, WhatsApp) | Formular-Analyse (Abbruch), Ladezeiten-Trend | Heatmaps nur mit Einwilligung |
| 4.3 Berichte und Exporte | Monats-PDF (Entwurf → Freigabe), CSV/XLSX/JSON, Maßnahmen-Logbuch mit Vorher-nachher | Automatische Verbesserungs-Vorschläge (KI-Entwurf, Mensch prüft), Warnungen bei Einbrüchen | Kunden-Dashboard live |
| 4.4 KI-Crawler | Import der Hoster-Logs (Apache/Nginx) für Websites mit Logs, Erkennung plus IP-Prüfung | Logging-Snippet beim Hoster, Edge-Anbindung (z. B. Cloudflare) | Eigener Reverse-Proxy |
| 4.5 KI-Referrer und Begriffe | Matomo-Kanal „AI Assistants“, utm_source-Regeln, Google Search Console | Bing Webmaster Tools (KI-Performance, Export), Schätzung „KI-vermittelte Besuche“ | weitere Quellen, sobald APIs da sind |
| 4.6 AI-Visibility-Check | Test-Fragen pro Kunde, monatlich, Claude und ChatGPT (OpenAI) | plus Gemini und Perplexity, Wettbewerber-Vergleich | weitere Modelle (Mistral, Meta AI), wöchentlich |
| 4.7 MCP-Server | Nur lesen, Token pro Kunde und Team-Token, Bericht-Entwurf anstoßen | OAuth 2.1 für Connectoren in claude.ai und ChatGPT | Schreib-Werkzeuge für Logbuch |
| 4.8 Datenschutz | Cookieless, IP-Kürzung, Opt-out, Löschfristen, AV-Vorlage | Strenger Modus „nur Server“ pro Website | – |

### 4.1 Kunden-Struktur

- **Kunde**: Name, Paket (Fundament, Wegweiser, Wahrzeichen), Vertragsbeginn, Ansprechperson, Status (aktiv, pausiert, beendet). Optional Verknüpfung mit dem CRM (später, über eine ID).
- **Website**: Domain, Kunde, Matomo-Site-ID, Hoster und Log-Zugang (Typ, nicht das Passwort im Klartext), Tracking-Modus (Standard oder Streng), Ziele, Prompt-Set, Search-Console-Property.
- **Benutzer und Rollen**: Team (Can, Jamil: alles), Kunde-Lesen (nur eigene Websites; in Stufe 1 **ausgeschaltet**: Konto kann angelegt, aber nicht angemeldet werden; Schalter pro Kunde).
- **Mandantentrennung** in Postgres mit Row-Level-Security wie im CRM. Jede Abfrage läuft im Kontext eines Kunden oder des Teams.
- Matomo-Zugang: ein technischer Matomo-Benutzer mit Leserechten auf alle Sites. Sein Token kennt nur der Server, nie ein Kunde oder ein MCP-Client.

### 4.2 Kern-Kennzahlen und Ziele

Kennzahlen (aus der Matomo-Reporting-API):

- Besuche, Seitenaufrufe, Einstiegsseiten, Top-Seiten, durchschnittliche Dauer.
- Quellen und Kanäle: Suchmaschine, direkt, Social Media, Verweise, Kampagnen, **KI-Assistenten**.
- Geräte (Handy, Tablet, PC), Region (aus gekürzter IP, bis Stadt).
- Ladezeit (Matomo-Plugin „Performance“).
- Hinweis: Ohne Cookies erkennt Matomo wiederkehrende Besucher nur innerhalb eines Tages. „Eindeutige Besucher“ ist deshalb eine Schätzung. Das steht im Bericht als Fußnote.

Ziele (Matomo-Goals, pro Website eingerichtet):

| Ziel | Auslöser |
|---|---|
| Anfrage gesendet | Danke-Seite aufgerufen oder JS-Ereignis nach erfolgreichem Senden |
| Buchen geklickt / Termin gebucht | Klick auf Buchen-Knopf; später Bestätigung aus dem Buchungs-Widget (Bauwelt Terminbuchung) |
| Anruf geklickt | Klick auf `tel:`-Link |
| Mail geklickt | Klick auf `mailto:`-Link |
| WhatsApp geklickt | Klick auf WhatsApp-Link |

Für jede Website gibt es eine Konversionsrate: Ziele geteilt durch Besuche.

### 4.3 Berichte, Exporte, Vorher-nachher

**Monatsbericht (PDF):**

- Wird am 2. Kalendertag um 06:00 für den Vormonat erstellt. Bis 08:00 ist er fertig.
- Inhalt in leichter Sprache, Waybuild-Design, großzügiger Zeilenabstand:
  1. Das Wichtigste in 3 Sätzen.
  2. Besucher und Anfragen (mit Vormonat und Vorjahresmonat, sobald es Daten gibt).
  3. Woher die Besucher kommen, auch KI-Assistenten.
  4. Suchbegriffe aus Google (Search Console), Top 10.
  5. KI-Sichtbarkeit: welche KI-Bots die Seite gelesen haben, Ergebnis des AI-Visibility-Checks.
  6. Was wir verbessert haben (aus dem Logbuch) und was es gebracht hat.
  7. Was wir als Nächstes vorschlagen.
- Ablauf: Status „Entwurf“ → Team prüft und ergänzt → „freigegeben“. Ablage in Nextcloud im Kundenordner. Versand an den Kunden nur von Hand und nur nach Cans „ja“ (wie bei allen externen Mails).
- Fehlen Daten (z. B. Matomo war ausgefallen), steht im Bericht deutlich „unvollständig“. Der Bericht wird dann nicht freigegeben, bis jemand entscheidet.
- Technik: HTML-Vorlage → PDF mit Chromium (Playwright). Schriften liegen im Projekt.

**Exporte:** CSV, XLSX und JSON für jeden Zeitraum und jede Website. Gleiche Rechenwege wie im Bericht (ein gemeinsamer Kennzahlen-Baustein). JSON hat ein festes, versioniertes Schema, damit KI-Agenten es zuverlässig lesen.

**Maßnahmen-Logbuch und Vorher-nachher:**

- Eintrag: Datum, Website, Maßnahme (z. B. „Startseite neue Überschrift“), Kategorie (Text, Design, Technik, SEO, KI/GEO), erwartete Wirkung, beobachtete Kennzahl.
- Automatischer Vergleich: 28 Tage vor und 28 Tage nach dem Datum, gleiche Wochentage. Kennzahlen: Besuche, Ziele, Konversionsrate, KI-Besuche, KI-Crawler-Abrufe.
- Ehrlichkeit: Bei weniger als 100 Besuchen pro Zeitraum steht „zu wenig Daten für eine sichere Aussage“. Saison und Zufall werden erwähnt. Es ist ein Hinweis, kein Beweis.

### 4.4 KI-Crawler-Erkennung (ohne JavaScript)

KI-Crawler führen meist kein JavaScript aus. Der Matomo-Tracker sieht sie also nicht. Wir brauchen die Anfragen, die beim Webserver ankommen.

**Bot-Liste (Stand 06.11.2026, aus den Herstellerseiten; als Datendatei im Code, monatlich prüfen):**

| User-Agent | Betreiber | Zweck | robots.txt | Prüfung der Echtheit | Matomo-Kern erkennt |
|---|---|---|---|---|---|
| GPTBot | OpenAI | Training | ja | openai.com/gptbot.json | nein |
| OAI-SearchBot | OpenAI | Suchindex ChatGPT | ja | openai.com/searchbot.json | nein |
| ChatGPT-User | OpenAI | Abruf für eine Nutzerfrage | evtl. nicht | openai.com/chatgpt-user.json | ja |
| OAI-AdsBot | OpenAI | Prüfung von Anzeigen-Zielseiten | k. A. | openai.com/adsbot.json | nein |
| ClaudeBot | Anthropic | Training | ja | claude.com/crawling/bots.json | nein |
| Claude-SearchBot | Anthropic | Suche | ja | claude.com/crawling/bots.json | nein |
| Claude-User | Anthropic | Abruf für eine Nutzerfrage | ja | claude.com/crawling/bots.json | ja |
| PerplexityBot | Perplexity | Suchindex | ja | perplexity.ai/perplexitybot.json | nein |
| Perplexity-User | Perplexity | Abruf für eine Nutzerfrage | meist nicht | perplexity.ai/perplexity-user.json | ja |
| Googlebot | Google | Google-Suche inkl. AI Overviews und AI Mode | ja | Google-IP-Listen, Reverse-DNS googlebot.com | nein |
| Google-CloudVertexBot, GoogleOther | Google | Vertex-AI-Agenten, sonstige Abrufe | ja | common-crawlers.json | nein |
| Gemini-Deep-Research, Google-NotebookLM | Google | Abruf für eine Nutzeranfrage | k. A. | Google-IP-Listen | ja |
| Google-Extended | Google | **nur robots.txt-Token, kein eigener User-Agent** | – | im Log nicht messbar | – |
| Bingbot | Microsoft | Bing-Index, Grundlage für Copilot | ja | Reverse-DNS search.msn.com, Bing-IP-Liste | nein |
| Applebot | Apple | Siri, Spotlight, Safari; Daten auch für Training | ja | applebot.json, Reverse-DNS applebot.apple.com | nein |
| Applebot-Extended | Apple | **nur robots.txt-Token** | – | im Log nicht messbar | – |
| meta-externalagent | Meta | Training und Index | ja | Reverse-DNS/IP laut Meta prüfen | nein |
| meta-externalfetcher | Meta | Abruf für eine Nutzeranfrage | evtl. nicht | dto. | nein |
| meta-webindexer | Meta | Meta-AI-Suche | ja | dto. | nein |
| CCBot | Common Crawl | offener Datensatz, oft für Training genutzt | ja | Angaben von Common Crawl prüfen | nein |
| MistralAI-User | Mistral | Abruf für eine Nutzerfrage (Le Chat) | k. A. | prüfen | ja |
| Amazonbot, Bytespider, DuckAssistBot, cohere-ai, YouBot, Diffbot, PetalBot | verschiedene | Suche oder Training | unterschiedlich | **vor der Umsetzung an den Herstellerseiten prüfen** | nein |

Einteilung in drei Gruppen: **Training**, **Suchindex**, **Nutzer-Abruf**. Die Gruppe „Nutzer-Abruf“ ist am wertvollsten: Ein Mensch hat gerade eine KI etwas gefragt, und die KI hat dafür unsere Seite geöffnet.

User-Agents lassen sich fälschen. Deshalb prüfen wir die IP-Adresse gegen die veröffentlichten Listen oder per Reverse-DNS und markieren jeden Treffer als „geprüft“ oder „nicht geprüft“.

**Wege, an die Server-Anfragen zu kommen:**

| Weg | Wie | Vorteil | Nachteil | Stufe |
|---|---|---|---|---|
| 1. Hoster-Logs importieren | Täglicher Abruf der Access-Logs per SFTP oder Hoster-Schnittstelle (IONOS, ALL-INKL). Unser Log-Sammler filtert Bots heraus. | Nichts an der Website ändern | Nicht jeder Hoster liefert Logs; IPs manchmal schon gekürzt (dann keine IP-Prüfung); Verzögerung bis 1 Tag | MVP |
| 2. Logging-Snippet beim Hoster | Bei PHP-Hostern: Eine `.htaccess`-Regel leitet **nur Anfragen mit Bot-User-Agent** an ein kleines PHP-Skript. Das Skript meldet die Anfrage an unseren Ingest-Endpunkt und liefert die Seite normal aus. Menschen laufen nie durch das Skript. | Echtzeit, volle Kontrolle | Etwas Technik auf der Kundenseite; muss gut getestet werden | V2 |
| 3. Edge (Cloudflare Worker, CloudFront) | Offizielle Matomo-Anbindung für Chatbot-Abrufe, von uns erweitert um Crawler | Sehr zuverlässig, kein Eingriff in den Hoster | DNS über den Edge-Anbieter, US-Anbieter, AV-Vertrag nötig | V2 (optional) |
| 4. Eigener Reverse-Proxy | Unser Server steht vor der Kundenseite | Alles in eigener Hand | Unser Server wird zum kritischen Punkt für die Websites | später |

Wichtig: **GitHub Pages liefert keine Logs** und erlaubt kein Snippet. Websites, die dort live laufen, bekommen keine Crawler-Messung (siehe D7). Bauwelt (IONOS, Apache) eignet sich als erste Test-Website. Vorher prüfen wir, welche Logs IONOS liefert und ob die IPs schon gekürzt sind.

Datenfluss: Log-Zeilen von **Menschen** verwirft der Log-Sammler sofort im Speicher. Gespeichert werden nur Bot-Zeilen. Chatbot-Abrufe (ChatGPT-User usw.) geben wir zusätzlich an Matomo weiter (`recMode=1`). Dann füllen sich auch die eingebauten Matomo-Berichte „AI Chatbots“. Crawler, die Matomo nicht kennt, speichern wir in unserer Datenbank.

Auswertung: pro Bot und Website Abrufe pro Tag, abgerufene Seiten, Fehlerseiten (404/5xx), zuletzt gesehen, Seiten, die nie von KI gelesen werden. Dazu ein Abgleich mit der robots.txt der Website: „Bot X ist erlaubt / gesperrt“. Die Entscheidung über die robots.txt bleibt bei Jamil und Can (Jamil will keine pauschale Freigabe für KI-Crawler).

### 4.5 KI-Referrer-Kanal und „Begriffe sammeln“

**KI-Referrer-Kanal:** Den liefert Matomo ab 5.5 selbst (ChatGPT, Copilot, Gemini, Claude, Le Chat, Meta AI, iAsk, Perplexity). Wir ergänzen:

- Regeln für Kampagnen-Parameter: `utm_source=chatgpt.com` (ChatGPT hängt das oft an Links an), `utm_source=perplexity`, `copilot` usw. → Kanal „KI-Assistent“.
- Liste der KI-Domains als Datendatei (chatgpt.com, chat.openai.com, perplexity.ai, gemini.google.com, copilot.microsoft.com, claude.ai, chat.mistral.ai, meta.ai, …).
- Schätzung „KI-vermittelte Besuche“ (V2): Ein Nutzer-Abruf (z. B. ChatGPT-User auf Seite X) und kurz danach (bis etwa 60 Sekunden) ein Besuch, der auf Seite X einsteigt. Das ist ein Hinweis, kein Beweis, und wird auch so beschriftet.

**„Begriffe sammeln“ – was ehrlich geht und was nicht:**

| Geht | Quelle | Was wir bekommen |
|---|---|---|
| Ja | Referrer und utm_source | Welche KI geschickt hat, auf welcher Seite der Besuch eingestiegen ist. Die Einstiegsseite zeigt das Thema. |
| Ja | KI-Crawler und Nutzer-Abrufe | Welche Seiten von welcher KI gelesen werden und wann. |
| Ja | Google Search Console (API) | Echte Suchbegriffe aus der Google-Suche mit Klicks, Impressionen und Position. AI Overviews und AI Mode zählen dort mit. Seit 03.06.2026 gibt es außerdem einen Beta-Bericht „Search Generative AI“ (nur Impressionen; eine API dafür ist nicht bestätigt). |
| Ja, mit Handarbeit | Bing Webmaster Tools, Bericht „AI Performance“ (seit Februar 2026, Vorschau) | **Grounding Queries**: Themen-Suchanfragen, mit denen Copilot und Bing-KI unsere Seiten finden, plus zitierte Seiten. Nur als Export, API laut Microsoft „auf der Liste“. |
| Ja | AI-Visibility-Check (4.6) | Mit welchen Begriffen und Fragen die Firma in KI-Antworten genannt wird und mit welchen nicht. |
| Ja | Suche auf der Website (Matomo „Site Search“) | Begriffe, die Besucher auf der Website eintippen, falls es dort eine Suche gibt. |
| **Nein** | ChatGPT, Claude, Perplexity, Gemini, Copilot | Die **echte Frage des Nutzers** wird nicht an die Website übergeben. Kein Anbieter liefert sie. |
| **Nein** | ChatGPT-App und andere Apps | Viele Besuche aus Apps kommen ohne Referrer und landen bei „Direkt“. Es gibt eine Dunkelziffer. |
| **Nein** | KI-Antworten allgemein | Antworten sind persönlich und schwanken. Es gibt keine festen „Rankings“ wie bei Google. Wir messen Stichproben und Trends. |

### 4.6 AI-Visibility-Check (regelmäßige Test-Fragen an die großen Modelle)

**Ziel:** Jeden Monat prüfen, ob und wie die Firma eines Kunden in KI-Antworten vorkommt.

**Prompt-Set pro Kunde (10–30 Fragen):** Wir bauen es aus Branche × Ort × Leistung × Absicht, dazu Fragen nach der Marke. Beispiele:

- „Wer macht Badsanierung in Norderstedt?“
- „Guter Fliesenleger im Hamburger Norden, wen empfiehlst du?“
- „Website für Handwerker mit monatlichem Abo, welche Anbieter gibt es in Schleswig-Holstein?“
- „Was ist Bauwelt Handwerk?“

Die Fragen legt das Team fest. Sie bleiben über Monate gleich, damit Trends vergleichbar sind.

**Ablauf (monatlich, z. B. am 25.):**

1. Jede Frage geht an jedes Modell mit **Websuche** und Standort Deutschland, 3 Wiederholungen (Antworten schwanken).
2. Wir speichern die Antwort, die zitierten Quellen (URLs) und Uhrzeit, Modell und Version.
3. Ein günstiges Modell zieht mit festem Ausgabe-Schema (strukturierte Ausgabe) heraus: Firma genannt ja/nein, Position in der Aufzählung, eigene Domain zitiert ja/nein, genannte Wettbewerber, **Begriffe**, mit denen die Firma beschrieben wird, Tonalität.
4. Kennzahlen: **Nennungsrate** pro Modell und gesamt, **Zitierrate** der eigenen Domain, Top-Begriffe, Lücken (Fragen ohne Nennung).
5. Der Trend erscheint im Monatsbericht und im Vorher-nachher zum Logbuch.

**Anbieter, Kosten und Bedingungen (Stand 06.11.2026, Preise in US-Dollar, netto):**

| Modell | Weg | Kosten | Quelle | Bemerkung |
|---|---|---|---|---|
| Claude | Anthropic API mit Web-Search-Tool | 10 $ pro 1.000 Suchen plus Tokens; Claude Haiku 5.5: 0,10 $ / 0,50 $ pro 1 Mio. Tokens (Eingabe/Ausgabe), Claude Sonnet 5.5: 2 $ / 10 $ | offizielle Preisseite Anthropic | Suchergebnisse zählen als Eingabe-Tokens |
| ChatGPT | OpenAI Responses API mit Tool `web_search` | etwa 10 $ pro 1.000 Tool-Aufrufe plus Tokens | Sekundärquellen, **vor Start auf openai.com prüfen** | Preis wurde 2026 laut Berichten von 25 $ auf 10 $ gesenkt |
| Gemini | Gemini API mit „Grounding with Google Search“ | Gemini 3: 5.000 Suchanfragen pro Monat frei, danach 14 $ pro 1.000 | Sekundärquellen, **prüfen** | ältere Modelle wurden pro Prompt abgerechnet |
| Perplexity | Sonar API | Sonar: 5–12 $ pro 1.000 Anfragen (je nach Suchtiefe) plus 1 $ pro 1 Mio. Tokens | Sekundärquellen, **prüfen** | Berichte über Umstellung auf eine „Agent API“; Stand prüfen |
| Copilot | **keine öffentliche Copilot-API** | – | Microsoft hat die Bing Search APIs am 11.08.2025 eingestellt | Ersatz „Grounding with Bing Search“ (Azure, gemeldet 14–35 $ pro 1.000; das Microsoft-Datenschutz-Addendum gilt dafür laut Microsoft nicht). Empfehlung: kein API-Check, stattdessen Bing-Webmaster-Export (4.5). |

**Beispielrechnung pro Kunde und Monat:** 20 Fragen × 3 Wiederholungen × 4 Modelle = 240 Abfragen. Pro Abfrage etwa 1–5 Cent (Suchgebühr plus Tokens) → **etwa 3–10 $ pro Kunde und Monat**. Mit nur Claude und ChatGPT im MVP etwa die Hälfte. Die Auswertung mit Haiku kostet weniger als 0,10 $. Ein **hartes Budget pro Kunde** in der App stoppt die Abfragen, wenn die Grenze erreicht ist (Vorschlag 10 € netto).

**Regeln:**

- Nur offizielle APIs. Kein automatisches Abfragen der Verbraucher-Oberflächen (chatgpt.com usw.). Das verbieten die Nutzungsbedingungen.
- Ehrlich im Bericht: API-Antworten sind nicht identisch mit der App, die ein Kunde nutzt (anderes Systemprompt, keine Personalisierung, anderer Standort). Wir messen Stichproben und Trends.
- In den Fragen stehen nur Firmen-, Marken- und Ortsangaben, keine Besucherdaten.
- API-Schlüssel liegen nur auf dem Server (nur für den Dienst lesbar), nie im Repo und nie im Chat.
- Nutzungsbedingungen der Anbieter vor dem Start prüfen: Daten aus API-Nutzung werden laut Anbietern standardmäßig nicht fürs Training genutzt. Das prüfen wir je Anbieter und halten es fest.

### 4.7 MCP-Server

**Zweck:** Claude (Claude Code, später claude.ai), ChatGPT und unsere eigenen Agenten können Zahlen lesen und Berichte anstoßen, ohne Matomo direkt zu sehen.

**Technik:** Eigener MCP-Server in unserer App, Transport „Streamable HTTP“ nach der aktuellen MCP-Spezifikation (modelcontextprotocol.io, Revision 2026-07-28; bei der Umsetzung den genauen Stand prüfen). Das Matomo-Plugin `McpServer` geben wir **nicht** nach außen frei, weil es auf Wunsch rohe API-Methoden ausführt.

**Werkzeuge (Tools):**

| Tool | Art | Beschreibung |
|---|---|---|
| `kunden_liste` | lesen | Kunden, die das Token sehen darf |
| `websites_liste` | lesen | Websites eines Kunden |
| `besucher_kennzahlen` | lesen | Besuche, Seiten, Quellen, Geräte für Zeitraum und Vergleichszeitraum |
| `ziele_konversionen` | lesen | Anfragen, Buchen, Anrufe, Konversionsrate |
| `ki_sichtbarkeit` | lesen | KI-Crawler, KI-Besuche und Ergebnis des AI-Visibility-Checks für einen Monat |
| `suchbegriffe` | lesen | Top-Begriffe aus der Search Console |
| `massnahmen_logbuch` | lesen | Maßnahmen und ihr Vorher-nachher |
| `bericht_erzeugen` | schreiben (begrenzt) | Erstellt nur einen **Entwurf** des Monatsberichts. Freigeben und Versenden geht nie über MCP. |

Ressourcen: fertige Berichte (PDF und JSON), ein Glossar der Kennzahlen. Prompts: „Monatsanalyse“, „Verbesserungs-Vorschläge“.

**Sicherheit:**

- **Token pro Kunde** (sieht nur diesen Kunden) und **Team-Token** (sieht alles). Token mit Ablaufdatum (Vorschlag 90 Tage), jederzeit widerrufbar, in der Datenbank nur als Hash gespeichert.
- Rechte pro Token: `lesen` und optional `bericht_entwurf`.
- Die Trennung der Kunden erzwingt die Datenbank (Row-Level-Security), nicht nur der Code. Ein automatischer Test prüft: Token von Kunde A bekommt nie Daten von Kunde B.
- Begrenzung der Aufrufe pro Minute, Protokoll jedes Aufrufs (wer, wann, welches Tool, kein Inhalt mit Geheimnissen).
- Schutz vor Prompt-Injection: Seitentitel, KI-Antworten und Bot-Namen sind fremde Daten. Die Tool-Ausgaben kennzeichnen sie als Daten. Kein Tool führt Befehle aus Textfeldern aus.
- V2: Anmeldung über OAuth 2.1 mit Protected Resource Metadata (wie in der MCP-Spezifikation verlangt). Dann funktionieren Connectoren in claude.ai und ChatGPT sauber, auch für Kunden-Logins.

### 4.8 Datenschutz-Design

**Tracking-Modi pro Website:**

| Modus | Was passiert | Rechtliche Lage (zu prüfen) |
|---|---|---|
| **Standard** | Matomo-JS ohne Cookies (`disableCookies`), ohne Browser-Merkmale (`disableBrowserFeatureDetection`), keine User-ID, IP auf 2 Bytes gekürzt | Datenverarbeitung: Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse). **Restrisiko:** Das Skript liest Informationen aus dem Endgerät (z. B. Bildschirmgröße, Sprache). Ob das nach § 25 TDDDG ohne Einwilligung erlaubt ist, ist umstritten. Anwalt prüfen. |
| **Streng** | Kein Skript im Browser. Messung nur über Server-Logs oder serverseitige Ereignisse (z. B. Formular gesendet → Server meldet an Matomo) | Kein Zugriff auf das Endgerät, § 25 TDDDG greift nicht. Weniger Daten (keine Geräte-Details, kein Klick-Tracking ohne Server). |

**Weitere Regeln:**

- IP-Kürzung auf 2 Bytes in Matomo. Volle IPs werden nie gespeichert.
- Opt-out: Matomo-Opt-out-Baustein in der Datenschutzerklärung jeder Website. „Do Not Track“ und „Global Privacy Control“ werden beachtet.
- Keine Heatmaps, keine Sitzungsaufzeichnung, kein Fingerprinting.
- **Aufbewahrung (Vorschlag):** Rohdaten der Besuche 6 Monate, zusammengefasste Berichte 25 Monate (24-Monats-Vertrag plus Vorjahresvergleich). Bot-Rohdaten 90 Tage, zusammengefasst 25 Monate. KI-Check-Antworten 25 Monate. Menschliche Zeilen aus Server-Logs: **nicht speichern**, sofort verwerfen.
- **Server-Logs und Bots, Rechtsgrundlage:** Bots von Firmen-Rechenzentren sind meist keine personenbezogenen Daten. Die Logs enthalten aber auch Menschen. Deshalb: Art. 6 Abs. 1 lit. f DSGVO (Betrieb, Sicherheit, Statistik), Datenminimierung beim Import (nur Bot-Zeilen, IP nur zur Echtheitsprüfung, danach gekürzt).
- **AV-Vertrag:** Für Kundenwebsites sind wir Auftragsverarbeiter (Art. 28 DSGVO). Jeder Kunde bekommt einen AV-Vertrag mit TOM und der Liste der Unterauftragsverarbeiter (Server-Hoster, Backup-Speicher). Die KI-Anbieter im AI-Visibility-Check bekommen keine Besucherdaten. Sie sind deshalb für Besucherdaten keine Unterauftragsverarbeiter. Wir nennen sie trotzdem in unserem Verzeichnis.
- Textbaustein für die Datenschutzerklärung der Kundenseiten (später mit dem Datenschutz-Skill und dem DSGVO-Auditor prüfen).
- Server, Backups und Datenbanken in Deutschland oder der EU.

---

## 5. Architektur

### 5.1 Komponenten

| Nr. | Komponente | Aufgabe | Schnittstelle | Hängt ab von |
|---|---|---|---|---|
| K1 | Tracker | Seitenaufrufe und Ziele aus dem Browser (Modus Standard) oder vom Server (Modus Streng) | HTTP an Matomo `matomo.php` | K2 |
| K2 | Matomo (unverändert, GPL) | Daten sammeln, archivieren, Reporting-API, interne Oberfläche | Tracking-API, Reporting-API | MariaDB |
| K3 | WA-Kern (eigene App) | Kunden, Websites, Ziele, Logbuch, Benutzer, Rollen, Oberfläche | Web-UI, interne Module | Postgres |
| K4 | Kennzahlen-Baustein | Ein Ort für alle Rechenwege (Bericht, Export, MCP nutzen ihn) | TypeScript-Modul | K2 (API), K5, K6, GSC |
| K5 | Crawler-Ingest | Hoster-Logs abholen, Bots erkennen und prüfen, speichern; Chatbot-Abrufe an Matomo weitergeben | SFTP/HTTP rein, Postgres, Matomo-Tracking-API | Bot-Liste, IP-Listen |
| K6 | AI-Visibility-Check | Prompt-Sets, Anbieter-Adapter (Anthropic, OpenAI, Gemini, Perplexity), Auswertung, Budget-Wächter | Anbieter-APIs, Postgres | API-Schlüssel |
| K7 | Bericht-Dienst | Monats-PDF, Exporte CSV/XLSX/JSON, Ablage in Nextcloud | Chromium (Playwright), WebDAV | K4 |
| K8 | MCP-Server | Tools aus 4.7, Token-Prüfung | Streamable HTTP | K4, K7 |
| K9 | Jobs | Zeitpläne (Logs täglich, Check monatlich, Bericht monatlich), Wiederholung bei Fehlern | Job-Warteschlange in Postgres (z. B. pg-boss) | Postgres |
| K10 | Infrastruktur | Caddy (TLS), MariaDB 11, Postgres 16, Backups, Überwachung | Docker Compose | Server |

Jede Komponente hat eine klare Aufgabe und eine klare Schnittstelle. Anbieter-Adapter in K6 haben ein gemeinsames Interface. Einen neuen Anbieter fügen wir hinzu, ohne den Rest zu ändern. Für Tests gibt es einen „Fake-Anbieter“.

### 5.2 Datenfluss

```
Besucher-Browser ──(Matomo-JS, cookieless)──────────────► K2 Matomo ──► MariaDB
Website-Server   ──(Server-Ereignis, Modus Streng)──────► K2 Matomo
Hoster-Logs      ──(täglich, SFTP)──► K5 Crawler-Ingest ─┬─► Postgres (nur Bot-Zeilen)
                                                         └─► K2 Matomo (Chatbot-Abrufe, recMode=1)
Google Search Console / Bing-Export ──────────────────────► K4 ──► Postgres
KI-Anbieter-APIs ◄──(Test-Fragen, monatlich)── K6 AI-Visibility-Check ──► Postgres
K2 Matomo (Reporting-API) ───────────────────────────────► K4 Kennzahlen
K4 ──► K7 Bericht (PDF/Export) ──► Nextcloud Kundenordner (Entwurf)
K4 ──► K3 Oberfläche (Team, später Kunde)
K4 ──► K8 MCP-Server ◄── Claude / ChatGPT / eigene Agenten (Token pro Kunde)
```

### 5.3 Fehlerbehandlung

- Matomo nicht erreichbar: Tracker-Anfragen gehen verloren. Deshalb hohe Verfügbarkeit von Matomo. Optional das kostenlose Matomo-Plugin „QueuedTracking“ für Lastspitzen. Berichte für betroffene Tage werden als „unvollständig“ markiert.
- Log-Abruf schlägt fehl: 3 Versuche mit Pause, danach Meldung im internen Talk-Raum. Der nächste Lauf holt verpasste Tage nach, wenn der Hoster sie noch hat.
- KI-Anbieter antwortet nicht: Wiederholung mit wachsender Pause. Teilergebnisse werden gespeichert und als „Teilergebnis“ markiert. Budget überschritten: Stopp und Hinweis im Bericht.
- Fehler bei der Berichtserstellung: Der Bericht bleibt im Status „Fehler“ mit Grund. Es geht nie ein halber Bericht raus.

### 5.4 Hosting auf separatem Server

- Eigener virtueller Server in Deutschland, getrennt vom Nextcloud-Server (Vorgabe V3).
- Größe für den Start (bis etwa 50 Websites, etwa 2 Mio. Seitenaufrufe pro Monat): **4 vCPU, 8 GB RAM, 160 GB NVMe**. Erfahrungswert: etwa 10–20 € netto im Monat bei deutschen Anbietern. Anbieter ist offen (D4).
- Wachstum: Bei mehr Last zuerst mehr RAM für MariaDB, dann Matomo-Archivierung auf eigene Prozesse, später Datenbank auf einen eigenen Server.
- Domains (Vorschlag): `analytics.waybuild-software.de` (App und MCP) und `statistik.waybuild-software.de` (Tracker-Endpunkt). Matomo-Oberfläche nur intern.
- Installationspaket nach unserer Regel: Ordner `installation/` mit benannten `.sh`-Skripten und dem Menü „exe“. Damit lässt sich der Dienst auf einem neuen Server einrichten.

### 5.5 Backup

- Jede Nacht: `mariadb-dump` (Matomo), `pg_dump` (App), Konfiguration und Bericht-Vorlagen.
- Verschlüsselt mit restic auf einen externen Speicher an einem anderen Ort (z. B. Storage-Box).
- Aufbewahrung: 7 tägliche, 4 wöchentliche, 6 monatliche Stände.
- Einmal im Monat ein Test: Wiederherstellung auf einem Test-System, mit Protokoll.
- Matomo kann Berichte aus den Rohdaten neu berechnen. Rohdaten sind deshalb das Wichtigste.

### 5.6 Überwachung

- Erreichbarkeit von Tracker-Endpunkt, App und MCP (Prüfung alle 5 Minuten).
- Letzter erfolgreicher Lauf der Matomo-Archivierung, des Log-Imports und des KI-Checks.
- Speicher, RAM, CPU, Zertifikate.
- Meldungen gehen in einen internen Talk-Raum. Der wöchentliche Sicherheitscheck (Dienstag 13:00) bekommt den neuen Server dazu. Updates nur nach Cans Go (bestehende Regel).

### 5.7 Tests

- Unit-Tests: Kennzahlen-Baustein, Vorher-nachher-Rechnung, Bot-Erkennung, IP-Prüfung, Begriffs-Auswertung.
- Integrationstests: echtes Matomo im Test-Container mit festen Testdaten; Vertrags-Tests gegen die Reporting-API (fällt auf, wenn ein Matomo-Update die Antworten ändert).
- Mandanten-Tests: Kein Token, kein Benutzer und kein Export sieht Daten eines fremden Kunden.
- MCP-Tests: jedes Tool mit gültigem, abgelaufenem und fremdem Token.
- Ende-zu-Ende-Tests (Playwright): Oberfläche, Bericht als PDF (Text im PDF prüfen).
- KI-Adapter nur mit Fake-Anbieter in der automatischen Testkette. Echte API-Aufrufe nur in einem bewusst gestarteten Probelauf mit Budget.
- Test-Datensatz Bot-Logs: echte Beispielzeilen (anonymisiert) für alle Bots der Liste.

---

## 6. Offene Entscheidungen für Can und Jamil

| Nr. | Frage | Vorschlag |
|---|---|---|
| D1 | Name: „Waybuild Analytics“, „Waybuild Analytic“ oder ein anderer Name? (Jamil hat gefragt) | „Waybuild Analytics“, vorher Markenrecherche „Waybuild“ |
| D2 | Lösungsweg | Weg B (Matomo unverändert plus eigene App) |
| D3 | MVP-Umfang wie in 4.0? Welche Websites zuerst? | Ja; Pilot Bauwelt (live, IONOS mit Logs), dann waybuild Website |
| D4 | Server: Anbieter, Größe, Ort; Domain | Deutscher Anbieter, 4 vCPU / 8 GB / 160 GB; Subdomains auf waybuild-software.de |
| D5 | KI-Abfragen: welche Modelle im MVP, Budget pro Kunde, wer legt die API-Konten an? | Claude und ChatGPT im MVP; Budget 10 € netto pro Kunde und Monat; Can legt Konten an, Schlüssel nur auf dem Server |
| D6 | Standard-Tracking-Modus | „Standard“ (cookieless JS), bis der Anwalt § 25 TDDDG beurteilt hat; „Streng“ als Option |
| D7 | Hosting der Kundenwebsites muss Logs liefern (GitHub Pages kann das nicht) | Für den Live-Betrieb Hoster mit Log-Zugang wählen (IONOS, ALL-INKL o. ä.) |
| D8 | Edge-Anbieter (Cloudflare) ja oder nein? | Erst nein; in V2 neu bewerten |
| D9 | Anwaltliche Prüfung (3.6): wer, wann, Budget? | Vor dem ersten Kundenbericht |
| D10 | Rechteübertragung Can und Jamil auf die UG schriftlich regeln | Ja, zusammen mit den bestehenden Verträgen |
| D11 | Gehört Waybuild Analytics in Wegweiser und Wahrzeichen, oder gibt es „KI-Sichtbarkeit“ als Zusatzpaket? | Geschäftsentscheidung; Kosten pro Kunde siehe 4.6 |
| D12 | robots.txt-Politik für KI-Crawler | Bleibt bei Jamil und Can; Waybuild Analytics liefert nur die Zahlen dafür |

---

## 7. Nächste Schritte

1. Can und Jamil lesen diese Spec und entscheiden D1 bis D12, zumindest D2, D3, D4 und D5.
2. Änderungswünsche arbeite ich ein und prüfe die Spec erneut.
3. Nach der schriftlichen Freigabe schreibe ich den Umsetzungsplan (Skill writing-plans) für Stufe 1. Stufe 1 ist zu groß für einen einzigen Plan. Sie wird in Teilpläne zerlegt, die nacheinander gebaut werden:
   - 1a: Server, Installationspaket, Matomo, Kunden-Struktur, Ziele
   - 1b: Kennzahlen-Baustein, Monatsbericht, Exporte, Maßnahmen-Logbuch
   - 1c: KI-Crawler-Import, KI-Referrer-Regeln, Google Search Console
   - 1d: AI-Visibility-Check (Claude, ChatGPT) und MCP-Server
   Jeder Teilplan wird erst gezeigt und freigegeben.
4. Erst danach beginnt die Umsetzung: zuerst der Server mit Installationspaket, dann Matomo, dann die App.

---

## Selbstprüfung der Spec (06.11.2026)

- Platzhalter: keine offenen „TBD“. Unsichere Preise sind ausdrücklich als „prüfen“ markiert.
- Widersprüche: Querverweise, MVP-Tabelle (4.0), Kosten (4.6) und Entscheidungen (6) sind abgeglichen.
- Umfang: Stufe 1 wird in vier Teilpläne zerlegt (Abschnitt 7).
- Eindeutigkeit: Kunden-Login in Stufe 1 = Konto anlegbar, Anmeldung gesperrt. Versand von Berichten = nur von Hand nach Cans „ja“. MCP schreibt nur Entwürfe.

## Anhang: Quellen (abgerufen am 06.11.2026)

- Matomo LICENSE (GPLv3): https://github.com/matomo-org/matomo/blob/5.x-dev/LICENSE
- Matomo composer.json („GPL-3.0+“): https://github.com/matomo-org/matomo/blob/5.x-dev/composer.json
- Matomo JS-Tracker (BSD-3-Clause): https://github.com/matomo-org/matomo/blob/5.x-dev/js/piwik.js
- Matomo Releases (5.14.2 vom 22.10.2026): https://github.com/matomo-org/matomo/releases
- Matomo BotTracking-Quellcode (Bot-Muster): https://github.com/matomo-org/matomo/blob/5.x-dev/plugins/BotTracking/BotDetector.php
- Matomo Trademark Policy: https://matomo.org/trademark/
- Matomo 5.8.0 Changelog: https://matomo.org/changelog/matomo-5-8-0/
- Matomo AI-Chatbot-Tracking per HTTP-API: https://matomo.org/faq/how-to/set-up-ai-chatbot-tracking-with-the-http-tracking-api/
- Matomo AI Assistants (Referrer): https://matomo.org/faq/reports/how-to-track-and-analyse-traffic-from-ai-assistants-like-chatgpt-in-matomo-reports
- Matomo McpServer-Plugin: https://plugins.matomo.org/McpServer
- GNU GPL v3 (Abschnitt 0, „convey“): https://www.gnu.org/licenses/gpl-3.0.html
- GNU AGPL v3 (Abschnitt 13): https://www.gnu.org/licenses/agpl-3.0.html
- GPL-FAQ (Plugins, Aggregation): https://www.gnu.org/licenses/gpl-faq.html
- OpenAI Crawler: https://developers.openai.com/api/docs/bots
- Anthropic Crawler: https://support.claude.com/en/articles/8896518
- Perplexity Crawler: https://docs.perplexity.ai/guides/bots
- Google Crawler: https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers
- Apple Applebot: https://support.apple.com/en-us/119829
- Meta Crawler: https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/
- Anthropic Preise: https://platform.claude.com/docs/en/about-claude/pricing
- MCP-Spezifikation (Autorisierung, Revision 2026-07-28): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index
- Preise OpenAI, Gemini, Perplexity, Bing-Grounding, Bing AI Performance, Search-Console-KI-Bericht: Sekundärquellen (Fachblogs, Preis-Tracker, 2026). **Vor dem Start an den offiziellen Preisseiten prüfen.**
