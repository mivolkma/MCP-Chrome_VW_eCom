# 🎓 Training & Dokumentation - Zentrale Navigation

**Version:** 2.2  
**Status:** 🧪 Proof of Work (PoW)  
**Zuletzt aktualisiert:** 15. Januar 2026

Alle Dokumentationen, Guides und Trainingsmaterialien für das VW BTO API Analysis Projekt.

---

## 🚀 **QUICK-START** (Anfänger? Hier starten!)

Wenn du neu bist, folge diesem Pfad (~30 Minuten):

### **1️⃣ [Projektüberblick](00_EINSTIEG/00_Projektüberblick.md)** (10 min)
- Was ist dieses Projekt?
- Was ist die Mission?
- Welche Technologien?
- Kernaufgaben überblicken

### **2️⃣ [VS Code Setup](01_QUICK-START/01_VS-Code-Setup.md)** (12 min)
- GitHub Copilot Extension installieren
- MCP Marketplace konfigurieren
- Chrome DevTools MCP einrichten
- Verifizierung

### **3️⃣ [Chrome DevTools Setup](01_QUICK-START/02_Chrome-DevTools-Setup.md)** (8 min)
- Chrome mit Remote Debugging starten
- MCP Server initialisieren
- Verbindung testen

### **4️⃣ [Schnell-Referenz](01_QUICK-START/04_Schnell-Referenz.md)** (5 min)
- Häufigste Aufgaben
- Struktur Übersicht
- Schnelle Antworten während Arbeit

---

## 📚 **DETAILLIERTE ANLEITUNG** (Tieferes Verständnis)

Für Fragen, Fehlerbehebung und erweiterte Topics:

### **[Vollständige Projektstruktur](02_DETAILLIERT/10_Vollständige-Struktur.md)**
- Alle Verzeichnisse erklären
- Wofür jeder Ordner?
- Datei-Konventionen
- Best Practices

### **[Umgebungsvariablen & Konfiguration](02_DETAILLIERT/11_Umgebungsvariablen.md)**
- `$env:USERPROFILE` erklären
- Wie Konfiguration funktioniert
- User-unabhängige Pfade
- Troubleshooting

### **[Chrome DevTools MCP - Tiefgang](01_Erste_Schritte_Testszenarien.md)**
- Advanced MCP Server Konfiguration
- Debugging Szenarien
- Real-World Testfälle
- Performance-Tipps

### **[processOpportunities Payload-Vollständigkeit](02_DETAILLIERT/20_ProcessOpportunities_Payload_Completeness.md)**
- Welche Journey-Daten im Submit stecken müssen
- Sichere Erfassung (Redaction)
- Lokales Validierungstool (PASS/FAIL)

---

## 🎓 **SPEZIELLE TEMPLATES & TOOLS**

### **[Copilot Chat Initialisierungs-Prompt](03_TEMPLATES/Copilot-Chat-Init.md)**
- Vorlage für neue Chat-Sessions
- Projekt-Kontext setzen
- Mit Copilot effektiv arbeiten

---

## 🔒 **SICHERHEIT & BEST PRACTICES**

⚠️ **WICHTIG:** Lade [agents.md](../agents.md) in deinen Chat-Kontext, wenn du mit diesem Projekt arbeitest!

**agents.md** enthält:
- ✅ 5 kritische Sicherheits-Regeln
- ✅ Phishing-Erkennung
- ✅ Git-Sicherheit (`.gitignore`)
- ✅ Credentials-Handling
- ✅ Effizienz-Regeln (Keine Duplikat-Dokumentationen!)

---

## 📋 **HISTORISCHE DATEN & ARCHIVE**

Alte Dokumentationen, abgeschlossene Migrationen:

- [MIGRATION.md](04_ARCHIVE/MIGRATION.md) - Migration zur neuen Struktur (abgeschlossen)
- [MIGRATION-REPORT.md](04_ARCHIVE/MIGRATION-REPORT.md) - Detaillierter Migrations-Report

---

## 📊 **ÜBERSICHT - Wo finde ich was?**

| Thema | Datei | Typ |
|-------|-------|-----|
| **Projekt-Einstieg** | [00_EINSTIEG/00_Projektüberblick.md](00_EINSTIEG/00_Projektüberblick.md) | Start |
| **VS Code einrichten** | [01_QUICK-START/01_VS-Code-Setup.md](01_QUICK-START/01_VS-Code-Setup.md) | Anleitung |
| **Chrome DevTools Setup** | [01_QUICK-START/02_Chrome-DevTools-Setup.md](01_QUICK-START/02_Chrome-DevTools-Setup.md) | Anleitung |
| **Schnelle Antworten** | [01_QUICK-START/04_Schnell-Referenz.md](01_QUICK-START/04_Schnell-Referenz.md) | Referenz |
| **Vollständige Struktur** | [02_DETAILLIERT/10_Vollständige-Struktur.md](02_DETAILLIERT/10_Vollständige-Struktur.md) | Referenz |
| **Umgebungsvariablen** | [02_DETAILLIERT/11_Umgebungsvariablen.md](02_DETAILLIERT/11_Umgebungsvariablen.md) | Referenz |
| **Chrome MCP Tiefgang** | [01_Erste_Schritte_Testszenarien.md](01_Erste_Schritte_Testszenarien.md) | Anleitung |
| **processOpportunities Payload** | [02_DETAILLIERT/20_ProcessOpportunities_Payload_Completeness.md](02_DETAILLIERT/20_ProcessOpportunities_Payload_Completeness.md) | Check/Referenz |
| **Chat-Templates** | [03_TEMPLATES/Copilot-Chat-Init.md](03_TEMPLATES/Copilot-Chat-Init.md) | Template |
| **Archiv** | [04_ARCHIVE/](04_ARCHIVE/) | Historisch |

---

## 🎯 **FAQ - Häufige Fragen**

### **"Ich bin neu - wo fange ich an?"**
→ Folge dem **QUICK-START** Pfad oben (30 min, alles was du brauchst)

### **"Ich habe einen Fehler bei VS Code"**
→ [VS Code Setup](01_QUICK-START/01_VS-Code-Setup.md) § Error Handling

### **"Ich habe einen Fehler mit Chrome DevTools"**
→ [Chrome DevTools Setup](01_QUICK-START/02_Chrome-DevTools-Setup.md) § Troubleshooting

### **"Wo speichere ich meine Ergebnisse?"**
→ [Schnell-Referenz](01_QUICK-START/04_Schnell-Referenz.md) § Aufgaben

### **"Was darf ich in Git committen?"**
→ [agents.md](../agents.md) § WICHTIGE DATEIEN Tabelle

### **"Ich verstehe die Ordnerstruktur nicht"**
→ [Vollständige Projektstruktur](02_DETAILLIERT/10_Vollständige-Struktur.md)

---

## 🔗 **SCHNELLE LINKS**

**Zum Root-Verzeichnis:**
- [📖 Projekt-Überblick (README)](../README.md)
- [🔐 Sicherheits-Regeln (agents.md)](../agents.md)
- [⚡ Schnelle Hilfe WÄHREND der Arbeit (QUICK-REFERENCE)](01_QUICK-START/04_Schnell-Referenz.md)

**Zu lokalen Ordnern:**
- [💾 .secrets/ (Credentials)](../.secrets/)
- [📝 prompts/ (Workflows)](../prompts/)
- [📊 results/ (Ergebnisse)](../results/)
- [📚 docs/ (Dokumentation)](../docs/)

---

## 📈 **Lern-Pfad für neue Agenten**

```
🚀 START HIER
    ↓
├─→ agents.md laden (Sicherheits-Memory)
│
├─→ QUICK-START durchlaufen (30 min)
│   ├─→ 00_Projektüberblick
│   ├─→ 01_VS-Code-Setup
│   ├─→ 02_Chrome-DevTools-Setup
│   └─→ 04_Schnell-Referenz
│
├─→ ERSTE ANALYSE durchführen
│   (Mit Schnell-Referenz + Chrome Browser)
│
├─→ Bei Fragen / Problemen
│   ├─→ DETAILLIERTE Anleitung
│   └─→ TEMPLATES nutzen
│
└─→ Workflow in prompts/ dokumentieren
    (Damit andere es auch können!)
```

---

## ✨ **Was ist neu in dieser Reorganisation?**

**v2.0 (13. Januar 2026):**
- ✅ Root-Struktur optimiert (weniger Clutter)
- ✅ Subdirectories für logische Gruppierung (00_EINSTIEG, 01_QUICK-START, etc.)
- ✅ Zentrale Navigation über trainings/README.md
- ✅ Duplikate entfernt
- ✅ Klarere Lern-Pfade
- ✅ agents.md mit Effizienz-Regeln erweitert

**Ziel:** Neue Agenten können sofort produktiv arbeiten ohne "Welche Datei lese ich zuerst?" zu fragen 🎯

---

**Für Fragen zu Sicherheit & Best Practices:** → [agents.md](../agents.md)
**Für schnelle Antworten während Arbeit:** → [Schnell-Referenz](01_QUICK-START/04_Schnell-Referenz.md)
- [ ] Chrome-Verbindung getestet
- [ ] Alle MCP Tools verfügbar

---

### [01_Erste_Schritte_Testszenarien.md](./01_Erste_Schritte_Testszenarien.md)
**Dauer:** 60-90 Minuten  
**Level:** Anfänger bis Experte

**Inhalte:**
- Level 1: Einfache Navigation (Warm-up)
- Level 2: VW Konfigurator öffnen
- Level 3: "Online leasen" klicken
- Level 4: duc-vehicle API analysieren
- Level 5: Vollständiger BTO-Workflow
- Advanced Szenarien

**Checkliste:**
- [ ] Level 1 abgeschlossen
- [ ] Level 2 abgeschlossen
- [ ] Level 3 abgeschlossen
- [ ] Level 4 abgeschlossen
- [ ] Level 5 abgeschlossen
- [ ] BTO_duc-vehicle.md aktualisiert

---

## 🚀 Quick Start

### Für Eilige (15 Minuten Schnellstart)

1. **Node.js installieren:**
   ```powershell
   # Download von nodejs.org und installieren
   node --version  # Überprüfen
   ```

2. **MCP Server installieren:**
   ```powershell
   npm install -g @modelcontextprotocol/server-chrome-devtools
   ```

3. **VS Code konfigurieren:**
   - Öffne Settings (`Ctrl + Shift + P` → "Preferences: Open User Settings (JSON)")
   - Füge hinzu:
   ```json
   {
     "github.copilot.chat.mcp.enabled": true,
     "github.copilot.chat.mcp.servers": {
       "chrome-devtools-mcp": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-chrome-devtools"]
       }
     }
   }
   ```

4. **VS Code neu starten** (WICHTIG!)

5. **Ersten Test durchführen:**
   - Copilot Chat öffnen (`Ctrl + Alt + I`)
   - Eingeben: `Öffne Chrome und navigiere zu https://www.google.de`

---

## 📁 Workspace-Struktur

```
AI_WorkDir/
├── credentials.json              # VW Staging Credentials
├── BTO_duc-vehicle_PROMPT.md     # Wiederverwendbarer Workflow-Prompt
├── BTO_duc-vehicle.md            # Ergebnisse der API-Analysen
└── trainings/                    # 📍 SIE SIND HIER
    ├── README.md                 # Diese Datei
    ├── 00_Setup_MCP_Chrome_DevTools.md
    └── 01_Erste_Schritte_Testszenarien.md
```

---

## 🎓 Empfohlene Lernreihenfolge

### Für Anfänger (Gesamt: 2-3 Stunden)

1. **Setup durchführen** (00_Setup_MCP_Chrome_DevTools.md)
   - Alle Installationen
   - Konfiguration
   - Erste Tests
   - ⏱️ 45 Minuten

2. **Level 1-3 absolvieren** (01_Erste_Schritte_Testszenarien.md)
   - Einfache Navigation
   - VW Konfigurator
   - "Online leasen" klicken
   - ⏱️ 30 Minuten

3. **Level 4-5 üben** (01_Erste_Schritte_Testszenarien.md)
   - API-Analyse
   - Vollständiger Workflow
   - ⏱️ 45 Minuten

4. **Eigene URLs testen**
   - Verschiedene Konfigurationen
   - Dokumentation erweitern
   - ⏱️ 30 Minuten

---

### Für Fortgeschrittene (Gesamt: 1-2 Stunden)

1. **Setup-Review** (15 min)
   - Konfiguration überprüfen
   - Optimierungen vornehmen

2. **Level 4-5 direkt** (30 min)
   - duc-vehicle API Analyse
   - Vollständiger Workflow

3. **Advanced Szenarien** (45 min)
   - Verschiedene Modelle testen
   - API-Responses vergleichen
   - Eigene Workflows erstellen

---

## 🔧 Wichtige Dateien

### .secrets/credentials.json
Speichert alle Zugangsdaten (lokal, nicht committen):
```json
{
  "vw_staging": {
      "username": "<VW_STAGING_USERNAME>",
      "password": "<VW_STAGING_PASSWORD>",
    "base_url": "https://cs-stage-vw.lighthouselabs.eu"
  },
  "api_keys": {
      "oneapi_key": "<ONEAPI_KEY>"
  }
}
```

Wichtig: Legen Sie echte Credentials lokal in `.secrets/credentials.json` ab (wird nicht committet) und verwenden Sie hier nur Platzhalter.

### BTO_duc-vehicle_PROMPT.md
Der Haupt-Workflow-Prompt, der alle Schritte definiert:
- Browser öffnen
- Navigieren mit Auth
- "Online leasen" klicken
- duc-vehicle Call analysieren
- Ergebnisse speichern

### BTO_duc-vehicle.md
Die Ergebnis-Dokumentation mit:
- Request/Response Details
- Fahrzeug-Informationen
- Performance-Metriken
- API-Call Historie

---

## 🐛 Troubleshooting

### ❌ "MCP Server not found"
**➡️ Lösung:** Siehe Abschnitt "Troubleshooting" in `00_Setup_MCP_Chrome_DevTools.md`

### ❌ Chrome öffnet nicht
**➡️ Lösung:** Chrome-Profile löschen und Browser manuell schließen

### ❌ "401 Unauthorized"
**➡️ Lösung:**
- Wenn ein HTTP Basic Auth Dialog erscheint: Credentials aus `.secrets/credentials.json` eingeben
- Keine Credentials in die URL schreiben (Browser-History/Logs)

### ❌ duc-vehicle Call nicht gefunden
**➡️ Lösung:** Wartezeiten erhöhen, nach Checkout-Load suchen

**Vollständige Troubleshooting-Guides in den jeweiligen Modulen!**

---

## 📊 Erwartete Ergebnisse

Nach Abschluss des Trainings sollten Sie:

✅ MCP Chrome DevTools Server konfiguriert haben  
✅ Chrome automatisch steuern können  
✅ VW Konfigurator mit Auth öffnen können  
✅ Network Requests monitoren können  
✅ duc-vehicle API Calls analysieren können  
✅ Ergebnisse strukturiert dokumentieren können  
✅ Eigene Workflows erstellen können  

---

## 🎯 Typische Use Cases

### 1. Regressions-Tests
Automatische Überprüfung ob duc-vehicle API nach Updates noch korrekt funktioniert

### 2. Konfigurationsvergleiche
Verschiedene Fahrzeug-Konfigurationen testen und API-Responses vergleichen

### 3. Performance-Monitoring
Response-Zeiten des duc-vehicle Endpoints überwachen

### 4. Dokumentation
Automatische Generierung von API-Dokumentation aus Live-Traffic

### 5. Debugging
Fehleranalyse bei Problemen im Checkout-Flow

---

## 📖 Zusätzliche Ressourcen

### Offizielle Dokumentationen
- **MCP Protocol:** https://modelcontextprotocol.io
- **Chrome DevTools:** https://chromedevtools.github.io/devtools-protocol/
- **GitHub Copilot:** https://docs.github.com/en/copilot
- **Node.js:** https://nodejs.org/docs

### Community
- **GitHub Issues:** Probleme melden und diskutieren
- **VS Code Discord:** Copilot Channel
- **Stack Overflow:** Tag `mcp-server`

---

## 🤝 Feedback und Beiträge

Haben Sie Verbesserungsvorschläge oder Fehler gefunden?

1. Öffnen Sie ein Issue im Projekt-Repository
2. Schlagen Sie Änderungen vor
3. Teilen Sie Ihre Erfahrungen mit dem Team

**Wichtig bei Doku-Änderungen:**
- Pflegen Sie die Versionierung mit (Header: `Version` und `Zuletzt aktualisiert`).
- Ergänzen Sie relevante Änderungen zusätzlich in der Tabelle unter „Version History“.

---

## 📅 Version History

| Version | Datum | Änderungen |
|---------|-------|------------|
| 2.2 | 15.01.2026 | Meta-Format vereinheitlicht (Zuletzt aktualisiert statt Datum) |
| 2.1 | 15.01.2026 | Hinweis: Versionierung bei Doku-Änderungen ergänzt |
| 1.0 | 13.01.2026 | Erste Version erstellt |

---

## ✅ Abschluss-Checkliste

Haben Sie alles durchgearbeitet?

- [ ] Setup-Anleitung (00) gelesen und durchgeführt
- [ ] Alle 5 Test-Levels (01) abgeschlossen
- [ ] BTO_duc-vehicle.md mit Daten befüllt
- [ ] Troubleshooting-Guides gelesen
- [ ] Eigene Konfigurationen getestet
- [ ] Workflow verstanden und anwendbar

---

**Viel Erfolg beim Training!** 🚀🎓

Bei Fragen wenden Sie sich an das Team oder konsultieren Sie die Troubleshooting-Guides.

---

**Erstellt für:** VW BTO duc-vehicle API Analyse  
**Zuletzt aktualisiert:** 15. Januar 2026  
**Version:** 2.2
