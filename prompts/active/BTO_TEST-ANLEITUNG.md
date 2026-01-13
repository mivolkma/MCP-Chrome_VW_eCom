# 🧪 BTO duc-vehicle API - Manueller Test

**Version:** 1.0  
**Status:** 🧪 Test-Ready  
**Datum:** 13. Januar 2026

Schritt-für-Schritt Anleitung zum Testen des BTO duc-vehicle Prompts.

---

## ✅ VORAUSSETZUNGEN

### 1. Chrome MCP läuft
```powershell
# Prüfen:
Get-Process chrome | Where-Object { $_.CommandLine -like "*9333*" }

# Falls nicht: Starten
.\chrome-mcp-start.ps1
```

### 2. Credentials vorhanden
```powershell
# Prüfen:
Test-Path ".secrets\credentials.json"
# → Sollte $True sein
```

### 3. VS Code Copilot Chat bereit
- GitHub Copilot Chat Extension aktiv
- MCP Chrome DevTools verfügbar

---

## 🎯 TEST-SZENARIO

### Test-URL:
```
https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/id-5-pure/id-5-pure-pro-77-kwh
```

### Erwartetes Ergebnis:
- Browser öffnet URL mit HTTP Basic Auth
- "Online leasen" Button wird gefunden
- Nach Klick: duc-vehicle API Call erfolgt
- Response wird in `results/bto-duc-vehicle/latest.md` gespeichert

---

## 📋 SCHRITT-FÜR-SCHRITT TEST

### **Schritt 1: Chrome öffnen (manuell testen)**

```powershell
# Chrome sollte schon auf Port 9333 laufen
# Öffne eine neue Tab manuell in dem Chrome-Fenster
# Navigiere zu: https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/id-5-pure/id-5-pure-pro-77-kwh

# Bei HTTP Basic Auth Prompt:
# Username: vw-staging-user (aus credentials.json)
# Password: [aus credentials.json]
```

### **Schritt 2: Copilot Chat verwenden**

Öffne VS Code Copilot Chat und verwende diesen Prompt:

```
@BTO_duc-vehicle_PROMPT.md

Analysiere die folgende URL:
https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/id-5-pure/id-5-pure-pro-77-kwh

Verwende die Credentials aus .secrets/credentials.json für HTTP Basic Auth.
```

### **Schritt 3: Erwartete Aktionen**

Copilot sollte:
1. ✅ Chrome Browser mit der URL öffnen
2. ✅ HTTP Basic Auth mit Credentials durchführen
3. ✅ "Online leasen" Button suchen
4. ✅ Auf Button klicken
5. ✅ Network-Traffic monitoren
6. ✅ duc-vehicle API Call finden
7. ✅ Response extrahieren
8. ✅ Datei `results/bto-duc-vehicle/latest.md` erstellen

### **Schritt 4: Ergebnis prüfen**

```powershell
# Prüfe ob Datei erstellt wurde:
Test-Path "results\bto-duc-vehicle\latest.md"
# → Sollte $True sein

# Öffne Ergebnis:
code "results\bto-duc-vehicle\latest.md"

# Oder im Terminal anzeigen:
Get-Content "results\bto-duc-vehicle\latest.md" | Select-Object -First 50
```

---

## 🐛 TROUBLESHOOTING

### **Problem 1: Chrome nicht gefunden**
```
Fehler: "Could not connect to Chrome DevTools"

Lösung:
1. .\chrome-mcp-start.ps1 ausführen
2. Warten bis Chrome vollständig gestartet ist (5 Sek)
3. Erneut versuchen
```

### **Problem 2: HTTP Basic Auth schlägt fehl**
```
Fehler: "401 Unauthorized"

Lösung:
1. Prüfe credentials.json:
   cat .secrets\credentials.json
2. Prüfe ob Username/Password korrekt sind
3. Ggf. Browser-Cache leeren
```

### **Problem 3: "Online leasen" Button nicht gefunden**
```
Fehler: "Button not found"

Lösung:
1. Seite manuell in Chrome öffnen
2. Visuell prüfen ob Button existiert
3. Mit DevTools (F12) Button-Element inspizieren
4. Selector anpassen falls nötig
```

### **Problem 4: duc-vehicle Call nicht gefunden**
```
Fehler: "No duc-vehicle API call detected"

Lösung:
1. Manuell in Chrome:
   - F12 öffnen
   - Network Tab
   - "Online leasen" klicken
   - Nach "duc-vehicle" filtern
2. Prüfe ob Call wirklich erfolgt
3. URL-Pattern ggf. anpassen
```

---

## 📊 ERWARTETES ERGEBNIS

### Datei: `results/bto-duc-vehicle/latest.md`

```markdown
# DUC-Vehicle API Call - 2026-01-13 14:30:00

## Request Details

### URL
https://v1-123-3.ecom.feature-app.io/bff/duc-vehicle?identifier=VPNVQSWQ&...

### Methode
GET

### Query-Parameter (dekodiert)
- identifier: VPNVQSWQ
- market: de1
- locale: de-DE
- ...

### Request Headers
{
  "accept": "application/json",
  "user-agent": "Mozilla/5.0...",
  ...
}

## Response Details

### Status
200 OK

### Response Body
{
  "identifier": "VPNVQSWQ",
  "model": "ID.5 PURE 125KW",
  "description": "...",
  "images": [...],
  "labels": [...]
}

## Fahrzeug-Informationen

- **Identifier:** VPNVQSWQ
- **Modell:** ID.5 PURE 125KW
- **Motorleistung:** 125 kW (170 PS)
- **Antrieb:** ELECTRICITY
- **CO2-Klasse:** A
- **Außenfarbe:** Costa Azul Metallic
```

---

## ✅ SUCCESS-KRITERIEN

| Kriterium | Erwartung | Check |
|-----------|-----------|-------|
| **Datei erstellt** | `results/bto-duc-vehicle/latest.md` existiert | [ ] |
| **URL korrekt** | duc-vehicle API URL vorhanden | [ ] |
| **Response vollständig** | Kompletter JSON Response gespeichert | [ ] |
| **Fahrzeug-Daten** | Identifier, Modell, etc. extrahiert | [ ] |
| **Zeitstempel** | Datum/Uhrzeit dokumentiert | [ ] |

---

## 🚀 QUICK-TEST BEFEHLE

```powershell
# 1. Chrome starten
.\chrome-mcp-start.ps1

# 2. Warten
Start-Sleep -Seconds 5

# 3. Credentials checken
cat .secrets\credentials.json | ConvertFrom-Json | Select-Object vw_staging_username

# 4. Test-URL in Zwischenablage
Set-Clipboard "https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/id-5-pure/id-5-pure-pro-77-kwh"
Write-Host "✅ URL in Zwischenablage - Jetzt in Copilot Chat einfügen!"

# 5. Nach Test: Ergebnis prüfen
if (Test-Path "results\bto-duc-vehicle\latest.md") {
    Write-Host "✅ Test erfolgreich!" -ForegroundColor Green
    code "results\bto-duc-vehicle\latest.md"
} else {
    Write-Host "❌ Test fehlgeschlagen - Datei nicht erstellt" -ForegroundColor Red
}
```

---

## 📝 NOTIZEN

**Was getestet wird:**
- Browser-Automation mit Chrome MCP
- HTTP Basic Auth Handling
- Button-Click Events
- Network-Request Monitoring
- API-Response Extraktion
- Markdown-File Generation

**Warum wichtig:**
- Validiert den kompletten BTO-Workflow
- Prüft ob MCP Tools korrekt funktionieren
- Zeigt ob Prompt-Struktur effektiv ist
- Gibt Feedback für Optimierung

---

**Bereit?** → Folge den Schritten oben und dokumentiere Ergebnisse! 🚀
