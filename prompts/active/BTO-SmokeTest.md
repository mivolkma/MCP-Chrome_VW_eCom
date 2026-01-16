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

Keep-it-green (Governance):
- Der Report darf keine "aus Screenshots abgeleiteten" Aussagen enthalten.
- Für jedes Checklist-Item gilt: entweder atomar automatisiert belegt (PASS/FAIL/WARN) oder explizit als Test-Gap markiert (UNKNOWN/WARN mit klarer Limitation).
- Optional (strict): alles außer PASS ist ein Gate-Fail (für CI/Quality-Gates erst aktivieren, wenn die Checks stabil sind).

Spec-Lock:
- Die Testcharta/Anforderungen werden nicht vom Agenten umformuliert oder abgeschwächt, nur um einen Lauf "grün" zu bekommen.
- Wenn ein Charter-Text unklar ist (z.B. "many tabs", "cover all steps"), muss der Mensch die Intention/Schwellenwerte festlegen.
- Der Agent markiert dann SPEC_REQUIRED als UNKNOWN/WARN inkl. konkreter Frage.

Sprachregel (systemweit, verbindlich):
- Kommunikation mit dem Human erfolgt IMMER in dessen bevorzugter Sprache.
- Ablage/Artefakte (Fix-Backlog, SPEC_REQUIRED Fragen+Antworten, Mapping-Regeln) erfolgen IMMER in der Sprache der Testcharta.
- Wenn ein Ergebnis unklar/nicht bewertbar ist: Human nach Erwartung fragen (Human-Sprache) und explizit um Antwort in Charter-Sprache für die Ablage bitten.

## Strategie: Testfall-Verständnis → Härtung des Testscripts

Ziel: Aus Charter-Texten werden deterministische, maschinenprüfbare Checks – ohne "aus Screenshots zu raten".

Arbeitsartefakt (Fragen + Platz für Antworten):
- [results/bto-checkout/reports/latest_fix_backlog.md](results/bto-checkout/reports/latest_fix_backlog.md)

Vorgehen (konservativ, Spec-Lock-konform):
1) Charter-Bullet isolieren
	- Bullet ist die "Spec" (z.B. "sticky bar sticks while scrolling until footer is accessed").
	- Sofort entscheiden: deterministisch testbar? Wenn nein → SPEC_REQUIRED (Frage im Fix-Backlog).

2) Atomaren Check definieren (Hypothese + Messpunkt)
	- DOM-State: Sichtbarkeit, Text, Attribute, Position, CSS-Properties.
	- Navigation: URL/History/Tab-State/Step-Index.
	- Network: konkreter Call (Host+Path), Status, minimaler Payload-Ausschnitt (redacted).

3) Intent im Runner implementieren
	- In `tools/execute_smoketest.py` als `intent`-Step (kleine, robuste Assertions).
	- Ergebnis immer maschinenlesbar nach `results/.../step_results.jsonl` unter `atomic` schreiben.

4) Variant-/Viewport-Abhängigkeiten aktiv prüfen
	- Keine Annahmen hardcoden (z.B. Pfeile nur bei Overflow).
	- Wenn Verhalten viewport-abhängig: gezielt Viewports probieren (Desktop/Tablet/Mobile), dann Assertion.
	- Original-Viewport wiederherstellen; im `atomic` protokollieren welcher Viewport genutzt wurde.

5) Post-Run Mapping (Analyzer) statt Screenshot-Interpretation
	- `tools/analyze_bto_run.py` mappt nur echte `atomic` Ergebnisse auf Checklist PASS/FAIL/WARN.
	- Wenn SPEC_REQUIRED offen: Checklist bleibt UNKNOWN/WARN + klare Frage.

6) Supervisor/Quality Gate (optional)
	- `tools/supervise_bto_run.py` im strict mode: alles außer PASS ist Fail.
	- Aktivieren erst, wenn die Checks stabil sind (sonst blockiert man sich mit Flakes).

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

Post-Run (automatisch durch den Runner, falls aktiviert):
- `step_results.jsonl`: maschinenlesbare Step- und Atomic-Ergebnisse (Quelle der Wahrheit).
- `BTO_Test_Report_v1.0.html`: Checklist wird durch Analyzer deterministisch befüllt.
- `agent_feedback.md`: ehrliche Limitationen + konkrete To-dos (Selector/Timing/Spec-Gaps).
- Optional: `supervisor_summary.md` + Strict-Gate (FAIL wenn nicht alles PASS).

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
