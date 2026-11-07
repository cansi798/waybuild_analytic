# Diagramme Waybuild Analytics

PlantUML-Quelltexte (`*.puml`, Stil in `_stil.iuml`), gerendert nach `svg/` und `png/`.

Neu rendern:

```bash
cd docs/diagramme
docker run --rm -u $(id -u):$(id -g) -v $PWD:/data -w /data plantuml/plantuml:1.2024.8 -tsvg -o svg *.puml
docker run --rm -u $(id -u):$(id -g) -v $PWD:/data -w /data plantuml/plantuml:1.2024.8 -tpng -o png *.puml
```

| Datei | Inhalt |
|---|---|
| `1-use-cases.puml` | Use-Case-Diagramm |
| `2a-sequenz-besuch-dashboard.puml` | Besuch → Matomo → Kennzahlen → Dashboard |
| `2b-sequenz-ki-check.puml` | Monatlicher KI-Check je Website |
| `2c-sequenz-mcp.puml` | MCP-Abfrage mit Token je Kunde |
| `3a-aktivitaet-monatsbericht.puml` | Monatsbericht erstellen, freigeben, versenden |
| `3b-aktivitaet-onboarding.puml` | Neuen Kunden und Website onboarden |
