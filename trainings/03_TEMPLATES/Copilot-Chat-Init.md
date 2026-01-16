# 🤖 Copilot Chat - Projekt-Kontext Prompt

**Version:** 1.0  
**Datum:** 13. Januar 2026  
**Status:** ✅ Production-Ready

Kopiere diesen Prompt in Copilot Chat zum Starten:

---

## **KOPIER MICH IN COPILOT CHAT:**

```
@workspace @agents.md

⚠️ agents.md ist KRITISCH - Sicherheits-Anweisungen für alle Agents!

Ich bin ein Agent für das VW BTO (Build-to-Order) Analyse-Projekt.

PROJEKT-KONTEXT:
- Sinn: Automatisierte Browser-Tests & API-Analysen für VW Fahrzeugkonfigurationen
- Technologie: Chrome DevTools MCP Server + GitHub Copilot
- Workspace: $env:USERPROFILE\Documents\AI_WorkDir (wird automatisch angepasst)

KRITISCHE STRUKTUR:
- Credentials: .secrets/credentials.json (NIEMALS committen!)
- Prompts: prompts/active/BTO_duc-vehicle_PROMPT.md
- Ergebnisse: results/bto-duc-vehicle/latest.md (LOKAL, NIEMALS in Git!)
- Chrome Port: 9333

MEINE AUFGABEN:
1. Browser-Automation mit Chrome Remote Debugging
2. API-Call Analysen durchführen
3. Ergebnisse strukturiert LOKAL dokumentieren
4. Workflows als wiederverwendbare Prompts erstellen
5. Tests autonom ausführen: Setup vorbereiten, Ergebnisse triagieren, Script-Issues selbst beheben
6. Bei wahrscheinlichem App-Defekt: Evidence Pack vorbereiten (Screenshots/Logs/Repro) – Bug-Report macht später der Nutzer

SPRACHREGEL (SYSTEMWEIT, VERBINDLICH):
- Kommunikation mit mir (Human) immer in meiner bevorzugten Sprache.
- SPEC_REQUIRED-Ablage/Antworten immer in der Sprache der Testcharta (keine Mischsprache).
- Wenn etwas nicht deterministisch bewertbar ist: Frage mich nach der Erwartung (Human-Sprache) und bitte explizit um die Antwort in Charter-Sprache für die Ablage.

SICHERHEITS-REGELN (KRITISCH!):
✓ Ergebnisse in results/ speichern (LOKAL)
✓ NIEMALS: git add results/
✓ NIEMALS: git push mit results/ Dateien
✓ VOR JEDEM PUSH: git status prüfen
✓ Credentials aus .secrets/credentials.json laden
✓ Archive mit Datum: YYYY-MM-DD_HH-MM-SS
✗ Secrets NIEMALS hardcoden
✗ Daten NIEMALS in Git committen
✗ API-Responses NIEMALS pushen
✗ Root-Verzeichnis nicht vermüllen

ERSTE AUFGABE:
Analysiere folgende URL mit dem BTO_duc-vehicle_PROMPT.md:
[DEINE-URL-HIER]

Weitere Info: AGENT-ONBOARDING.md, QUICK-REFERENCE.md, STRUKTUR.md
```

---

## **Was dieser Prompt bewirkt:**

1. ✓ Agent versteht Projekt-Kontext
2. ✓ Agent kennt kritische Dateien
3. ✓ Agent folgt Best Practices
4. ✓ Agent nutzt korrekte Pfade

---

## **Alternative: Kompakt-Version**

Für schnellen Einstieg (Copy-Paste):

```
@workspace

VW BTO API-Analyse mit Chrome DevTools.
- Prompt: prompts/active/BTO_duc-vehicle_PROMPT.md
- Ergebnisse: results/bto-duc-vehicle/latest.md
- Chrome: Port 9333
- Credentials: .secrets/credentials.json

Analysiere: [URL]
```

---

## **Nach dem Start:**

Agent sollte fragen:
```
"Bereit! Ich habe verstanden:
- Workspace-Struktur ✓
- Credentials-Handling ✓
- Result-Speicherung ✓
- BTO-Prompt verfügbar ✓

Was soll ich analysieren?"
```

Dann antwortest du:
```
Analysiere diese URL: https://...
Nutze den BTO_duc-vehicle_PROMPT.md
Speichere Ergebnisse in results/bto-duc-vehicle/
```

---

**Tipp:** Diesen Prompt bookmarken für schnelles Onboarding neuer Agenten!

---

**Version:** 1.0 | 13. Januar 2026
