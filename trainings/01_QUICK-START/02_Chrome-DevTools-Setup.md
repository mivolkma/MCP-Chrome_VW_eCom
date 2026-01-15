# Chrome MCP Remote Debugging - Problemlösung & Konfiguration

**Version:** 1.1  
**Status:** ✅ Production-Ready  
**Zuletzt aktualisiert:** 15. Januar 2026

---

## 🔴 **Das Problem:**

```
Fehler: Schreibrechte für Chrome beim Start
Verknüpfung: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9333 --user-data-dir="$profileDir"
```

**Ursache:** `$profileDir` wird nicht als Variable interpoliert (Batch-String-Variable wird ignoriert)

---

## ✅ **Lösungen:**

### **Option 1: Batch-Script verwenden (Empfohlen)**

Verwende das vorbereitet Script:

```powershell
# Script ausführen (automatisch die richtige Pfade nutzen)
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
& "$WORKSPACE\chrome-mcp-start.bat"
```

**Was das Script macht:**
- ✓ Setzt `CHROME_PROFILE` korrekt als `$env:USERPROFILE\.cache\chrome-devtools-mcp`
- ✓ Erstellt das Verzeichnis automatisch
- ✓ Prüft Schreibrechte
- ✓ Startet Chrome mit korrekten Optionen

---

### **Option 2: PowerShell-Script**

```powershell
# Script ausführen (automatisch benutzer-spezifisch)
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
powershell -ExecutionPolicy Bypass -File "$WORKSPACE\chrome-mcp-start.ps1"
```

**Oder als Verknüpfung auf Desktop:**
```
Ziel: powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\AI_WorkDir\chrome-mcp-start.ps1"
Ausführen unter: Als Administrator
```

---

### **Option 3: Direkt im Terminal**

```powershell
# Erstelle Profil-Verzeichnis (automatisch benutzer-spezifisch)
$chromeProfil = "$env:USERPROFILE\.cache\chrome-devtools-mcp"
mkdir $chromeProfil -Force

# Starte Chrome
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9333 `
    --user-data-dir="$chromeProfil" `
    --disable-extensions
```

---

## 🔧 **Desktop-Verknüpfung Setup:**

### **A. Batch-Datei-Verknüpfung (Variablen-basiert)**

**Ziel:** `C:\Windows\System32\cmd.exe`  
**Argumente:** `/c "%USERPROFILE%\Documents\AI_WorkDir\chrome-mcp-start.bat"`  
**Arbeitsverzeichnis:** `%USERPROFILE%\Documents\AI_WorkDir`  
**Ausführen unter:** ☑ Als Administrator  

### **B. PowerShell-Verknüpfung (Variablen-basiert)**

**Ziel:** `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`  
**Argumente:** `-ExecutionPolicy Bypass -File "%USERPROFILE%\Documents\AI_WorkDir\chrome-mcp-start.ps1"`  
**Arbeitsverzeichnis:** `%USERPROFILE%\Documents\AI_WorkDir`  
**Ausführen unter:** ☑ Als Administrator  

---

## 📊 **Fehlerbehandlung:**

### **Fehler: "Keine Schreibrechte"**
```
Lösung 1: Führe als Administrator aus
Lösung 2: Änder das Profil-Verzeichnis zu einem beschreibbaren Ort
```

### **Fehler: "Chrome nicht gefunden"**
```
Lösung: Überprüfe ob Chrome unter:
  C:\Program Files\Google\Chrome\Application\chrome.exe
existiert
```

### **Fehler: "Port 9333 bereits in Verwendung"**
```
Lösung 1: Ändere Port in Script (z.B. 9334, 9335)
Lösung 2: Beende existierende Chrome-Instanz:
  Get-Process chrome | Stop-Process -Force
```

---

## 🔍 **Debugging & Verifikation:**

### **Chrome läuft? Port offen?**
```powershell
# Prüfe ob Chrome läuft
Get-Process chrome -ErrorAction SilentlyContinue | Select-Object ProcessName, Id

# Prüfe ob Port 9333 offen ist
netstat -ano | findstr ":9333"

# Oder mit netsh
netsh interface portproxy show all
```

### **Remote Debugging Port zugänglich?**
```powershell
# Öffne Browser und navigiere zu:
http://localhost:9333
```

---

## ✨ **Finale Konfiguration:**

### **Schnellstart - Drei Optionen:**

| Methode | Befehl | Vorteile |
|---------|--------|----------|
| **Batch** | `chrome-mcp-start.bat` | Einfach, zuverlässig |
| **PowerShell** | `chrome-mcp-start.ps1` | Professionell, Logger |
| **Terminal** | `powershell -c "..."` | Direkt, kein File |

### **Empfohlener Workflow:**

```
1. Desktop-Verknüpfung erstellen (Batch-Variante)
2. Mit Rechtsklick → "Als Administrator ausführen"
3. Chrome startet mit Port 9333
4. In VS Code: MCP Server verbindet sich automatisch
```

---

## 📋 **Chrome Start-Parameter Referenz:**

```bash
--remote-debugging-port=9333      # Remote Debugging Port
--user-data-dir="..."             # Profil-Verzeichnis
--disable-extensions              # Keine Extensions
--disable-plugins                 # Keine Plugins
--disable-default-apps            # Keine Standard-Apps
--disable-sync                    # Kein Sync mit Google Account
--no-first-run                    # Kein First-Run Dialog
--no-default-browser-check        # Kein Browser-Check
```

---

**Version:** 1.1  
**Status:** ✅ Getestet  
**Zuletzt aktualisiert:** 15. Januar 2026
