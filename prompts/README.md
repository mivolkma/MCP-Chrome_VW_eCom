# 📝 Prompts Directory

Zentrale Sammlung aller wiederverwendbaren Prompts und Workflows für automatisierte Browser-Tests und API-Analysen.

## Struktur

```
prompts/
├── README.md             # Diese Datei
├── templates/            # 🔧 Basis-Templates
│   ├── browser-navigation.md
│   ├── api-analysis.md
│   ├── network-monitoring.md
│   └── data-extraction.md
└── active/               # 🎯 Aktive Projekt-Prompts
    ├── BTO_duc-vehicle_PROMPT.md      # Build-to-Order Analyse
    ├── BTO-Test-full.md               # Test Execution Guide (Journey)
    ├── BTO-SmokeTest.md               # SmokeTest (Trockenlauf → nächste Version)
    ├── [weitere-projekte].md
    └── [weitere-projekte].md
```

## 📋 Verfügbare Templates

### 1. browser-navigation.md
**Zweck:** Navigation mit Authentifizierung  
**Use Case:** Zu Pages mit HTTP Basic Auth navigieren  
**Beispiel:** VW Staging Umgebung

### 2. api-analysis.md
**Zweck:** API-Call Analyse und Dokumentation  
**Use Case:** Request/Response Details extrahieren  
**Beispiel:** duc-vehicle Endpoint

### 3. network-monitoring.md
**Zweck:** Network-Traffic überwachen  
**Use Case:** Spezifische API-Calls identifizieren  
**Beispiel:** Filter nach "duc-vehicle"

### 4. data-extraction.md
**Zweck:** Daten strukturiert extrahieren  
**Use Case:** JSON-Responses verarbeiten  
**Beispiel:** Fahrzeug-Informationen extrahieren

## 🎯 Active Prompts

### BTO_duc-vehicle_PROMPT.md
**Status:** ✅ Produktiv  
**Projekt:** VW Build-to-Order Analyse  
**Workflow:**
1. Browser öffnen & navigieren
2. "Online leasen" klicken
3. duc-vehicle API abfangen
4. Daten extrahieren & speichern

**Verwendung:**
```
Verwende BTO_duc-vehicle_PROMPT.md für:
- VW Konfigurator-Tests
- duc-vehicle API-Analysen
- BTO-Workflow Automatisierung

### BTO-Test-full.md
**Status:** ✅ Aktiv
**Zweck:** Voller Journey-Run inkl. negative Tests, Evidence und UI↔API Checks.

### BTO-SmokeTest.md
**Status:** ✅ Aktiv
**Zweck:** Schneller Smoke über Tabs 1–4 + Preisbox/Edit + Submit Triggering.
**Enthält:**
- processOpportunities Vollständigkeits-Check (Tool: `tools/validate_process_opportunities_payload.py`)
- DUC/FSAG Entry-URL Live-Capture (Snippet: `tools/snippets/trace_duc_entrypoint.js`)
```

## 📝 Neuen Prompt erstellen

### Schritt 1: Template auswählen
Starten Sie mit dem passenden Template aus `templates/`

### Schritt 2: Strukturieren
```markdown
# [Projekt-Name] Prompt

## Beschreibung
[Kurzer Überblick]

## Use Case
[Wofür wird dieser Prompt verwendet]

## Voraussetzungen
[Was muss vorbereitet sein]

## Workflow
[Schritt-für-Schritt Anleitung]

## Fehlerbehandlung
[Häufige Probleme & Lösungen]
```

### Schritt 3: In `active/` speichern
```
prompts/active/[projekt]_PROMPT.md
```

## 🔄 Prompt Lifecycle

```
templates/
    ↓ (verwendet als Basis)
active/[projekt]_PROMPT.md
    ↓ (wird verwendet & optimiert)
active/[projekt]_PROMPT.md (v2.0)
    ↓ (wenn nicht mehr verwendet)
archive/[projekt]_PROMPT.md
```

## 📊 Best Practices

✅ **DO's:**
- Templates für neue Prompts verwenden
- Prompts klar dokumentieren
- Verwendungsbeispiele hinzufügen
- Fehlerbehandlung dokumentieren
- Regelmäßig aktualisieren

❌ **DON'Ts:**
- Credentials in Prompts einfügen
- URLs hardcoden
- Fehlende Fehlerbeschreibungen
- Veraltete Prompts nicht archivieren

---

**Version:** 1.0  
**Datum:** 13. Januar 2026
