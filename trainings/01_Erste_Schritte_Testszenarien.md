# Erste Schritte: Test-Szenarien für BTO duc-vehicle Analyse

Diese Anleitung führt Sie durch praktische Test-Szenarien nach der Installation des MCP Chrome DevTools Servers.

---

## 🎯 Übersicht der Test-Szenarien

| Level | Szenario | Dauer | Schwierigkeit |
|-------|----------|-------|---------------|
| 1 | Einfache Navigation zu Google | 2 min | ⭐ Einfach |
| 2 | VW Konfigurator öffnen | 5 min | ⭐⭐ Mittel |
| 3 | "Online leasen" klicken | 10 min | ⭐⭐⭐ Mittel |
| 4 | duc-vehicle API analysieren | 15 min | ⭐⭐⭐⭐ Fortgeschritten |
| 5 | Vollständiger BTO-Workflow | 20 min | ⭐⭐⭐⭐⭐ Experte |

---

## 📝 Level 1: Einfache Navigation (Warm-up)

### Ziel
Überprüfen, ob der MCP Server korrekt funktioniert

### Schritt-für-Schritt

1. **Copilot Chat öffnen** (`Ctrl + Alt + I`)

2. **Befehl eingeben:**
   ```
   Öffne einen Chrome Browser und navigiere zu https://www.google.de
   ```

3. **Erwartetes Verhalten:**
   - Chrome öffnet sich automatisch
   - Google wird geladen
   - Copilot bestätigt: "Navigation erfolgreich"

4. **Screenshot nehmen:**
   ```
   Nimm einen Screenshot der aktuellen Seite
   ```

### ✅ Erfolgskriterien
- [ ] Chrome öffnet sich
- [ ] Google wird angezeigt
- [ ] Keine Fehlermeldungen im Chat

---

## 📝 Level 2: VW Konfigurator öffnen

### Ziel
Mit HTTP Basic Auth zur VW Staging-Umgebung navigieren

### Vorbereitung
Stellen Sie sicher, dass `credentials.json` existiert:
```json
{
  "vw_staging": {
    "username": "onehub-cms-user",
    "password": "Tp5a38TCiosv"
  }
}
```

### Test-URL
```
https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/energy-sondermodelle/energy?buildabilityStatus=buildable&category=private&carlineId=30450&salesGroupId=36330&trimName=ENERGY
```

### Befehl
```
Öffne einen Chrome Browser und navigiere zu:
https://onehub-cms-user:Tp5a38TCiosv@cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/energy-sondermodelle/energy?buildabilityStatus=buildable&category=private&carlineId=30450&salesGroupId=36330&trimName=ENERGY

Warte 5 Sekunden bis die Seite vollständig geladen ist.
```

### ✅ Erfolgskriterien
- [ ] Keine "401 Unauthorized" Fehlermeldung
- [ ] VW Konfigurator wird angezeigt
- [ ] ID.5 ENERGY Fahrzeug ist sichtbar

### 📷 Was Sie sehen sollten
- VW Logo oben links
- Fahrzeugbild des ID.5
- Konfigurationsoptionen (Farbe, Ausstattung, etc.)
- "Online leasen" Button/Link

---

## 📝 Level 3: "Online leasen" Link klicken

### Ziel
Automatisch zum Checkout navigieren

### Befehl
```
1. Öffne Chrome und navigiere mit den Credentials aus credentials.json zu:
   https://onehub-cms-user:Tp5a38TCiosv@cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/energy-sondermodelle/energy?buildabilityStatus=buildable&category=private&carlineId=30450&salesGroupId=36330&trimName=ENERGY

2. Warte 5 Sekunden

3. Suche den Link mit dem Text "Online leasen" oder "ID. Online Leasing"

4. Klicke auf diesen Link

5. Warte weitere 5 Sekunden bis die Checkout-Seite geladen ist

6. Nimm einen Screenshot
```

### ✅ Erfolgskriterien
- [ ] Link "Online leasen" wurde gefunden
- [ ] Click wurde ausgeführt
- [ ] URL ändert sich zu `.../checkout.html`
- [ ] Checkout-Formular wird angezeigt

### 🐛 Troubleshooting

**Problem:** "Link nicht gefunden"
```
Nimm einen Snapshot der Seite und zeige mir alle verfügbaren Links
```

**Problem:** "Seite lädt zu langsam"
```
Warte 10 Sekunden statt 5
```

---

## 📝 Level 4: duc-vehicle API Call analysieren

### Ziel
Network-Traffic überwachen und duc-vehicle Call identifizieren

### Befehl (mehrstufig)

**Schritt 1: Navigation**
```
Öffne Chrome mit Credentials und navigiere zur VW Konfigurator URL.
Klicke auf "Online leasen" und warte bis die Checkout-Seite geladen ist.
```

**Schritt 2: Network Requests auflisten**
```
Liste alle Netzwerk-Requests auf die in den letzten 30 Sekunden gemacht wurden.
Suche nach Requests die "duc-vehicle" im URL enthalten.
```

**Schritt 3: Request Details abrufen**
```
Hole die vollständigen Details des duc-vehicle API Calls:
- Request Method
- Request Headers
- Request Body
- Response Status
- Response Headers
- Response Body
```

### ✅ Erfolgskriterien
- [ ] duc-vehicle Request gefunden
- [ ] Method: POST
- [ ] Status: 200 OK
- [ ] Response enthält `ducVehicleModel`
- [ ] Vehicle Identifier sichtbar (z.B. "VPNVQSWQ")

### 📊 Erwartete Response-Struktur
```json
{
  "ducVehicleModel": {
    "identifier": "VPNVQSWQ",
    "modelCode": "E392DF",
    "name": "ID.5 PURE 125KW",
    "description": "ID.5 Pure ENERGY...",
    "enginePower": "125 kW (170 PS)",
    "fuelType": "ELECTRICITY",
    ...
  }
}
```

---

## 📝 Level 5: Vollständiger BTO-Workflow (Experte)

### Ziel
Kompletter automatisierter Workflow gemäß `BTO_duc-vehicle_PROMPT.md`

### Vorbereitung
1. Öffnen Sie `BTO_duc-vehicle_PROMPT.md`
2. Lesen Sie den Prompt vollständig durch
3. Bereiten Sie die Test-URL vor

### Vollständiger Befehl
```
Ich möchte eine vollständige BTO duc-vehicle Analyse durchführen.

Verwende die Anleitung aus BTO_duc-vehicle_PROMPT.md und befolge alle Schritte:

1. Lade die Credentials aus credentials.json
2. Öffne Chrome und navigiere zur VW Konfigurator URL mit Authentication
3. Warte bis die Seite vollständig geladen ist (5 Sekunden)
4. Finde den "Online leasen" Link und klicke darauf
5. Warte bis die Checkout-Seite geladen ist (5 Sekunden)
6. Überwache den Network Traffic und finde den duc-vehicle API Call
7. Extrahiere alle Request/Response Details
8. Speichere die Ergebnisse strukturiert in BTO_duc-vehicle.md

Test-URL:
https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/energy-sondermodelle/energy?buildabilityStatus=buildable&category=private&carlineId=30450&salesGroupId=36330&trimName=ENERGY&modelId=E392DF$MAAUE0G$GRD8RD8$GW0GW0G&modelVersion=1&modelYear=2026&exteriorId=F14+3K3K&interiorId=F56+++++QT&options=GPAKPAK
```

### ✅ Erfolgskriterien
- [ ] Chrome öffnet automatisch
- [ ] Navigation erfolgreich (keine 401 Fehler)
- [ ] "Online leasen" wurde geklickt
- [ ] Checkout-Seite geladen
- [ ] duc-vehicle Call gefunden und analysiert
- [ ] BTO_duc-vehicle.md wurde aktualisiert
- [ ] Alle Fahrzeug-Details extrahiert:
  - [ ] Identifier
  - [ ] Modell-Name
  - [ ] Motorleistung
  - [ ] Farben
  - [ ] CO2-Klasse
  - [ ] Bild-URL

### 📄 Erwartetes Ergebnis in BTO_duc-vehicle.md

Die Datei sollte folgende Abschnitte enthalten:
- Request Details (URL, Method, Headers, Body)
- Response Details (Status, Headers, Body)
- Fahrzeug-Informationen (strukturierte Zusammenfassung)
- Reifen-Labels
- Performance-Metriken

---

## 🎓 Advanced: Verschiedene Konfigurationen testen

### Szenario A: Andere Farbe
```
Modifiziere die URL und ändere exteriorId auf:
- F14+0Q0Q (Moonstone Grey)
- F14+1R1R (Kings Red)
- F14+9T9T (Pure White)

Analysiere jeweils den duc-vehicle Call und vergleiche die Responses.
```

### Szenario B: Andere Ausstattung
```
Ändere die options auf:
- GPAK (nur Assist-Paket)
- GJAK (nur Komfort-Paket)
- GPAKPAKGJAK (beide Pakete)

Dokumentiere die Unterschiede in den API-Responses.
```

### Szenario C: Anderes Modell
```
Teste mit ID.4 oder ID.3:
Ändere carlineId, modelId und trimName entsprechend.
Vergleiche die duc-vehicle Response-Struktur.
```

---

## 📊 Benchmark-Zeiten

Typische Ausführungszeiten pro Szenario:

| Schritt | Erwartete Dauer |
|---------|-----------------|
| Chrome öffnen | 2-3 Sekunden |
| Seite laden (mit Auth) | 5-10 Sekunden |
| "Online leasen" klicken | 1-2 Sekunden |
| Checkout laden | 5-10 Sekunden |
| duc-vehicle Call | 0,5-1 Sekunde |
| Response verarbeiten | 0,5 Sekunden |
| **GESAMT** | **14-27 Sekunden** |

---

## 🐛 Häufige Fehler und Lösungen

### Fehler 1: "Element not found"
**Ursache:** Seite nicht vollständig geladen  
**Lösung:** Wartezeiten erhöhen (10-15 Sekunden)

### Fehler 2: "401 Unauthorized"
**Ursache:** Credentials nicht korrekt übergeben  
**Lösung:** URL-Format prüfen: `https://user:pass@domain.com`

### Fehler 3: "duc-vehicle Call nicht gefunden"
**Ursache:** Zu früh nach Network Requests gesucht  
**Lösung:** Erst nach vollständigem Checkout-Load suchen

### Fehler 4: "Response truncated"
**Ursache:** Response zu groß (>10KB)  
**Lösung:** Verwenden Sie `get_network_request` statt `list_network_requests`

---

## ✅ Abschluss-Checkliste

Nach Abschluss aller Test-Szenarien sollten Sie:

- [ ] Level 1-5 erfolgreich durchlaufen haben
- [ ] `BTO_duc-vehicle.md` mit aktuellen Daten befüllt haben
- [ ] Mindestens 3 verschiedene Konfigurationen getestet haben
- [ ] Screenshots der wichtigsten Schritte gespeichert haben
- [ ] Verstehen wie der duc-vehicle API Call funktioniert
- [ ] In der Lage sein, eigene URLs zu analysieren

---

## 🎯 Nächste Schritte

Nach erfolgreicher Durchführung:

1. **Automatisierung:** Erstellen Sie Scripts für wiederkehrende Analysen
2. **Dokumentation:** Ergänzen Sie `BTO_duc-vehicle.md` mit eigenen Erkenntnissen
3. **Erweiterung:** Analysieren Sie weitere API-Calls (z.B. webcalc-frontend-service)
4. **Integration:** Binden Sie die Analyse in CI/CD Pipelines ein

---

**Viel Erfolg bei Ihren Tests!** 🚀

---

**Version:** 1.0  
**Datum:** 13. Januar 2026  
**Erstellt für:** VW BTO duc-vehicle API Analyse Training
