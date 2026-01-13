
Agent Test Execution Guide for eCom BTO Journey
Purpose
This document explains the test goals, structure, and automation strategy for an MCP-enabled agent to execute tests for the eCommerce Build-To-Order (BTO) journey from a user perspective.


✅ Test Objectives
The primary goal is to validate the end-to-end eCom BTO journey across all tabs:

Configurator
Price Box
Personal Data
Pick Up
Summary
Thank You
FSAG
Each test ensures:

Correct UI rendering and navigation.
Functional behavior of CTAs, sliders, and sticky elements.
Accurate data handling and validation.
Responsive design across devices.


✅ JSON Test Structure
The agent will consume a JSON file containing:

testScenario: High-level description of the scenario.
acceptanceCriteria: Expected outcomes.
testCases: Detailed steps with data-testid selectors.
testDataSchema: Required fields and validation rules.
negativeTests: Edge cases and invalid input handling.
deviceMatrix: Supported devices for responsive checks.
Example JSON Snippet:
{
  "testScenario": "Personal Data Tab Validation",
  "description": "Verify that user can enter personal data and proceed only if mandatory fields are filled.",
  "acceptanceCriteria": [
    "Headline and copy text are displayed",
    "Dropdowns and input fields are available",
    "Proceeding to next step only possible when all mandatory fields are filled"
  ],
  "testCases": [
    {
      "id": "OH-eCom-BTO-08",
      "description": "Verify personal data input functionality",
      "preconditions": "User is on Personal Data tab",
      "steps": [
        {"action": "Open URL", "value": "https://stage-url-placeholder"},
        {"action": "Fill dropdown", "field": "Salutation", "value": "Mr", "data-testid": "dropdown-salutation"},
        {"action": "Fill input", "field": "First name", "value": "{{testData.firstName}}", "data-testid": "input-firstname"},
        {"action": "Fill input", "field": "Email", "value": "test@test.de", "data-testid": "input-email"},
        {"action": "Click CTA", "data-testid": "cta-next-step"}
      ],
      "expectedResult": "Next step is accessible only if all mandatory fields are filled"
    }
  ],
  "testDataSchema": {
    "firstName": {"type": "string", "required": true},
    "lastName": {"type": "string", "required": true},
    "email": {"type": "string", "required": true, "pattern": ".+@.+\\..+", "example": "test@test.de"}
  },
  "negativeTests": [
    {
      "description": "Verify error when mandatory fields are empty",
      "steps": [
        {"action": "Leave all fields empty"},
        {"action": "Click CTA", "data-testid": "cta-next-step"}
      ],
      "expectedResult": "Error message displayed, cannot proceed"
    }
  ],
  "deviceMatrix": ["Desktop-Chrome", "Mobile-iOS-Safari", "Tablet-Android-Chrome"]
}


✅ Agent Responsibilities

Load JSON and parse scenarios.
Locate elements using data-testid selectors.
Generate missing test data dynamically: Use predefined schema.
Always use test@test.de for email to avoid backend API calls.
Execute negative tests for validation errors.
Capture results and log pass/fail status.


✅ Automation Strategy

Fallback for Missing Data: Agent uses Faker or predefined defaults.
Responsive Testing: Iterate through deviceMatrix.
Error Handling: Validate UI messages for negative tests.


Next Steps

Full JSON export for all 35 checkpoints.
Integration with MCP agent for autonomous execution.
Testdata here:

prompts\testdata\BTO-testcharta.json


✅ Handling: Basic-Auth / Login Popups (bekanntes Phänomen)

- Bei jedem Wechsel eines Formularschritts kann Chrome erneut nach Basic-Auth fragen.
- Wenn die Domain auf `*.eu` endet: Credentials erneut eingeben und fortfahren.
- Wenn die Domain auf `*.io` endet: Popup schließen (kein Login nötig).


✅ Einschränkung

- Den letzten Schritt/Testcase aktuell überspringen (zur Zeit nur mit VPN erreichbar).


✅ Optional: JSON → kompakte Step-Liste

Für eine schnell scanbare Checklist kann die JSON lokal in Markdown konvertiert werden:

- Script: tools/testcharta_json_to_compact_md.py
- Default Output: prompts/testdata/BTO-testcharta_compact.md
- Empfehlung (VPN-Schritt skippen): `python tools/testcharta_json_to_compact_md.py --skip-last`


✅ Lokale Testergebnisse / Evidence (aktueller Run)

Diese Artefakte sind lokal unter `results/**` abgelegt (nicht in Git committen):

- Run Log: results/bto-checkout/runs/2026-01-13_14-31-04/run_log.md
- Journey Tree: results/bto-checkout/runs/2026-01-13_14-31-04/journey_tree.md
- data-testid / data-cy Tracking pro Checkpoint: results/bto-checkout/runs/2026-01-13_14-31-04/ui_testids_checkpoints.md
- UI ↔ API Konsistenzcheck (insb. WebCalc Werte ↔ UI): results/bto-checkout/runs/2026-01-13_14-31-04/api_ui_consistency.md

✅ Submit-Qualität: processOpportunities muss Journey-Daten enthalten

Erwartung: Der POST `.../bff-forms/processOpportunities` ist der zentrale Submit/Process Call und muss **alle im Journey gesammelten Daten** enthalten (Fahrzeug/Angebot, Finance/WebCalc, Dealer+Pickup, Personal Data, Consents).

Wie prüfen (ohne Secrets zu speichern):
- Guide: trainings/02_DETAILLIERT/20_ProcessOpportunities_Payload_Completeness.md
- Lokales Tool: tools/validate_process_opportunities_payload.py
- Beispiel-Expect: tools/examples/process_expect.example.json

✅ Manuelltest (VPN): FSAG/Entry-Point URL aus DUC-Response

Wenn der Flow „Zum Leasingantrag“ eine DUC-Response mit Links liefert (z.B. `ENTRY_POINT`), wird diese URL für den manuellen Test im VPN-Browser benötigt.

- Tool: tools/extract_fsag_entry_url.py
- Default: redacted (ohne Query)
- Für lokalen manuellen Test: `--full` (nicht committen/loggen)

✅ Automatischer Testlauf: FSAG/Entry-Point URL direkt aus Network abgreifen

Zeitpunkt: Direkt nach Klick auf „Zum Leasingantrag“ (im selben Schritt, in dem `processOpportunities` getriggert wird) kommt typischerweise der Network-Call zu `.../bff/duc-leasing`.

Vorgehen (MCP / Browser-Injection):
- Vor dem Klick per `evaluate_script` den Tracer installieren: `tools/snippets/trace_duc_entrypoint.js`
- Klick auf „Zum Leasingantrag“
- Danach per `evaluate_script` auslesen:
  - redacted: `window.__FSAG_ENTRY_URL`
  - optional full (nur lokal): erst `window.__BTO_ENABLE_FULL_FSAG_URL()` aufrufen, dann `window.__FSAG_ENTRY_URL_FULL`