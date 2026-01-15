# BTO SmokeTest (Trockenlauf → nächste Version)

Ziel: Schneller Smoke über die kritischen Pfade (Tabs 1–4) + Preisbox/Edit + Submit-Triggering inkl. FSAG Entry URL Capture.

Wichtig: Bevor der Smoke startet, muss die Test-URL bekannt sein.

➡️ Bitte antworte jetzt mit der Test-URL, unter der der Smoketest stattfinden soll.
- Du darfst die vollständige Start-URL inkl. Query liefern, wenn sie für den korrekten Journey-Start erforderlich ist.
- Wichtig: Der Agent nutzt die URL intern vollständig, speichert/loggt aber nur Host+Path (Query/Token redacted) in Reports/Results.

Rahmenbedingungen:
- Keine Secrets/Tokens/Query-Strings in Logs/Doku.
- E-Mail immer: `test@test.de`
- Bekannter Chrome-Dialog: `.eu` → Credentials; `.io` → schließen.

## Agenten-Verhalten (Autonom)
- Der Agent fragt beim Start nach der Test-URL und führt danach Setup + Test automatisiert aus.
- Setup ist keine Testausführung: Auth (Basic), Cookie-Banner/Modals wegklicken, „sauberer Startzustand“ via Screenshot dokumentieren.
- Nach jedem Lauf: Ergebnisse prüfen, Triage durchführen (Script-Issue vs. App-Defekt) und nächste Schritte ableiten.
- Bei App-Defekt: Evidence Pack vorbereiten (Screenshots/Logs/Repro-Schritte); der standardisierte Bug-Report wird später vom Nutzer erstellt.

Testcharta (git-verfügbar, v1.0):
- Vollständig: [prompts/testdata/bto/v1.0/charter_full.md](prompts/testdata/bto/v1.0/charter_full.md)
- Kompakt: [prompts/testdata/bto/v1.0/charter_compact.md](prompts/testdata/bto/v1.0/charter_compact.md)
- JSON: [prompts/testdata/bto/v1.0/charter.json](prompts/testdata/bto/v1.0/charter.json)

## Scope (PASS/FAIL Kriterien)

### 1) Einstieg & Tab-Slider ([OH-eCom-BTO-02](prompts/testdata/bto/v1.0/charter_full.md#L15) / [OH-eCom-BTO-03](prompts/testdata/bto/v1.0/charter_full.md#L20))
- Checkout öffnet, Tabs sichtbar, Tab 5 bleibt ggf. disabled (akzeptiert, solange CTA-Calls laufen).

### 2) Preisbox Baseline (OH-eCom-BTO-04)
- Preisbox sichtbar, Basiswerte plausibel.
- WebCalc Call `api.cons.webcalc.vwfs.io/webcalc-frontend-service` liefert 200.

### 3) Angebot bearbeiten ([OH-eCom-BTO-05](prompts/testdata/bto/v1.0/charter_full.md#L36))
- „Angebot bearbeiten“ öffnet Financing Layer.
- Änderung z.B. 10.000 → 15.000 km ist möglich.
- Summary zeigt die neuen Werte.

### 4) processOpportunities Vollständigkeit (Submit) – (erwartet)
- Beim Klick „Zum Leasingantrag“ wird `.../bff-forms/processOpportunities` getriggert.
- Erwartung: Payload enthält Journey-Daten (Vehicle/Offer, Finance, Dealer+Pickup, Personal, Consents).
- Prüfung: trainings/02_DETAILLIERT/20_ProcessOpportunities_Payload_Completeness.md + Tool `tools/validate_process_opportunities_payload.py`

### 5) DUC Leasing + FSAG Entry URL (für VPN-Manuallauf)
- Beim Klick „Zum Leasingantrag“ wird `.../bff/duc-leasing` getriggert.
- FSAG Entry URL wird im Testlauf abgegriffen (redacted) und für VPN-Manuallauf optional full.

## Durchführung (kurz)

### A) Automatisierter Lauf (empfohlen)
- Runner starten: `tools/run_bto_checkout.ps1`
- Start-URL bei Prompt einfügen (vollständig inkl. Query ist ok; Artefakte bleiben redacted).
- Artefakte liegen danach unter `results/bto-checkout/runs/<timestamp>/`.

### B) Live Tracer installieren (vor CTA-Klick)
- In DevTools/MCP per `evaluate_script` das Snippet `tools/snippets/trace_duc_entrypoint.js` injizieren.

### C) Klick „Zum Leasingantrag“
- Network prüfen: `processOpportunities` + `duc-leasing`.

### D) FSAG URL auslesen
- redacted: `window.__FSAG_ENTRY_URL`
- optional full (nur lokal): `window.__BTO_ENABLE_FULL_FSAG_URL()` dann `window.__FSAG_ENTRY_URL_FULL`

### E) Optional: Payload-Check lokal
- `python tools/validate_process_opportunities_payload.py --payload results/.../processOpportunities_payload_redacted.json --email test@test.de --duration 36 --mileage 15000 --down-payment 0`

## Evidence (lokal)
- Nutze einen neuen Run-Ordner unter `results/bto-checkout/runs/<YYYY-MM-DD_HH-mm-ss>/`.
- Speichere nur redacted Informationen (Host/Path + sichere Werte).
