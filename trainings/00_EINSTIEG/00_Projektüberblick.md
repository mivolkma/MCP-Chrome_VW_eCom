# 🚀 Projekt-Initialisierungs-Prompt

**Version:** 2.0  
**Zielgruppe:** Neue Agenten, Entwickler, Mitarbeiter  
**Zweck:** Schnelle Einarbeitung in Struktur & Workflow  
**Zeit:** ~10-15 Minuten zum Durchlesen  
**Status:** ✅ Production-Ready

⚠️ **NACH DIESEM DOKUMENT:** Lies [../../agents.md](../../agents.md) für tägliche Sicherheits-Anweisungen und Arbeitsablauf!

---

## 📖 **Für Agenten: Projekt-Überblick**

Hallo! Du wirst in folgendes Projekt eingearbeitet:

### **Projekt-Name**
**VW Build-to-Order (BTO) API Analyse & Automation**

### **Mission**
Automatisierte Browser-Tests und API-Analysen für VW Fahrzeugkonfigurationen durchführen, dokumentieren und in wiederverwendbare Workflows verpacken.

### **Technologie-Stack**
- 🌐 **Chrome DevTools MCP Server** (Model Context Protocol)
- 🤖 **GitHub Copilot** für Automation & Code-Generierung
- 📝 **Markdown** für Dokumentation & Workflows
- 🔐 **Git** mit `.gitignore` für Credential-Schutz

---

## 🎯 **Kernaufgaben**

1. **Browser-Automation**
   - Chrome remote steuern
   - URLs navigieren mit HTTP Basic Auth
   - Click-Events auslösen
   - Warten auf Page-Loads

2. **API-Analyse**
   - Network-Traffic monitoren
   - Spezifische API-Calls isolieren
   - Request/Response extrahieren
   - Daten strukturiert dokumentieren

3. **Workflow-Dokumentation**
   - Prompts als Vorlagen erstellen
   - Best Practices dokumentieren
   - Fehlerbehandlung definieren
   - Training für andere erstellen

4. **Daten-Management**
   - Ergebnisse strukturiert speichern
   - Historische Daten archivieren
   - Sicherheit gewährleisten (Credentials)

---

## 📁 **Projekt-Struktur (WICHTIG!)**

```
AI_WorkDir/                          ← ROOT: Dokumentation & Startups
│
├── 🔐 .secrets/                     ← SICHERHEIT: Credentials & Secrets
│   ├── credentials.json             (lokal, .gitignore-geschützt)
│   ├── credentials.example.json     (Template zum Teilen)
│   ├── README.md
│   └── .gitignore
│
├── 📝 prompts/                      ← WORKFLOWS: Wiederverwendbare Prompts
│   ├── README.md                    (Prompt-Management Guide)
│   ├── templates/                   (Basis-Templates)
│   │   ├── README.md
│   │   ├── browser-navigation.md
│   │   ├── api-analysis.md
│   │   ├── network-monitoring.md
│   │   └── data-extraction.md
│   └── active/                      (LIVE-PROMPTS)
│       └── BTO_duc-vehicle_PROMPT.md
│
├── 📊 results/                      ← ERGEBNISSE: Analyseergebnisse & Daten
│   ├── README.md                    (Ergebnis-Management Guide)
│   └── bto-duc-vehicle/             (Projekt-spezifische Ergebnisse)
│       ├── README.md
│       ├── summary.md               (Zusammenfassung aller Analysen)
│       ├── latest.md                (Neustes Analyseergebnis)
│       ├── archive/                 (Historische Analysen)
│       │   └── README.md
│       └── data/                    (Raw JSON Daten)
│           └── README.md
│
├── 📚 docs/                         ← DOKUMENTATION: Guides & Referenzen
│   ├── README.md                    (Navigation)
│   ├── CHROME-MCP-SETUP.md          (Browser-Automation)
│   ├── MIGRATION.md                 (Struktur-Änderungen)
│   └── guides/                      (Zukünftige Guides)
│
├── 🎓 trainings/                    ← LERNEN: Onboarding & Referenzen
│   ├── README.md                    (Training-Übersicht)
│   ├── AGENT-ONBOARDING.md          (Projekt-Überblick - DU BIST HIER)
│   ├── QUICK-REFERENCE.md           (Tägliche Nachschlag)
│   └── COPILOT-CHAT-INIT.md         (Chat-Initialisierung)
│   ├── 00_Setup_MCP_Chrome_DevTools.md
│   └── 01_Erste_Schritte_Testszenarien.md
│
├── .gitignore                       (Credentials & Cache schützen)
├── README.md                        (Haupt-Dokumentation)
├── STRUKTUR.md                      (Diese Struktur im Detail)
├── MIGRATION.md                     (Wie es reorganisiert wurde)
└── CHROME-MCP-SETUP.md              (Chrome Remote Debugging Setup)
```

---

## 🔑 **Kritische Regeln - BITTE BEACHTEN!**

### ✅ **MUSS gemacht werden:**
- Credentials IMMER in `.secrets/credentials.json` speichern
- Ergebnisse IMMER in `results/[projekt]/` speichern (NIEMALS committen!)
- Neue Prompts IMMER in `prompts/active/` speichern
- Archive IMMER mit Datum versehen (YYYY-MM-DD_HH-MM-SS)
- **VOR JEDEM GIT-PUSH:** `git status` prüfen - KEINE `results/` Dateien!

### ❌ **NIEMALS - SICHERHEITS-KRITISCH!**
- ⚠️ **ERGEBNISSE IN GIT COMMITTEN** (results/ sind lokal nur!)
- ⚠️ **API-Responses/Daten committen** (können Secrets enthalten)
- ⚠️ **Credentials hardcoden oder teilen**
- ⚠️ **Analyseergebnisse mit echten Daten pushen**
- Root-Verzeichnis mit Dateien vermüllen
- Alte Analysen löschen (→ archive/)
- Secrets in Dokumentation schreiben
- Veraltete Prompts nicht archivieren

### 🔐 **GIT-SICHERHEIT - GOLDENE REGELN**

**Vor JEDEM Push:**
```powershell
git status
```
**Sollte ZEIGEN:**
```
nothing to commit, working tree clean
```

**Sollte NICHT zeigen:**
```
results/
.secrets/credentials.json
.cache/
chrome-profile/
```

Wenn doch: **NICHT pushen!** `.gitignore` ist nicht konfiguriert!

---

## 🔄 **Typischer Workflow**

### **Szenario 1: Neue Analyse durchführen**

```
1. Prompt auswählen
   └─ prompts/active/BTO_duc-vehicle_PROMPT.md

2. URL vorbereiten
   └─ z.B. https://cs-stage-vw.lighthouselabs.eu/...

3. Copilot Chat öffnen
   └─ "Verwende BTO_duc-vehicle_PROMPT.md und analysiere [URL]"

4. Ergebnisse speichern
   └─ results/bto-duc-vehicle/latest.md

5. Summary aktualisieren
   └─ results/bto-duc-vehicle/summary.md

6. Alte Analyse archivieren (falls nötig)
   └─ results/bto-duc-vehicle/archive/YYYY-MM-DD_analysis.md
```

### **Szenario 2: Neues Projekt starten**

```
1. Template auswählen
   └─ prompts/templates/[template].md

2. Prompt anpassen
   └─ Kopie als prompts/active/[projekt]_PROMPT.md

3. Ergebnis-Verzeichnis erstellen
   └─ mkdir results/[projekt]/{archive,data}

4. README.md für Projekt erstellen
   └─ results/[projekt]/README.md

5. Training aktualisieren (optional)
   └─ trainings/01_Erste_Schritte_Testszenarien.md
```

---

## 🛠️ **Verfügbare Tools im Projekt**

### **MCP Chrome DevTools**
```
- mcp_io_github_chr_navigate
- mcp_io_github_chr_click
- mcp_io_github_chr_wait_for
- mcp_io_github_chr_take_snapshot
- mcp_io_github_chr_list_network_requests
- mcp_io_github_chr_get_network_request
- mcp_io_github_chr_evaluate_script
```

### **VS Code / Dateimanagement**
```
- create_file
- replace_string_in_file
- read_file
- list_dir
- grep_search
```

### **Terminal & Automation**
```
- run_in_terminal (PowerShell)
- create_and_run_task
```

---

## 📊 **Aktuelles Projekt: BTO duc-vehicle**

### **Status:** ✅ AKTIV

### **Was ist das?**
VW Build-to-Order Fahrzeugkonfiguration API-Analyse:
- API Endpoint: `POST /bff/duc-vehicle`
- Fahrzeug: ID.5 Pure 125kW (VPNVQSWQ)
- Umgebung: VW Staging (dev-tqa)
- Port: 9333 (Chrome Remote Debugging)

### **Verfügbare Daten**
- **Prompt:** `prompts/active/BTO_duc-vehicle_PROMPT.md`
- **Letztes Ergebnis:** `results/bto-duc-vehicle/latest.md`
- **Zusammenfassung:** `results/bto-duc-vehicle/summary.md`
- **Historische Daten:** `results/bto-duc-vehicle/archive/`

### **Nächste Schritte**
- [ ] Weitere Fahrzeugkonfigurationen analysieren
- [ ] Andere Modelle testen (ID.4, ID.3)
- [ ] Performance-Trends dokumentieren
- [ ] Andere Märkte testen (FR, IT, ES)

---

## 🔐 **Sicherheit & Credentials**

### **Setup:**
```
1. Kopiere: .secrets/credentials.example.json
2. Benenne zu: .secrets/credentials.json
3. Fülle echte Werte ein
4. Git ignoriert automatisch (✓ .gitignore)
```

### **Struktur:**
```json
{
  "vw_staging": {
    "base_url": "https://cs-stage-vw.lighthouselabs.eu",
    "username": "...",
    "password": "..."
  },
  "api_keys": {
    "oneapi_key": "..."
  }
}
```

### **Verwendung im Prompt:**
```javascript
// Credentials laden (lokal aus .secrets/credentials.json)
// WICHTIG: Credentials NICHT in die URL einbetten (History/Logs/Screenshots).
// Stattdessen:
// - Browser/HTTP Basic Auth Dialog verwenden ODER
// - in Playwright via http_credentials arbeiten (siehe tools/execute_smoketest.py)
const creds = require('./.secrets/credentials.json');

// Beispiel (konzeptionell):
// const context = await browser.newContext({
//   httpCredentials: { username: creds.vw_staging.username, password: creds.vw_staging.password }
// });
// await page.goto(creds.vw_staging.base_url + '/konfigurator.html/...');
```

---

## 📚 **Schnell-Referenz**

### **Ich möchte...**

| Ziel | Datei | Befehl |
|------|-------|--------|
| Projekt verstehen | `README.md` | Start hier |
| Struktur sehen | `STRUKTUR.md` | Vollständiger Übersicht |
| Neue Analyse | `prompts/active/` | Prompt auswählen |
| Ergebnis speichern | `results/[proj]/` | latest.md bearbeiten |
| Neuen Prompt | `prompts/templates/` | Template kopieren |
| Training | `trainings/` | README.md lesen |
| Chrome starten | `chrome-mcp-start.bat` | Ausführen |
| Sicherheit | `agents.md` | Memory laden |

---

## 🎯 **Erste 5 Minuten als Agent**

```
1. README.md lesen (2 min)
   → Projekt-Überblick verstehen

2. STRUKTUR.md durchsuchen (2 min)
   → Ordner-Layout kennen

3. .secrets/ prüfen (1 min)
   → Credentials konfiguriert?

4. prompts/active/ ansehen (1 min)
   → Welche Prompts sind verfügbar?

5. results/bto-duc-vehicle/ checken (1 min)
   → Letzte Analyseergebnisse sehen
```

**→ Danach:** Bereit für erste Aufgaben!

---

## ✨ **Best Practices**

### **Dokumentation**
✅ Markdown mit klarer Struktur  
✅ Headers (# ## ###) konsistent nutzen  
✅ Codeblöcke mit Sprache kennzeichnen  
✅ Links relativ (kein absoluter Pfad)  

### **Dateibenennung**
✅ Projekt-Namen konsistent (z.B. `bto-duc-vehicle`)  
✅ Datum für Archive: `YYYY-MM-DD_HH-MM-SS`  
✅ Aussagekräftige Namen (nicht `data.md`)  
✅ Klein geschrieben mit Bindestrich  

### **Commits (Git)**
✅ Vor Push: Keine Secrets in Code  
✅ `.gitignore` prüfen (sollte Secrets schützen)  
✅ Aussagekräftige Commit-Messages  
✅ Regelmäßig pushen (nicht warten)  

### **Code-Qualität**
✅ Fehlerbehandlung definieren  
✅ Timeouts für langsame APIs setzen  
✅ Logging für Debugging  
✅ Tests mit verschiedenen Szenarien  

---

## 📞 **FAQ für Agenten**

### **F: Wo speichere ich Analyseergebnisse?**
**A:** `results/[projekt-name]/latest.md`  
Falls ältere Ergebnisse existieren → `archive/` verschieben

### **F: Wie nutze ich die Credentials?**
**A:** Aus `.secrets/credentials.json` laden, niemals hardcoden

### **F: Welcher Port für Chrome?**
**A:** 9333 (konfigurierbar in `chrome-mcp-start.bat`)

### **F: Wie archiviere ich alte Daten?**
**A:** Verschiebe in `results/[proj]/archive/YYYY-MM-DD_description.md`

### **F: Kann ich neue Projekte starten?**
**A:** Ja! Kopiere Template aus `prompts/templates/`, erstelle neues `results/[proj]/`

### **F: Was wenn etwas schiefgeht?**
**A:** 
1. `CHROME-MCP-SETUP.md` prüfen
2. `trainings/00_Setup*.md` durchlesen
3. Terminal-Befehle debuggen

---

## 🚀 **Nächster Schritt**

### **Für diese Sitzung:**
1. Diesen Prompt verstanden? ✓
2. Struktur in `STRUKTUR.md` überprüfen
3. Erste Aufgabe? → Frag nach!

### **Langfristig:**
- Neue Projekte hinzufügen
- Templates erweitern
- Automation vertiefen
- Team skalieren

---

## 📋 **Agent-Checkliste**

- [ ] Projekt-Zweck verstanden
- [ ] Ordnerstruktur überblickt
- [ ] .secrets/credentials.json konfiguriert
- [ ] prompts/active/ analysiert
- [ ] results/bto-duc-vehicle/ überprüft
- [ ] chrome-mcp-start.bat getestet
- [ ] README.md & STRUKTUR.md gelesen
- [ ] Erste Aufgabe angefordert

---

**Version:** 1.0  
**Erstellt:** 13. Januar 2026  
**Für:** Agenten, Entwickler, neue Mitarbeiter  
**Status:** ✅ Bereit zum Einsatz

---

## 💬 **Kontakt & Fragen**

Falls Fragen oder Unklarheiten:
- Lies relevante `.md` Datei
- Prüfe `CHROME-MCP-SETUP.md`
- Frag nach spezifischer Aufgabe

**Willkommen im Team!** 🎉
