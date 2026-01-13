# DUC-Vehicle API Analyse Prompt

## Anweisung für AI-Assistenten

Wenn ich dir eine VW Konfigurator-URL gebe, führe folgende Schritte aus:

### 1. Browser öffnen und navigieren
```
Öffne einen Chrome Browser und navigiere zur angegebenen URL.
Verwende die Credentials aus der credentials.json Datei falls HTTP Basic Auth erforderlich ist.
```

### 2. "Online leasen" Link finden und klicken
```
Suche auf der Seite nach dem Link/Button "Online leasen" oder "ID. Online Leasing".
Klicke darauf und warte bis die Checkout-Seite geladen ist.
Plane Wartezeiten von 3-5 Sekunden ein, da die Seite langsam reagieren kann.
```

### 3. Netzwerk-Traffic analysieren
```
Überwache den Netzwerk-Traffic und suche gezielt nach dem "duc-vehicle" API-Call.
Der Call erfolgt typischerweise an: https://v1-123-3.ecom.feature-app.io/bff/duc-vehicle
```

### 4. API-Call Details extrahieren

Extrahiere folgende Informationen:
- **HTTP-Methode** (GET/POST)
- **Vollständige URL** mit allen Query-Parametern
- **Request Headers**
- **Request Body** (falls POST)
- **Response Status**
- **Response Headers**
- **Response Body** (vollständig)

### 5. Daten strukturiert speichern

Speichere die Ergebnisse in `results/bto-duc-vehicle/latest.md` mit folgender Struktur:

```markdown
# DUC-Vehicle API Call - [Datum/Uhrzeit]

## Request Details

### URL
[Vollständige URL]

### Methode
[GET/POST/etc]

### Query-Parameter (dekodiert)
[Strukturierte Liste der Parameter]

### Request Headers
[Alle Headers]

### Request Body
[JSON formatiert]

## Response Details

### Status
[HTTP Status Code]

### Response Headers
[Alle Headers]

### Response Body
[Vollständiger JSON Response, formatiert]

## Fahrzeug-Informationen (Zusammenfassung)

- **Identifier:** [VPNVQSWQ]
- **Modell:** [ID.5 PURE 125KW]
- **Beschreibung:** [Volltext]
- **Motorleistung:** [125 kW (170 PS)]
- **Antrieb:** [ELECTRICITY]
- **CO2-Klasse:** [A]
- **Außenfarbe:** [Costa Azul Metallic]
- **Innenfarbe:** [Soul-Schwarz/Platinum Grey]
- **Getriebe:** [1-Gang-Automatik]
- **Bild-URL:** [Link zum Fahrzeugbild]

## Reifen-Labels
[Liste aller Reifen mit ihren Label-URLs]

---
```

### 6. Fehlerbehandlung

Falls Probleme auftreten:
- **401 Unauthorized:** Prüfe ob die Seite vollständig geladen wurde
- **404 Not Found:** Warte länger oder prüfe ob der duc-vehicle Call überhaupt erfolgt
- **Timeout:** Erhöhe Wartezeiten zwischen den Schritten
- **Kein duc-vehicle Call gefunden:** Prüfe alle Network-Requests nach Patterns wie "vehicle", "duc", "bff"

## Beispiel-Verwendung

**Input:**
```
Analysiere: https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/...
```

**Erwartete Aktionen:**
1. Browser öffnen mit Credentials
2. Zur URL navigieren
3. "Online leasen" klicken
4. duc-vehicle Call abfangen
5. Daten in results/bto-duc-vehicle/latest.md speichern

## Tools die verwendet werden sollen

- `mcp_io_github_chr_navigate`
- `mcp_io_github_chr_evaluate_script`
- `mcp_io_github_chr_wait_for`
- `mcp_io_github_chr_click`
- `mcp_io_github_chr_list_network_requests`
- `mcp_io_github_chr_get_network_request`
- `create_file` oder `replace_string_in_file` für die Markdown-Datei
