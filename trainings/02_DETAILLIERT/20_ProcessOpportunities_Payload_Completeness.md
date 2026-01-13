# ✅ processOpportunities – Payload Vollständigkeit (Journey Context)

Ziel: Der POST `.../bff-forms/processOpportunities` muss **alle im Journey gesammelten Informationen** enthalten, damit das Backend den Leasingantrag konsistent weiterverarbeiten kann.

Sicherheits-/Redaction-Regeln (kritisch):
- **Keine** Tokens/Keys/Cookies/Authorization/Query-Strings persistieren.
- In Dokumenten und Reports nur **Host + Path** notieren.
- Request-Bodies können sensitive Felder wie `targetUrl` enthalten → **immer Query entfernen** bzw. Feld redacted.

---

## 1) Was „vollständig“ bedeutet

„Vollständig“ heißt: Der Request enthält mindestens diese Daten-Gruppen (nicht nur UI-Text, sondern strukturierte Werte), die während Tabs 1–4 gesammelt wurden.

### A) Angebots-/Fahrzeug-Kontext
- Fahrzeug-Identifikatoren (z.B. Modell/Trim/Carline bzw. eine eindeutige Vehicle/Offer-ID)
- Konfiguration / Ausstattung (soweit im Checkout relevant)

### B) Finanzierungs-Kontext (WebCalc)
- `duration` (Laufzeit)
- `mileage` (jährliche Fahrleistung)
- `downPayment` (Sonderzahlung)
- optional/idealerweise: rate/recurring payment oder Referenz/ID auf das kalkulierte Angebot

### C) Dealer + Pickup/Delivery
- Dealer-Identifikation und Adresse (mind. ID/Name/PLZ/Ort)
- Abhol-/Lieferoption (Pick-up option)
- Delivery/Überführungskosten bzw. referenzierte Daten (falls Backend benötigt)

### D) Kundendaten (Personal Data)
- Anrede
- Vorname / Nachname
- E-Mail (im Test immer `test@test.de`)
- Mobilnummer
- Adresse (Straße, Hausnr., PLZ, Ort)

### E) Consent/Legal
- DSGVO/Datenschutz Zustimmung
- optionale Marketing-Opt-ins (wenn im UI vorhanden)

### F) Technischer Kontext (Backend Routing)
- Checkout/Opportunity IDs, Correlation IDs etc. (nicht unbedingt sichtbar in UI, aber notwendig fürs Backend)

---

## 2) Warum der 403 trotzdem „relevant“ ist

Auch wenn der Call aktuell oft mit **403** endet (z.B. `passcodeVerificationResult.success=false`), ist er der zentrale „Submit“-Request.

Wichtig:
- 403 blockiert den End-to-End-Fortschritt, aber der Request ist trotzdem der richtige Ort, um **Payload-Vollständigkeit** zu prüfen.
- Der Payload kann groß sein (Form-/Mapping-Konfiguration). Deshalb braucht es eine **strukturierte Suche** nach den Journey-Werten.

---

## 3) Sichere Datenerfassung (ohne Secrets)

### Schritt 1: Request Payload aus DevTools holen
1. Chrome DevTools → Network → Filter `processOpportunities`
2. Request auswählen → Tab **Payload**
3. **Copy request payload** (oder JSON manuell kopieren)

### Schritt 2: Lokal speichern (nur Workspace!)
- Speichere in einem Run-Ordner unter `results/` (niemals committen).
- Entferne/ersetzte sensitive Felder vor dem Speichern:
  - alles was wie `targetUrl` aussieht: Query-Teil entfernen (`?…`) oder Wert komplett `"[REDACTED_URL]"` setzen
  - keine Headers wie `Authorization`, `Cookie` etc. speichern

Beispiel-Pfad:
- `results/bto-checkout/runs/<RUN>/processOpportunities_payload_redacted.json`

---

## 3b) Manuelltest (VPN): FSAG/Entry-Point URL aus DUC-Response extrahieren

Wenn „Zum Leasingantrag“ einen DUC-Leasing Call liefert, enthält die Response typischerweise Links wie `ENTRY_POINT`/`CONTINUE_IN_CHECKOUT`.
Für den manuellen Test (VPN + Browser) wird oft die Entry-URL benötigt.

Wichtig: Der DUC-Request ist häufig eine URL mit vielen Query-Parametern (z.B. `oneapiKey`, `endpoint`, `signature`, etc.).
- Für Identifikation/Logging reicht **Host + Path**:
  - `https://v1-123-3.ecom.feature-app.io/bff/duc-leasing`
- Query-Parameter dieser Art sind als **sensitiv** zu behandeln und dürfen nicht in Doku/Logs/Git landen.

- Script: `tools/extract_fsag_entry_url.py`
- Input: eine lokal gespeicherte DUC-Response (JSON)
- Ausgabe:
  - Standard: redacted (ohne Query/Fragment)
  - Optional: volle URL mit `--full` (nur lokal verwenden; nicht committen/loggen)

Beispiel:
```powershell
C:/Users/mivolkma/Documents/AI_WorkDir/.venv/Scripts/python.exe tools/extract_fsag_entry_url.py --input results/bto-checkout/runs/<RUN>/duc_leasing_response.json
```

Für den VPN-Manuallauf:
```powershell
C:/Users/mivolkma/Documents/AI_WorkDir/.venv/Scripts/python.exe tools/extract_fsag_entry_url.py --input results/bto-checkout/runs/<RUN>/duc_leasing_response.json --full
```

### Alternative (empfohlen für den Testlauf): Live-Extraktion direkt im Browser

Wenn du die URL **im Testlauf** (Zeitpunkt: nach Klick/ProcessOp, wenn `bff/duc-leasing` läuft) automatisch einsammeln willst, installiere vor dem Klick einen kleinen Fetch/XHR-Tracer.

- Snippet: `tools/snippets/trace_duc_entrypoint.js`
- Effekt: setzt nach DUC-Response folgende Window-Variablen:
  - `window.__FSAG_ENTRY_URL` (redacted)
  - optional `window.__FSAG_ENTRY_URL_FULL` (nach `window.__BTO_ENABLE_FULL_FSAG_URL()`)

Damit kann der Agent die URL direkt nach dem Klick auslesen und in den lokalen Run-Artefakten ablegen.

---

## 4) Automatisierte Validierung

Es gibt ein lokales Tool, das den Payload nach den wichtigsten Journey-Werten durchsucht und einen PASS/FAIL Report erzeugt:

- Script: `tools/validate_process_opportunities_payload.py`
- Example Expectation File: `tools/examples/process_expect.example.json`

### Variante A: Mit Expect-JSON
```powershell
C:/Users/mivolkma/Documents/AI_WorkDir/.venv/Scripts/python.exe tools/validate_process_opportunities_payload.py `
  --payload results/bto-checkout/runs/<RUN>/processOpportunities_payload_redacted.json `
  --expect tools/examples/process_expect.example.json
```

### Variante B: Mit Flags (Quick Check)
```powershell
C:/Users/mivolkma/Documents/AI_WorkDir/.venv/Scripts/python.exe tools/validate_process_opportunities_payload.py `
  --payload results/bto-checkout/runs/<RUN>/processOpportunities_payload_redacted.json `
  --email test@test.de `
  --duration 36 --mileage 15000 --down-payment 0
```

Erwartung:
- Das Tool gibt pro Daten-Gruppe PASS/FAIL aus.
- Exit-Code ist ungleich 0, wenn Pflichtfelder fehlen.

---

## 5) Ergebnisinterpretation

- **PASS (Vollständigkeit):** Alle Gruppen A–E sind im Payload nachweisbar und (wo spezifiziert) stimmen Werte (z.B. duration/mileage/downPayment).
- **FAIL:** Mindestens eine Gruppe fehlt komplett (z.B. keine Dealer-Infos) oder zentrale Werte fehlen.
- **WARN:** Werte sind vorhanden, aber mehrfach/inkonsistent (z.B. duration einmal 36 und einmal 48) → dann ist eine Korrelation/Quelle zu klären.

---

## 6) Häufige Ursachen für fehlende Daten im processOpportunities Payload

- Edit-Änderung (WebCalc) wird nur im UI aktualisiert, aber nicht in das „Submit Model“ gemappt.
- Mehrere Kalkulationen im Session-Cache; falsche wird referenziert.
- Dealer/Pickup wird UI-seitig gesetzt, aber Backend erwartet IDs aus anderen BFF Calls.
- Consent-Flags werden nur als UI-State gehalten, aber nicht serialisiert.

