# Setup-Anleitung: MCP Chrome DevTools Server für VW BTO-Analyse

Diese Anleitung zeigt, wie Sie den Chrome DevTools MCP Server in VS Code einrichten, um automatisierte Browser-Tests und API-Analysen durchzuführen.

---

## 📋 Voraussetzungen

- **VS Code** (aktuellste Version)
- **Node.js** (Version 18 oder höher) - [Download](https://nodejs.org/)
- **Google Chrome** (aktuellste Version)
- **GitHub Copilot** Lizenz (für VS Code)

---

## 🔧 Schritt 1: Node.js installieren

1. Laden Sie Node.js von [nodejs.org](https://nodejs.org/) herunter
2. Installieren Sie die LTS-Version
3. Überprüfen Sie die Installation im Terminal:
   ```powershell
   node --version
   npm --version
   ```

Erwartete Ausgabe: `v18.x.x` oder höher

---

## 🛠️ Schritt 2: Chrome DevTools MCP Server installieren

Öffnen Sie ein PowerShell-Terminal und führen Sie aus:

```powershell
npm install -g @modelcontextprotocol/server-chrome-devtools
```

**Hinweis:** Falls Berechtigungsfehler auftreten, führen Sie PowerShell als Administrator aus.

### Installation überprüfen:
```powershell
Get-Command chrome-devtools-mcp
```

Falls der Befehl nicht gefunden wird, prüfen Sie ob die npm global bin directory im PATH ist:
```powershell
npm config get prefix
```

---

## ⚙️ Schritt 3: VS Code User Settings konfigurieren

### 3.1 Settings.json öffnen

1. In VS Code: Drücken Sie `Ctrl + Shift + P`
2. Tippen Sie: `Preferences: Open User Settings (JSON)`
3. Drücken Sie Enter

### 3.2 MCP Server Konfiguration hinzufügen

Fügen Sie folgende Konfiguration in Ihre `settings.json` ein:

```json
{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": {
    "chrome-devtools-mcp": {
      "command": "node",
      "args": [
        "C:\\Users\\[IHR-BENUTZERNAME]\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-chrome-devtools\\dist\\index.js"
      ]
    }
  }
}
```

**🚨 WICHTIG:** Ersetzen Sie `[IHR-BENUTZERNAME]` mit Ihrem Windows-Benutzernamen!

### 3.3 Pfad zum MCP Server ermitteln

Falls Sie den genauen Pfad nicht kennen:

```powershell
npm root -g
```

Hängen Sie dann `\@modelcontextprotocol\server-chrome-devtools\dist\index.js` an.

**Beispiel für Benutzer "mivolkma":**
```
C:\Users\mivolkma\AppData\Roaming\npm\node_modules\@modelcontextprotocol\server-chrome-devtools\dist\index.js
```

### 3.4 Alternative: npx verwenden (empfohlen)

Falls die direkte Pfad-Angabe Probleme macht, verwenden Sie `npx`:

```json
{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": {
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-chrome-devtools"
      ]
    }
  }
}
```

---

## 🔌 Schritt 4: VS Code Erweiterungen installieren

### Erforderliche Extensions:

1. **GitHub Copilot** (erforderlich)
   - Extension ID: `GitHub.copilot`
   - Installation: VS Code → Extensions → Suche nach "GitHub Copilot"

2. **GitHub Copilot Chat** (erforderlich)
   - Extension ID: `GitHub.copilot-chat`
   - Wird meist automatisch mit Copilot installiert

### Installation per Command Line:

```powershell
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
```

---

## 🔄 Schritt 5: VS Code neu starten

**WICHTIG:** Nach der Konfiguration muss VS Code komplett neu gestartet werden!

1. Schließen Sie **alle** VS Code Fenster
2. Starten Sie VS Code neu
3. Öffnen Sie Ihren Workspace: `c:\Users\[IHR-NAME]\Documents\AI_WorkDir`

---

## ✅ Schritt 6: Installation überprüfen

### 6.1 Copilot Chat öffnen

1. Drücken Sie `Ctrl + Alt + I` oder klicken Sie auf das Chat-Symbol in der Sidebar
2. Geben Sie ein: `@workspace /tests`

### 6.2 MCP Tools überprüfen

Fragen Sie den Copilot:

```
Zeige mir alle verfügbaren MCP Chrome Tools
```

**Erwartete Antwort:** Der Copilot sollte Tools wie diese auflisten:
- `mcp_io_github_chr_navigate`
- `mcp_io_github_chr_click`
- `mcp_io_github_chr_evaluate_script`
- `mcp_io_github_chr_list_network_requests`
- `mcp_io_github_chr_take_snapshot`
- etc.

### 6.3 Chrome-Verbindung testen

```
Öffne einen Chrome Browser und navigiere zu https://www.google.de
```

**Erwartetes Verhalten:**
- Ein Chrome-Fenster öffnet sich automatisch
- Die Seite wird geladen
- Copilot bestätigt die Navigation

---

## 🧪 Schritt 7: Erster Test mit BTO duc-vehicle

### 7.1 Credentials vorbereiten

Stellen Sie sicher, dass die Datei `credentials.json` im Workspace existiert:

```json
{
  "vw_staging": {
    "username": "onehub-cms-user",
    "password": "Tp5a38TCiosv",
    "base_url": "https://cs-stage-vw.lighthouselabs.eu"
  }
}
```

### 7.2 Test-URL verwenden

Kopieren Sie diese URL für den ersten Test:

```
https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/energy-sondermodelle/energy?buildabilityStatus=buildable&category=private&carlineId=30450&salesGroupId=36330&trimName=ENERGY&modelId=E392DF$MAAUE0G$GRD8RD8$GW0GW0G&modelVersion=1&modelYear=2026&exteriorId=F14+3K3K&interiorId=F56+++++QT&options=GPAKPAK
```

### 7.3 Ersten API-Call analysieren

Geben Sie im Copilot Chat ein:

```
Verwende die Anleitung aus BTO_duc-vehicle_PROMPT.md und analysiere diese URL:
https://cs-stage-vw.lighthouselabs.eu/de1/konfigurator.html/der-id-5/energy-sondermodelle/energy?buildabilityStatus=buildable&category=private&carlineId=30450&salesGroupId=36330&trimName=ENERGY&modelId=E392DF$MAAUE0G$GRD8RD8$GW0GW0G&modelVersion=1&modelYear=2026&exteriorId=F14+3K3K&interiorId=F56+++++QT&options=GPAKPAK
```

### 7.4 Erwartetes Ergebnis

Der Copilot sollte:
1. ✅ Chrome öffnen
2. ✅ Mit Credentials zur URL navigieren
3. ✅ "Online leasen" Link finden und klicken
4. ✅ Zur Checkout-Seite navigieren
5. ✅ duc-vehicle API-Call abfangen
6. ✅ Request/Response Details extrahieren
7. ✅ Daten in `BTO_duc-vehicle.md` speichern

---

## 🐛 Troubleshooting

### Problem: "MCP Server not found"

**Lösung 1:** Prüfen Sie den Pfad in settings.json
```powershell
npm root -g
```

**Lösung 2:** Verwenden Sie npx statt direktem Pfad (siehe Schritt 3.4)

**Lösung 3:** Installieren Sie den Server neu:
```powershell
npm uninstall -g @modelcontextprotocol/server-chrome-devtools
npm install -g @modelcontextprotocol/server-chrome-devtools
```

---

### Problem: Chrome öffnet nicht

**Lösung 1:** Chrome manuell schließen und erneut versuchen

**Lösung 2:** Chrome-Profile löschen:
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\chrome-devtools-mcp"
```

**Lösung 3:** Prüfen Sie ob Chrome installiert ist:
```powershell
Get-Command chrome
```

---

### Problem: "401 Unauthorized" bei duc-vehicle Call

**Ursache:** Die Seite wurde nicht vollständig geladen oder Authentifizierung fehlt

**Lösung:**
1. Prüfen Sie die credentials.json
2. Warten Sie länger (erhöhen Sie Wartezeiten auf 5-10 Sekunden)
3. Stellen Sie sicher, dass die URL mit Credentials formatiert ist:
   ```
   https://username:password@domain.com
   ```

---

### Problem: VS Code zeigt keine MCP Tools

**Lösung 1:** VS Code komplett neu starten (alle Fenster schließen!)

**Lösung 2:** Prüfen Sie GitHub Copilot Lizenz:
```
Settings → Extensions → GitHub Copilot → Sign in
```

**Lösung 3:** Überprüfen Sie die settings.json Syntax:
- Keine fehlenden Kommas
- Korrekte JSON-Formatierung
- Doppelte Backslashes in Windows-Pfaden: `\\`

---

### Problem: "Cannot find module"

**Lösung:** Installieren Sie Node.js Module global:
```powershell
npm config set prefix $env:APPDATA\npm
npm install -g @modelcontextprotocol/server-chrome-devtools
```

Fügen Sie den npm-Pfad zum System PATH hinzu:
```powershell
$env:PATH += ";$env:APPDATA\npm"
```

---

## 📚 Weitere Ressourcen

- **MCP Dokumentation:** https://modelcontextprotocol.io
- **Chrome DevTools Protocol:** https://chromedevtools.github.io/devtools-protocol/
- **GitHub Copilot Docs:** https://docs.github.com/en/copilot

---

## ✅ Checkliste für erfolgreiche Installation

- [ ] Node.js installiert (v18+)
- [ ] Chrome DevTools MCP Server installiert
- [ ] settings.json konfiguriert
- [ ] GitHub Copilot Extension installiert
- [ ] VS Code neu gestartet
- [ ] MCP Tools im Copilot Chat verfügbar
- [ ] Chrome-Verbindung erfolgreich getestet
- [ ] credentials.json vorhanden
- [ ] Erster duc-vehicle Test erfolgreich

---

## 🎯 Nächste Schritte

Nach erfolgreicher Installation:

1. Lesen Sie `BTO_duc-vehicle_PROMPT.md` für die Workflow-Details
2. Testen Sie verschiedene VW Konfigurator-URLs
3. Analysieren Sie die Ergebnisse in `BTO_duc-vehicle.md`
4. Experimentieren Sie mit anderen Browser-Automatisierungen

---

**Version:** 1.0  
**Datum:** 13. Januar 2026  
**Erstellt für:** VW BTO duc-vehicle API Analyse
