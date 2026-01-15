# 🏢 AI_WorkDir - VW BTO API Analysis Projekt

**Version:** 3.1  
**Zuletzt aktualisiert:** 15. Januar 2026  
**Status:** 🧪 Proof of Work (PoW)  
**Struktur:** ✅ Optimiert (Redundanzen entfernt)

Zentrale Arbeitsumgebung für automatisierte Browser-Tests, API-Analysen und Dokumentation mit GitHub Copilot und MCP Chrome DevTools.

⚠️ **Hinweis zum Reifegrad:** Dieses Repo zeigt die Arbeitsweise (Runner + Evidence-Pipeline) als **Proof of Work**. Inhalte/Reports/Findings sind nicht automatisch ein „aktuelles, belastbares Ergebnis“ und müssen je Run/Umgebung verifiziert werden.

**Wofür ist dieses Repo praktisch gedacht?**
- **Journey-/Smoke-Tests ausführbar machen** (Playwright-basiert, charter-/prompt-getrieben)
- **Evidence/Artefakte automatisch erzeugen** (z.B. Network-/API-Spuren, Checkpoints, Findings, Screenshots, Reports)
- **Reproduzierbarkeit & Teilen ermöglichen**, ohne dass lokale Runs oder Secrets im Repo landen (alles Sensitive bleibt lokal/ignored)
- **Guardrails gegen Leaks** (z.B. Secret-Scanning via GitHub Actions / Gitleaks)

Kurz: Statt manuell in DevTools zu suchen, bekommst du pro Lauf ein konsistentes Evidence-Paket, das Debugging/Regression erleichtert.

**Übertragbarkeit:** Die gleiche Arbeitsweise lässt sich 1:1 auf andere Journeys und Testartefakte anwenden (z.B. andere Checkout-Varianten, DUC/Leasing-Flows, reine API-Checks, UI-Regressionen, Performance-/Fehler-Sammlungen) – du tauschst im Wesentlichen nur Charter/Prompts und die gewünschten Evidence-Outputs.

---

## 🎯 **EINSTIEG - 3 SCHRITTE (30 Minuten)**

### **1️⃣ Sicherheits-Gedächtnis laden**
Lade **[agents.md](agents.md)** in deinen Chat-Kontext als "Memory" für dieses Projekt!

```
@agents.md in deinen Chat-Context laden
→ Alle Sicherheits-Regeln & Best Practices sind verfügbar
```

**agents.md enthält:**
- ✅ 5 kritische Sicherheits-Regeln  
- ✅ Phishing-Erkennung
- ✅ Git-Safety-Checks
- ✅ Effizienz-Anweisungen (Keine Duplikat-Doku!)

### **2️⃣ Training & Dokumentation**
Alle Dokumentationen & Guides sind unter **[trainings/](trainings/README.md)** organisiert:

👉 **[trainings/README.md](trainings/README.md)** ← START HIER!

Darin findest du:
- 📌 **QUICK-START** (30 min) - Alles für den Anfang
- 📚 **DETAILLIERT** - Tieferes Verständnis
- 🎓 **TEMPLATES** - Fertige Vorlagen
- 📋 **ARCHIVE** - Alte Dokumentationen

### **3️⃣ Chrome DevTools & erste Analyse**
```powershell
# Chrome mit Remote Debugging starten
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
& "$WORKSPACE\chrome-mcp-start.bat"

# Dann in VS Code Copilot Chat verwenden:
# prompts/active/BTO_duc-vehicle_PROMPT.md
```

---

## 📁 **Verzeichnisstruktur**

```
AI_WorkDir/
│
├── 🔐 .secrets/                   # Geschützte Credentials (NICHT in Git!)
│   ├── .gitignore                 # Schützt credentials.json
│   ├── credentials.example.json   # Template zum Teilen
│   └── README.md                  # Wie Credentials nutzen?
│
├── 📝 prompts/                    # Wiederverwendbare Workflows
│   ├── README.md                  # Prompt-Verwaltung
│   ├── templates/                 # Basis-Templates
│   │   ├── browser-navigation.md
│   │   ├── api-analysis.md
│   │   ├── network-monitoring.md
│   │   └── data-extraction.md
│   └── active/                    # LIVE Prompts
│       └── BTO_duc-vehicle_PROMPT.md
│
├── 📊 results/                    # Analyseergebnisse (NICHT in Git!)
│   ├── README.md                  # Ergebnis-Verwaltung
│   └── bto-duc-vehicle/           # Projekt-Ergebnisse
│       ├── latest.md              # Aktuelle Analyse
│       ├── summary.md             # Zusammenfassung
│       ├── archive/               # Historische Daten
│       └── data/                  # Raw JSON Data
│
├── 📚 docs/                       # Projektdokumentation (OK in Git)
│   ├── README.md
│   └── [weitere Dokumentationen]
│
├── 🎓 trainings/                  # ZENTRAL: Alle Training & Guides! ⭐
│   ├── README.md                  ← START HIER
│   ├── 00_EINSTIEG/               # Projektüberblick
│   ├── 01_QUICK-START/            # Setup & Anfänger
│   ├── 02_DETAILLIERT/            # Advanced Topics
│   ├── 03_TEMPLATES/              # Fertige Vorlagen
│   └── 04_ARCHIVE/                # Historisch
│
├── 🔧 chrome-mcp-start.bat        # Browser-Launcher (Windows)
├── 🔧 chrome-mcp-start.ps1        # Browser-Launcher (PowerShell)
├── agents.md                      # ⚠️ SICHERHEITS-MEMORY (LADE IMMER!)
├── README.md                      # Diese Datei
└── .gitignore                     # Git-Sicherheit (results/, .secrets/ ignoriert)
```

---

## 🔐 **Git-Sicherheit: Was darf rein?**

| Verzeichnis | Inhalt | Git | Grund |
|-----------|--------|-----|--------|
| `agents.md` | Sicherheits-Regeln | ✅ **JA** | Shared Memory |
| `trainings/` | Dokumentation & Guides | ✅ **JA** | Shared Knowledge |
| `prompts/` | Wiederverwendbare Workflows | ✅ **JA** | Shared Templates |
| `docs/` | Projektdokumentation | ✅ **JA** | Shared Knowledge |
| `.secrets/` | Credentials | ❌ **NEIN** | Sicherheit! |
| `results/` | Analyseergebnisse | ❌ **NEIN** | Zu große Dateien |
| `chrome-profile/` | Browser-Profil | ❌ **NEIN** | Local-spezifisch |

**Regel:** `git status` muss **"working tree clean"** zeigen bevor du pusht!

---

## 🧾 Versionierung (MAJOR.MINOR)

- **MAJOR** nur erhöhen bei großen/strukturbrechenden Änderungen (Reorg, Pfade/Struktur ändern).
- **MINOR** erhöhen bei inhaltlichen Updates/Erweiterungen oder Regel-/Format-Änderungen.
- Für reine Tippfehler/Wording gilt ebenfalls **MINOR** (weil wir hier ohne Patch-Level versionieren).

---

## 🚨 **WICHTIGSTE DATEIEN**

| Datei | Zweck | Typ |
|-------|--------|-----|
| **[agents.md](agents.md)** | Sicherheits-Anweisungen & Agent-Memory | ⚠️ LADE IMMER! |
| **[trainings/README.md](trainings/README.md)** | Zentrale Dokumentations-Navigation | 📌 START HIER |
| **[trainings/01_QUICK-START/](trainings/01_QUICK-START/)** | Quick-Start Setup (30 min) | 🚀 Für Anfänger |
| **[trainings/02_DETAILLIERT/](trainings/02_DETAILLIERT/)** | Detaillierte Guides | 📚 Für Fragen |

**Zu viele Dateien zum Lesen?**
→ Lade **agents.md** + gehe zu **trainings/README.md**
→ Folge dem QUICK-START Pfad (30 min)
→ Dann kannst du anfangen! 🎯

---

## ⚡ **Schnelle Kommandos**

```powershell
# Chrome mit MCP starten
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
& "$WORKSPACE\chrome-mcp-start.bat"

# BTO Checkout Smoketest Runner (Playwright)
# - Fragt nach der dynamischen Start-URL (inkl. Query möglich)
# - Loggt/speichert redacted (nur Host+Path)
& "$WORKSPACE\tools\run_bto_checkout.ps1"

# Workspace öffnen
cd "$env:USERPROFILE\Documents\AI_WorkDir"

# Git-Status checken
git status
# MUSS zeigen: "nothing to commit, working tree clean"
```

---

## 📊 **Was ist neu in dieser Version?**

**v3.1 (15. Januar 2026):**
- ✅ Wording vereinheitlicht ("committet" statt Umgangssprache)
- ✅ Versionierungsregeln (MAJOR.MINOR) präzisiert

**v3.0 (13. Januar 2026):**
- ✅ Root-Struktur optimiert (weniger Dateien, mehr Klarheit)
- ✅ Alle Trainings unter `trainings/` organisiert
- ✅ Zentrale Navigation über `trainings/README.md`
- ✅ Redundanzen entfernt (Struktur nur noch 1x dokumentiert)
- ✅ Klarer Lern-Pfad für Anfänger
- ✅ agents.md mit Effizienz-Regeln erweitert

**Das Ziel:** Neue Agenten sollen in 30 Minuten produktiv arbeiten können! 🚀

---

## 🔗 **Wichtige Links**

- 🔐 [Sicherheits-Memory laden](agents.md)
- 📚 [Alle Trainings & Dokumentation](trainings/README.md)
- 🚀 [QUICK-START für Anfänger](trainings/01_QUICK-START/)
- 💾 [Credentials Setup](trainings/01_QUICK-START/01_VS-Code-Setup.md)
- 🌐 [Chrome DevTools Setup](trainings/01_QUICK-START/02_Chrome-DevTools-Setup.md)
- ⚡ [Schnell-Referenz](trainings/01_QUICK-START/04_Schnell-Referenz.md)
- 📖 [Vollständige Struktur](trainings/02_DETAILLIERT/10_Vollständige-Struktur.md)

---

## 📋 Workflows

### Workflow 1: Neue Analyse durchführen

```
1. Prompt aus prompts/ auswählen
   └─ BTO_duc-vehicle_PROMPT.md

2. URL vorbereiten
   └─ z.B. VW Konfigurator URL

3. Copilot Chat öffnen (Ctrl + Alt + I)
   └─ Prompt + URL eingeben

4. Ergebnisse in results/ speichern
   └─ results/bto-duc-vehicle/latest.md

5. Summary aktualisieren
   └─ results/bto-duc-vehicle/summary.md
```

### Workflow 2: Neues Projekt starten

```
1. Prompt-Template auswählen
   └─ prompts/templates/[template].md

2. Neuen Prompt erstellen
   └─ prompts/active/[projekt]_PROMPT.md

3. Projekt-Verzeichnis in results/ erstellen
   └─ results/[projekt]/

4. Erste Analyse durchführen
   └─ Ergebnisse in results/[projekt]/

5. Training aktualisieren
   └─ Neues Szenario hinzufügen
```

### Workflow 3: Ergebnisse archivieren

```
1. Analyse abgeschlossen
   └─ results/[projekt]/latest.md

2. In Archive verschieben
   └─ results/[projekt]/archive/YYYY-MM-DD_analysis.md

3. Summary aktualisieren
   └─ results/[projekt]/summary.md

4. Neue Analyse starten
   └─ Neues latest.md
```

---

## 📊 Verfügbare Projekte

### 1. BTO duc-vehicle
**Status:** ✅ Aktiv  
**Beschreibung:** VW Build-to-Order Fahrzeugkonfiguration Analyse  
**Prompt:** `prompts/active/BTO_duc-vehicle_PROMPT.md`  
**Results:** `results/bto-duc-vehicle/`  

---

## 🎓 Dokumentation

### Für Anfänger
1. trainings/README.md
2. trainings/00_Setup_MCP_Chrome_DevTools.md
3. trainings/01_Erste_Schritte_Testszenarien.md
4. docs/ARCHITECTURE.md

### Für Entwickler
1. docs/API-REFERENCE.md
2. docs/WORKFLOW.md
3. prompts/README.md
4. docs/guides/prompt-creation.md

### Für Probleme
1. docs/TROUBLESHOOTING.md
2. trainings/00_Setup_MCP_Chrome_DevTools.md (Troubleshooting Section)

---

## � Dokumentation & Onboarding

| Dokument | Für wen? | Wann lesen? |
|----------|---------|-----------|
| **[agents.md](agents.md)** | 🤖 Alle Agents | **VOR JEDEM START** - Sicherheits-Gedächtnis |
| **[Projektüberblick](trainings/00_EINSTIEG/00_Projektüberblick.md)** | 👤 Neue Agenten | Erste Woche - Projekt-Überblick |
| **[Schnell-Referenz](trainings/01_QUICK-START/04_Schnell-Referenz.md)** | ⚡ Während Arbeit | Tägliche Nachschlag |
| **[Copilot Chat-Init](trainings/03_TEMPLATES/Copilot-Chat-Init.md)** | 💬 Chat-Sessions | Neuen Chat starten |
| **[Chrome DevTools Setup](trainings/01_QUICK-START/02_Chrome-DevTools-Setup.md)** | 🌐 Browser-Automation | Chrome-Probleme |

---

## �🔄 Skalierbarkeit

Diese Struktur wächst mit Ihren Anforderungen:

```
Heute:          Morgen:              Später:
1 Projekt    →  3-5 Projekte    →   20+ Projekte
```

**results/[projekt]/** für jedes neue Projekt
**prompts/active/** für jeden neuen Workflow
**docs/** dokumentiert alles zentral

---

## ✅ Checkliste - Agent-Start

- [ ] **[agents.md](agents.md) in Chat-Kontext laden** (`@agents.md`)
- [ ] `.secrets/credentials.json` existiert
- [ ] `trainings/` Dokumentation gelesen
- [ ] MCP Server konfiguriert
- [ ] Workspace-Struktur verstanden
- [ ] Git-Sicherheit verinnerlicht (NIEMALS results/ committen!)

---

## ✅ Checkliste - Vor Commits

- [ ] `git status` zeigt "working tree clean"
- [ ] KEINE `results/` Dateien in staging area
- [ ] KEINE `.secrets/credentials.json` geändert
- [ ] KEINE Credentials/API-Keys in Code
- [ ] Nur `prompts/`, `docs/`, `trainings/` committet
- [ ] `git push` abgesichert

---

## 🤝 Best Practices

✅ **DO's:**
- Struktur konsistent nutzen
- Ergebnisse sofort speichern
- Prompts als Templates nutzen
- Dokumentation aktualisieren
- Archivieren statt Löschen

❌ **DON'Ts:**
- Credentials committen
- Projektdaten in root speichern
- Templates ändern (Kopie nutzen)
- Alte Analysen löschen
- Struktur ignorieren

---

## 📞 Support

**Problem?** → `docs/TROUBLESHOOTING.md`  
**Frage?** → `docs/` durchsuchen  
**Neue Idee?** → Neue Ordner-Struktur planen

---

**Version:** 3.1  
**Zuletzt aktualisiert:** 15. Januar 2026  
**Erstellt für:** VW BTO API Analyse & Automation
