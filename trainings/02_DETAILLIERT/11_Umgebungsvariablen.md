# 🔧 Umgebungsvariablen & Benutzer-Konfiguration

**Version:** 1.0  
**Status:** ✅ Production-Ready  
**Datum:** 13. Januar 2026

---

## 📍 Automatische Pfad-Erkennung

Das Projekt verwendet **Windows-Umgebungsvariablen**, um benutzer-unabhängig zu funktionieren. Sie müssen **NICHTS manuell konfigurieren** - alles funktioniert automatisch!

---

## 🔑 Wichtige Variablen

### **`$env:USERPROFILE`** (Dein Windows-Benutzerverzeichnis)
```powershell
# Beispiel Ausgabe (wird automatisch ersetzt):
C:\Users\[USERNAME]

# PowerShell-Befehl zum Prüfen:
echo $env:USERPROFILE
```

Wird automatisch ersetzt durch Deinen tatsächlichen Benutzernamen.

### **`$env:USERNAME`** (Dein Windows-Benutzername)
```powershell
# Beispiel Ausgabe:
actualWindowsUser

# PowerShell-Befehl zum Prüfen:
echo $env:USERNAME
```

### **`$env:COMPUTERNAME`** (Dein Computer-Name)
```powershell
# PowerShell-Befehl zum Prüfen:
echo $env:COMPUTERNAME
```

---

## 📁 Automatisch aufgelöste Pfade

Diese Variablen werden automatisch in alle Skripte eingebunden:

```powershell
# WORKSPACE (Projekt-Verzeichnis)
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"

# Beispiel: C:\Users\actualWindowsUser\Documents\AI_WorkDir (für Benutzer "actualWindowsUser")
# Beispiel: C:\Users\max\Documents\AI_WorkDir             (für Benutzer "max")
# Beispiel: C:\Users\anna\Documents\AI_WorkDir            (für Benutzer "anna")
```

```powershell
# RESULTS (Analyseergebnisse)
$RESULTS = "$WORKSPACE\results"

# SECRETS (Credentials)
$SECRETS = "$WORKSPACE\.secrets"

# PROMPTS (Workflows)
$PROMPTS = "$WORKSPACE\prompts"

# CHROME PROFILE
$CHROME_PROFILE = "$env:USERPROFILE\.cache\chrome-devtools-mcp"
```

---

## 💡 Verwendung in Dokumenten

### **Beispiel 1: Datei ausführen**
```powershell
# ❌ FALSCH - hardcodierter Pfad
& "C:\Users\actualWindowsUser\Documents\AI_WorkDir\chrome-mcp-start.ps1"

# ✅ RICHTIG - Variable benutzen
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
& "$WORKSPACE\chrome-mcp-start.ps1"
```

### **Beispiel 2: Ergebnisse speichern**
```powershell
# ❌ FALSCH - hardcodierter Pfad
$result | Out-File "C:\Users\actualWindowsUser\Documents\AI_WorkDir\results\analysis.md"

# ✅ RICHTIG - Variable benutzen
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
$result | Out-File "$WORKSPACE\results\bto-duc-vehicle\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')\analysis.md"
```

### **Beispiel 3: Batch-Datei mit Variablen**
```batch
REM Batch-Variablen benutzen
set WORKSPACE=%USERPROFILE%\Documents\AI_WorkDir
set CHROME_PROFILE=%USERPROFILE%\.cache\chrome-devtools-mcp

mkdir "%CHROME_PROFILE%" 2>nul

REM Chrome starten mit Variablen
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=9333 ^
    --user-data-dir="%CHROME_PROFILE%" ^
    --disable-extensions
```

---

## 📝 Checkliste für neue Dokumentation

Wenn Sie neue Dokumentationen schreiben:

### ✅ **DO - Variablen verwenden:**
```
✓ $env:USERPROFILE\Documents\AI_WorkDir
✓ $WORKSPACE\results\
✓ $WORKSPACE\prompts\
✓ $WORKSPACE\.secrets\
✓ $env:USERPROFILE\Desktop\
✓ $env:USERPROFILE\Downloads\
```

### ❌ **DON'T - Hardcodierte Pfade:**
```
✗ C:\Users\actualWindowsUser\Documents\AI_WorkDir
✗ C:\Users\actualWindowsUser\results\
✗ C:\Users\[beliebiger Name]\Documents\
```

### 📝 **Beschreibende Alternative:**
```
Wenn Variablen nicht möglich sind:
- Schreib: "$env:USERPROFILE\Documents\AI_WorkDir"
- Oder: "Ihr Workspace-Verzeichnis"
- Oder: "[WORKSPACE]/results/" (mit erklärung was [WORKSPACE] ist)
```

---

## 🔄 Umgebungsvariablen testen

### **Alle relevanten Variablen prüfen:**
```powershell
# Schneller Überblick
@{
    USERPROFILE = $env:USERPROFILE
    USERNAME = $env:USERNAME
    COMPUTERNAME = $env:COMPUTERNAME
    WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
    CHROME_PROFILE = "$env:USERPROFILE\.cache\chrome-devtools-mcp"
} | Format-Table
```

### **Workspace-Struktur automatisch erstellen:**
```powershell
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"

# Erstelle alle notwendigen Verzeichnisse
@(
    "$WORKSPACE\.secrets",
    "$WORKSPACE\prompts\active",
    "$WORKSPACE\prompts\templates",
    "$WORKSPACE\results",
    "$WORKSPACE\docs",
    "$WORKSPACE\trainings"
) | ForEach-Object {
    mkdir $_ -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Host "✓ $_ erstellt"
}
```

---

## 🎯 Für jeden Benutzer automatisch angepasst

| Benutzer | $env:USERPROFILE | $WORKSPACE |
|----------|------------------|-----------|
| actualWindowsUser | C:\Users\actualWindowsUser | C:\Users\actualWindowsUser\Documents\AI_WorkDir |
| max | C:\Users\max | C:\Users\max\Documents\AI_WorkDir |
| anna | C:\Users\anna | C:\Users\anna\Documents\AI_WorkDir |
| admin | C:\Users\admin | C:\Users\admin\Documents\AI_WorkDir |

**Das Projekt funktioniert für ALLE Benutzer - keine Anpassung nötig!**

---

## ⚠️ Wichtig für Dokumentation

### **Immer verwenden in Dokumentation:**
- `$env:USERPROFILE` für absolute Pfade
- `$WORKSPACE` für Projekt-relative Pfade
- Relative Pfade (z.B. `results/`, `prompts/`) wenn vom Workspace-Verzeichnis aus

### **Niemals verwenden:**
- Hardcodierte Benutzernamen (mivolkma, max, anna, etc.)
- Absolute Pfade mit C:\ wenn der Benutzer anders heißt
- Annahmen über lokale Verzeichnis-Struktur

---

## 📚 Weiterführende Links

- [agents.md](agents.md) - Sicherheits-Anweisungen
- [VERSIONS.md](VERSIONS.md) - Versionierungsschema
- [README.md](README.md) - Projekt-Überblick

---

**WICHTIG:** Diese Datei erklärt, warum das Projekt für alle Benutzer funktioniert. Schreiben Sie IMMER Dokumentationen mit Variablen statt hardcodierten Pfaden!
