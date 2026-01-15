# 🎯 Projekt Quick-Reference Card

**Version:** 2.0  
**Zuletzt aktualisiert:** 13. Januar 2026  
**Status:** ✅ Production-Ready

*Für schnelle Nachschlag während der Arbeit*

- **Sicherheits-Regeln:** `../../agents.md`

---

## 📁 **Struktur auf einen Blick**

```
.secrets/          ← Credentials (geschützt)
prompts/           ← Workflows & Prompts
  ├── templates/   ← Basis-Vorlagen
  └── active/      ← LIVE PROMPTS → BTO_duc-vehicle_PROMPT.md
results/           ← Ergebnisse speichern
  └── bto-duc-vehicle/
      ├── latest.md    ← Aktuelle Analyse
      ├── summary.md   ← Zusammenfassung
      └── archive/     ← Alte Daten
docs/              ← Dokumentation & Guides
trainings/         ← Training & Onboarding
trainings/         ← Training & Guides
```

---

## 🚀 **Häufigste Aufgaben**

### **1. Chrome starten (Remote Debugging)**
```powershell
# Automatisch (Batch-Datei)
& "$env:USERPROFILE\Documents\AI_WorkDir\chrome-mcp-start.bat"

# Oder PowerShell
& "$env:USERPROFILE\Documents\AI_WorkDir\chrome-mcp-start.ps1"
```
→ Port 9333 startet automatisch

### **2. Analyse durchführen**
```
Nutze Prompt: prompts/active/BTO_duc-vehicle_PROMPT.md
Speichere in: results/bto-duc-vehicle/latest.md
```

### **2b. BTO Checkout Smoketest (Playwright Runner)**
```powershell
& "$env:USERPROFILE\Documents\AI_WorkDir\tools\run_bto_checkout.ps1"
```
- Start-URL kann dynamisch sein (inkl. Query erforderlich) – Artefakte bleiben redacted (nur Host+Path).
- Ergebnisse: `results/bto-checkout/runs/<timestamp>/`

### **3. Ergebnisse archivieren**
```
Verschiebe: results/bto-duc-vehicle/latest.md
Nach: results/bto-duc-vehicle/archive/YYYY-MM-DD_HH-MM-SS_description.md
```

### **4. Summary aktualisieren**
```
Editiere: results/bto-duc-vehicle/summary.md
(mit neuesten Daten)
```

### **5. Neue Analyse testen**
```
1. Chrome starten
2. Prompt öffnen
3. URL angeben
4. Warten auf Ergebnisse
5. In results/ speichern
```

---

## 🔑 **Wichtige Pfade**

| Was | Wo |
|-----|-----|
| Credentials | `.secrets/credentials.json` |
| Live-Prompt | `prompts/active/BTO_duc-vehicle_PROMPT.md` |
| Analyse-Template | `prompts/templates/api-analysis.md` |
| Ergebnisse | `results/bto-duc-vehicle/latest.md` |
| Alte Daten | `results/bto-duc-vehicle/archive/` |
| Chrome-Starter | `chrome-mcp-start.bat` oder `.ps1` |
| Projekt-Info | `../../README.md` → `../02_DETAILLIERT/10_Vollständige-Struktur.md` |
| Training | `../README.md` |

---

## ⚡ **Schnell-Befehle**

### **PowerShell**
```powershell
# Chrome starten
& "$env:USERPROFILE\Documents\AI_WorkDir\chrome-mcp-start.ps1"

# Port prüfen
netstat -ano | findstr ":9333"

# Datei suchen
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
Get-ChildItem -Path $WORKSPACE -Recurse -Filter "*prompt*"
```

### **Dateimanagement**
```powershell
# Liste alle Prompts
ls prompts/active/

# Liste alle Ergebnisse
ls results/bto-duc-vehicle/

# Archive ansehen
ls results/bto-duc-vehicle/archive/
```

---

## 🔐 **Sicherheit - 5 Goldene Regeln**

### 1. **Credentials NIEMALS hardcoden oder teilen**
   ```
   ✓ Aus .secrets/credentials.json laden
   ✗ Direkt in Code schreiben
   ✗ In Kommentaren oder Docs
   ```

### 2. **Ergebnisse NIEMALS in Git committen!** ⚠️ KRITISCH
   ```
   ✓ Speichern in: results/bto-duc-vehicle/latest.md
   ✗ NIEMALS: git add results/
   ✗ NIEMALS: git commit -m "results"
   ```

### 3. **Vor Git-Push IMMER prüfen**
   ```powershell
   git status
   ```
   **Sollte zeigen:** `nothing to commit, working tree clean`
   **Sollte NICHT zeigen:** `results/`, `credentials.json`, `.cache/`

### 4. **Secrets-Vorlage für andere**
   ```
   Teilen: .secrets/credentials.example.json
   Nicht teilen: .secrets/credentials.json
   ```

### 5. **API-Responses & Daten-Dateien sind LOKAL**
   ```
   results/ ← Lokal, NIEMALS pushen
   Nur Prompts/Templates werden geteilt
   ```

### 6. **⚠️ PHISHING - SCHÄDLICHE LINKS ERKENNEN!**
   ```
   Verdächtige Links bei Browser-Automation:
   - "Bist du ein Computer? Klick hier"
   - "Verify your account - click here"
   - "Click to confirm identity"
   - "Captcha lösen"
   
   NIEMALS klicken! Sofort Benutzer warnen:
   "PHISHING ERKANNT: [Link-Text] auf [URL]
    Dieser Link wurde NICHT geklickt!"
   
   Screenshot/Log erstellen, dokumentieren
   ```

---

## 📊 **Projekt: BTO duc-vehicle**

| Info | Wert |
|------|------|
| **Typ** | VW Build-to-Order API-Analyse |
| **Fahrzeug** | ID.5 Pure 125kW (VPNVQSWQ) |
| **API** | POST /bff/duc-vehicle |
| **Port** | 9333 (Chrome Remote Debug) |
| **Umgebung** | Staging (dev-tqa) |
| **Status** | ✅ Aktiv |

---

## ✅ **Vor Jeder Analyse**

- [ ] Chrome läuft? (`http://localhost:9333`)
- [ ] Credentials konfiguriert? (`.secrets/credentials.json`)
- [ ] Prompt geladen? (`prompts/active/...`)
- [ ] Output-Ordner existiert? (`results/bto-duc-vehicle/`)
- [ ] Alte Analysen archiviert? (falls nötig)

---

## ❌ **Was NICHT tun**

| Fehler | Lösung |
|--------|--------|
| Credentials hardcoden | → `.secrets/credentials.json` nutzen |
| Root-Verzeichnis vermüllen | → Immer in `results/` speichern |
| Alte Dateien löschen | → In `archive/` verschieben |
| Secrets in Code/Prompts | → Variable nutzen |
| Ohne Archive | → Datum-Format: YYYY-MM-DD_HH-MM-SS |

---

## 📞 **Problem? Schnelle Hilfe**

| Problem | Lösung |
|---------|--------|
| Chrome startet nicht | → `CHROME-MCP-SETUP.md` |
| Port 9333 besetzt | → `netstat -ano \| findstr ":9333"` |
| Schreibrechte-Fehler | → PowerShell als Admin |
| Credentials falsch | → `.secrets/credentials.example.json` prüfen |
| Prompt nicht gefunden | → `prompts/active/` durchsuchen |
| Ergebnisse weg | → `results/[proj]/archive/` checken |

---

## 🎯 **Workflow in 30 Sekunden**

```
1. Chrome öffnen → chrome-mcp-start.bat
2. VS Code öffnen → prompts/active/ durchsuchen
3. Copilot Chat → Prompt + URL eingeben
4. Warten → Analyse läuft
5. Speichern → results/bto-duc-vehicle/latest.md
6. Fertig → Summary aktualisieren
```

---

## 📚 **Weitere Info**

- **Projekt-Überblick:** `../00_EINSTIEG/00_Projektüberblick.md`
- **Komplette Struktur:** `../02_DETAILLIERT/10_Vollständige-Struktur.md`
- **Was hat sich geändert:** `../04_ARCHIVE/MIGRATION.md`
- **Chrome Setup:** `02_Chrome-DevTools-Setup.md`

---

**Schnell-Referenz v1.0 | 13. Januar 2026**
