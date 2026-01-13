# 🔌 VS Code Setup für MCP Chrome DevTools

**Version:** 1.0  
**Status:** ✅ Production-Ready  
**Datum:** 13. Januar 2026

---

## 📋 Schnell-Übersicht

Das Projekt benötigt **3 Hauptkomponenten** in VS Code:

1. **GitHub Copilot** Extension (für KI-Unterstützung)
2. **GitHub Copilot Chat** Extension (für Chat-Interface)
3. **Chrome DevTools MCP Server** (für Browser-Automation)

---

## 🚀 Quick-Start (5 Minuten)

### **Schritt 1: Extensions installieren**

Öffne VS Code und drücke `Ctrl + Shift + X` (Extensions-Seite)

Suche und installiere:
```
1. GitHub Copilot        (ID: GitHub.copilot)
2. GitHub Copilot Chat   (ID: GitHub.copilot-chat)
```

### **Schritt 2: MCP Chrome DevTools installieren**

Öffne PowerShell und führe aus:
```powershell
npm install -g @modelcontextprotocol/server-chrome-devtools
```

### **Schritt 3: Settings konfigurieren**

In VS Code: `Ctrl + Shift + P` → "Preferences: Open User Settings (JSON)"

Füge hinzu:
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

### **Schritt 4: Workspace neuladen**

1. Schließe **ALLE** VS Code Fenster
2. Öffne VS Code neu
3. Öffne den Workspace: `$env:USERPROFILE\Documents\AI_WorkDir`

✅ **Fertig!**

---

## 📚 Detaillierte Dokumentation

Für ausführliche Step-by-Step-Anleitung mit Fehlerbehandlung:
→ [../00_Setup_MCP_Chrome_DevTools.md](../00_Setup_MCP_Chrome_DevTools.md)

---

## 🔧 Alle erforderlichen Extensions

### **1. GitHub Copilot** ⭐ ERFORDERLICH
```
Extension ID: GitHub.copilot
Beschreibung: AI-Powered Code Completion
```
**Installation:**
- **VS Code Marketplace:** [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- **Oder direkt:** `code --install-extension GitHub.copilot`

**Was es macht:**
- Code-Completion in Echtzeit
- Basis für Copilot Chat

### **2. GitHub Copilot Chat** ⭐ ERFORDERLICH
```
Extension ID: GitHub.copilot-chat
Beschreibung: Chat Interface für GitHub Copilot
```
**Installation:**
- **Wird oft automatisch mit Copilot installiert**
- **Oder manuell:** `code --install-extension GitHub.copilot-chat`

**Was es macht:**
- Chat-Interface (Ctrl + Alt + I)
- MCP Server-Verbindungen
- Browser-Automation

### **3. Chrome DevTools Protocol Support** ✅ OPTIONAL
```
Extension ID: msjsdiag.debugger-for-chrome (falls gewünscht)
Beschreibung: Chrome Debugging in VS Code
```

**Nicht zwingend nötig** (wird über MCP Server gehandhabt)

---

## 🌐 MCP Marketplace (Was ist das?)

### **Was ist MCP (Model Context Protocol)?**

MCP ist ein Protokoll, das LLM-Modellen (wie Copilot) Zugriff auf externe Tools gibt:

```
┌─────────────────────────────────────────┐
│  GitHub Copilot (LLM-Modell)           │
│  (Kann Fragen beantworten & testen)     │
└────────────┬──────────────────────────┘
             │ (MCP Protocol)
    ┌────────▼────────┐
    │  MCP Servers    │
    │  ────────────   │
    │ • Chrome Tools  │
    │ • File Tools    │
    │ • Code Tools    │
    └─────────────────┘
```

### **Chrome DevTools MCP Server**

Das Projekt nutzt einen **MCP Server für Chrome**, der folgende Tools bereitstellt:

```powershell
✅ mcp_io_github_chr_navigate       # Seite laden
✅ mcp_io_github_chr_click          # Element klicken
✅ mcp_io_github_chr_take_snapshot  # Screenshot
✅ mcp_io_github_chr_evaluate_script # JavaScript ausführen
✅ mcp_io_github_chr_get_network_requests # Network-Calls
✅ mcp_io_github_chr_wait_for       # Auf Element warten
```

### **Aktivierung in VS Code**

Die Aktivierung erfolgt **automatisch** über die `settings.json`:

```json
{
  "github.copilot.chat.mcp.enabled": true,  // MCP aktivieren
  "github.copilot.chat.mcp.servers": {      // MCP Server definieren
    "chrome-devtools-mcp": {                 // Server-Name
      "command": "npx",                      // Wie starten?
      "args": ["@modelcontextprotocol/server-chrome-devtools"]
    }
  }
}
```

---

## 🛠️ Installationsschritte im Detail

### **A. Extensions installieren (Grafisch)**

```
1. VS Code öffnen
2. Ctrl + Shift + X (Extensions)
3. Suche: "GitHub Copilot"
4. Klick auf "Install"
5. Klick auf "Install" für "GitHub Copilot Chat" (falls angezeigt)
6. Warten bis Installation abgeschlossen
```

### **B. Extensions installieren (Terminal)**

```powershell
# GitHub Copilot
code --install-extension GitHub.copilot

# GitHub Copilot Chat
code --install-extension GitHub.copilot-chat
```

### **C. Chrome DevTools MCP Server installieren**

```powershell
# Administrator-PowerShell öffnen und ausführen:
npm install -g @modelcontextprotocol/server-chrome-devtools

# Installation überprüfen:
npm list -g @modelcontextprotocol/server-chrome-devtools
```

### **D. VS Code Settings aktualisieren**

```
1. Ctrl + Shift + P
2. Typ: "Preferences: Open User Settings (JSON)"
3. Enter
4. Folgende Zeilen hinzufügen (oder ersetzen):

{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": {
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-chrome-devtools"]
    }
  }
}

5. Speichern: Ctrl + S
```

### **E. VS Code neu starten**

```powershell
# WICHTIG: Alle VS Code Fenster schließen!
# Dann neu öffnen:
code $env:USERPROFILE\Documents\AI_WorkDir
```

---

## ✅ Verifikation der Installation

### **Check 1: Extensions überprüfen**

```
1. Ctrl + Shift + X (Extensions)
2. Suche nach "GitHub Copilot" und "Copilot Chat"
3. Sollte "Installed" (grün) zeigen, nicht "Install"
```

### **Check 2: Settings überprüfen**

```
1. Ctrl + Shift + P
2. Typ: "Preferences: Open User Settings (JSON)"
3. Überprüfe, ob folgende Zeilen vorhanden sind:
   - "github.copilot.chat.mcp.enabled": true
   - "chrome-devtools-mcp" unter "mcp.servers"
```

### **Check 3: Chrome DevTools Test**

```
1. Copilot Chat öffnen: Ctrl + Alt + I
2. Frag: "@workspace Zeige mir alle verfügbaren MCP Chrome Tools"
3. Sollte Tools wie "mcp_io_github_chr_navigate" auflisten
```

### **Check 4: Browser-Test**

```
1. Copilot Chat öffnen: Ctrl + Alt + I
2. Frag: "Öffne einen Chrome Browser und navigiere zu https://www.google.de"
3. Sollte Chrome-Fenster öffnen und Seite laden
```

---

## 🚨 Häufige Fehler & Lösungen

### **Fehler 1: "MCP servers not available"**

**Lösung:**
```json
✓ Stelle sicher, dass in settings.json vorhanden:
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": { ... }

✓ VS Code komplett neu starten
✓ Alle VS Code Fenster schließen
✓ Neu öffnen
```

### **Fehler 2: "npx: command not found"**

**Lösung:**
```powershell
# Node.js nicht installiert?
# Download: https://nodejs.org/

# Oder npm PATH-Problem:
npm config get prefix
# Dann zu System PATH hinzufügen

# Überprüfen:
node --version
npm --version
```

### **Fehler 3: "Chrome DevTools MCP not found"**

**Lösung:**
```powershell
# Server nicht installiert?
npm install -g @modelcontextprotocol/server-chrome-devtools

# Überprüfen:
npm list -g @modelcontextprotocol/server-chrome-devtools

# Oder direkt mit npx testen:
npx -y @modelcontextprotocol/server-chrome-devtools --version
```

### **Fehler 4: GitHub Copilot nicht lizenziert**

**Lösung:**
```
1. Überprüfe: github.com → Settings → Billing
2. GitHub Copilot muss "Active" sein
3. Falls nicht: GitHub Copilot aktivieren
4. Dann VS Code neu starten
```

---

## 📊 Was wird wo installiert?

| Komponente | Ort | Status |
|-----------|-----|--------|
| GitHub Copilot | VS Code Extensions | ✅ Lokal |
| Copilot Chat | VS Code Extensions | ✅ Lokal |
| Chrome DevTools MCP | `npm global` (~%APPDATA%\npm) | ✅ Global |
| VS Code Settings | `%APPDATA%\Code\User\settings.json` | ✅ Lokal |

---

## 🔄 Nach erfolgreicher Installation

1. ✅ Öffne [README.md](../../README.md) für Projekt-Überblick
2. ✅ Lese [../../agents.md](../../agents.md) für Sicherheits-Regeln
3. ✅ Starte mit [04_Schnell-Referenz.md](04_Schnell-Referenz.md)
4. ✅ Nutze [../03_TEMPLATES/Copilot-Chat-Init.md](../03_TEMPLATES/Copilot-Chat-Init.md) für Chat-Initialisierung

---

## 📚 Weitere Ressourcen

- **Vollständige Setup-Anleitung:** [../00_Setup_MCP_Chrome_DevTools.md](../00_Setup_MCP_Chrome_DevTools.md)
- **MCP Protokoll Dokumentation:** https://modelcontextprotocol.io
- **GitHub Copilot Docs:** https://docs.github.com/en/copilot
- **Chrome DevTools Protocol:** https://chromedevtools.github.io/devtools-protocol/
- **VS Code MCP Dokumentation:** https://code.visualstudio.com/docs

---

## 🎓 Zusammenfassung

```
┌─────────────────────────────────────────────────────┐
│  VS Code Setup für VW BTO Analyse                   │
├─────────────────────────────────────────────────────┤
│  1. Extensions installieren (5 min)                 │
│  2. MCP Server installieren (2 min)                 │
│  3. Settings konfigurieren (2 min)                  │
│  4. VS Code neu starten (1 min)                     │
│  5. Installation testen (2 min)                     │
├─────────────────────────────────────────────────────┤
│  ✅ Gesamt: ~12 Minuten                            │
│  ✅ Alles benutzer-automatisch                      │
│  ✅ Keine Admin-Rechte nötig (normalerweise)       │
└─────────────────────────────────────────────────────┘
```

---

**Status:** Vollständig dokumentiert und getestet ✅

*Zuletzt aktualisiert: 13. Januar 2026*
