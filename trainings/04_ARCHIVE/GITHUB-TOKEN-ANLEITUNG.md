# 🔑 GitHub Token Setup - Schritt-für-Schritt Anleitung

**Version:** 1.0  
**Status:** ✅ Production-Ready  
**Zuletzt aktualisiert:** 13. Januar 2026

Ausführliche Anleitung zum Erstellen, Speichern und Verwenden von GitHub Personal Access Tokens für sichere Git Push/Pull Operationen.

---

## 📋 Überblick

| Thema | Datei | Beschreibung |
|-------|-------|-------------|
| **Diese Anleitung** | `GITHUB-TOKEN-ANLEITUNG.md` | Schritt-für-Schritt (du bist hier) |
| **Template** | `.secrets/github_token.example` | Muster für die echte Datei |
| **Dokumentation** | `.secrets/GITHUB-TOKEN-README.md` | Technische Details & Troubleshooting |
| **Script** | `setup-github-token.ps1` | Automatisierte Konfiguration |

---

## 🎯 **5 MINUTEN QUICK-START**

### **1️⃣ Token auf GitHub erstellen**
```
Gehe zu: https://github.com/settings/tokens
→ Klick "Generate new token (classic)"
→ Gib einen Namen ein (z.B. "MCP-Chrome-VW-eCom")
→ Wähle diese Scopes:
   ✅ repo (Full control of repositories)
   ✅ read:org (Read org membership, teams)
   ✅ workflow (Update GitHub Actions)
→ Klick "Generate token"
→ KOPIERE DEN TOKEN! (wird nur 1x angezeigt!)
```

### **2️⃣ Token lokal speichern**

**Option A - PowerShell (automatisch):**
```powershell
# Öffne PowerShell und gehe zum Workspace:
cd "$env:USERPROFILE\Documents\AI_WorkDir"

# Führe das Setup-Script aus:
.\setup-github-token.ps1

# Script fragt dich nach deinem Token
# → Eingeben und Enter
# → Script speichert es automatisch
# → Fragt ob du gleich pushen willst
```

**Option B - Manuell:**
```powershell
# Öffne PowerShell und gehe zum Workspace:
cd "$env:USERPROFILE\Documents\AI_WorkDir"

# Speichere deinen Token (ersetze XXXXX mit deinem echten Token):
$token = "github_pat_11A2K3VBQ0trudsR863J3q_5Qj5YZgV3b3pRmmLWNfwjqlRWoR8Pr9..."
$token | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline

# Verifiziere (sollte "github_token" zeigen):
ls ".secrets\github_token"
```

### **3️⃣ Git konfigurieren**
```powershell
# Falls du nicht das Script verwendet hast:
$token = Get-Content ".secrets\github_token" -Raw
git remote set-url origin "https://mivolkma:$($token)@github.com/mivolkma/MCP-Chrome_VW_eCom.git"
```

### **4️⃣ Pushen!**
```powershell
git push origin master
# ✅ Erfolgreich!
```

---

## 🔐 **Detaillierter Prozess**

### **Schritt 1: Neuen Token auf GitHub erstellen**

**URL:**
```
https://github.com/settings/tokens
```

**Anleitung:**
1. Oben rechts → Klick auf dein Profil
2. Settings → Developer settings → Personal access tokens (classic)
3. "Generate new token (classic)" Button
4. Gib einen Namen ein:
   ```
   Name: MCP-Chrome-VW-eCom-Token (oder ähnlich)
   Expiration: 90 days (empfohlen) oder No expiration
   ```

**Scopes auswählen (WICHTIG!):**

| Scope | Warum? |
|-------|--------|
| ✅ **repo** | Voller Zugriff auf deine Repositories |
| ✅ **read:org** | Lesen von Org & Team-Memberships |
| ✅ **workflow** | Update GitHub Actions & Workflows |
| ❌ admin:org | Nicht nötig |
| ❌ admin:repo_hook | Nicht nötig |

Dann: "Generate token" Button klicken

**⚠️ WICHTIG:**
```
Der Token wird danach NICHT mehr angezeigt!
→ KOPIEREN und sofort speichern!
→ Browser-Tab nicht schließen, bis Token lokal ist!
```

---

### **Schritt 2: Token lokal speichern**

**Wo speichern?**
```
.secrets/github_token  (wird ignoriert ✅)
↑ Nicht github_token.example!
```

**Wie speichern?**

**Option A - PowerShell (Empfohlen):**
```powershell
# Token einlesen (aus Browser kopiert):
$token = Read-Host "Gib deinen Token ein" -AsSecureString | ConvertFrom-SecureString

# Oder direkt:
$token = "github_pat_11A2K3VBQ0trudsR863J3q_5Qj5YZgV3b3pRmmLWNfwjqlRWoR8Pr9..."

# Speichern:
$token | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline

# Verifizieren:
Get-Content ".secrets\github_token"
# Sollte zeigen: github_pat_xxxxx...
```

**Option B - VS Code:**
1. Öffne VS Code
2. Datei → "Open File" → `.secrets/github_token` (wird als neue Datei erstellt)
3. Kopiere rein: `github_pat_xxxxx...`
4. Speichern (Ctrl+S)

**Option C - Text Editor:**
1. Notepad öffnen
2. Token paste
3. Speichern als: `C:\Users\[USERNAME]\Documents\AI_WorkDir\.secrets\github_token`
4. **WICHTIG:** Keine Newlines am Ende!

---

### **Schritt 3: Git konfigurieren**

**Automatisch (Script):**
```powershell
.\setup-github-token.ps1
# Macht alles automatisch für dich
```

**Manuell:**
```powershell
# Token laden
$token = Get-Content ".secrets\github_token" -Raw
$user = "mivolkma"
$repo = "MCP-Chrome_VW_eCom"

# Remote URL setzen
git remote set-url origin "https://$($user):$($token)@github.com/$($user)/$($repo).git"

# Verifizieren
git remote -v
# Sollte zeigen: https://mivolkma:github_pat_xxxxx...@github.com/mivolkma/MCP-Chrome_VW_eCom.git
```

---

### **Schritt 4: Pushen!**

```powershell
git status
# Sollte zeigen: "On branch master, Your branch is ahead of 'origin/master'"

git push origin master
# ✅ Successfully pushed!
```

---

## 🚀 **Schnelle Befehle**

```powershell
# Token speichern (PowerShell)
$token = "dein_token_hier"
$token | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline

# Setup durchführen
.\setup-github-token.ps1

# Manuell konfigurieren
$token = Get-Content ".secrets\github_token" -Raw
git remote set-url origin "https://mivolkma:$($token)@github.com/mivolkma/MCP-Chrome_VW_eCom.git"

# Pushen
git push origin master

# Status checken
git remote -v
git log --oneline -3
```

---

## 🔒 **Sicherheits-Checklist**

### **MUSS BEACHTET WERDEN:**

- ❌ **NIEMALS** Token im Chat posten
- ❌ **NIEMALS** Token in Dateien hardcoden
- ❌ **NIEMALS** Token in `.md` Dateien speichern
- ❌ **NIEMALS** Token in Git committen
- ✅ **IMMER** Token in `.secrets/github_token` speichern
- ✅ **IMMER** `.secrets/github_token` wird ignoriert (`.gitignore`)
- ✅ **IMMER** Token regelmäßig regenerieren (monatlich empfohlen)

### **Verifikation:**

```powershell
# Token sollte NICHT in Git sichtbar sein:
git status
# → Sollte .secrets/github_token NICHT anzeigen

# Token sollte NICHT in Dateien sein:
grep -r "github_pat_" . --exclude-dir=.git
# → Sollte NICHTS finden außer .secrets/github_token

# Token sollte existieren:
Test-Path ".secrets\github_token"
# → $True
```

---

## 🔄 **Token erneuern (Rotation)**

Regelmäßig (z.B. monatlich) Token wechseln:

### **Alten Token löschen:**
```
GitHub → Settings → Developer settings → Personal access tokens
→ Dein Token → Delete → Confirm
```

### **Neuen Token erstellen:**
```
(Siehe Schritt 1 oben)
```

### **Datei updaten:**
```powershell
# Neuen Token kopieren
$newToken = "github_pat_NEW_TOKEN_HERE"

# In Datei speichern
$newToken | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline

# Verifizieren
Get-Content ".secrets\github_token"
```

### **Neu pushen:**
```powershell
git push origin master
```

---

## ⚠️ **NOTFALL: Token kompromittiert!**

Wenn du merkst, dass dein Token öffentlich war:

### **1. SOFORT auf GitHub löschen:**
```
GitHub → Settings → Developer settings → Personal access tokens
→ Dein kompromittierter Token → Delete
```

### **2. Neuen Token erstellen** (siehe Schritt 1)

### **3. Lokal updaten:**
```powershell
$newToken = "github_pat_NEW_TOKEN..."
$newToken | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline
```

### **4. Testen:**
```powershell
git push origin master
# Sollte funktionieren
```

**WICHTIG:** Wenn Token im Chat gepostet wurde:
- Token kann nicht mehr genutzt werden (GitHub deaktiviert ihn automatisch)
- Aber: Neuen Token immer noch erstellen für Sicherheit!

---

## 🐛 **Troubleshooting**

### **Problem: "fatal: Authentication failed"**
```powershell
# Lösung 1: Token-Format prüfen
Get-Content ".secrets\github_token"
# Muss mit "github_pat_" starten

# Lösung 2: Token in Remote korrekt?
git remote -v
# Muss zeigen: https://mivolkma:github_pat_...@github.com/...

# Lösung 3: Token erneuern
# (Siehe Token erneuern Abschnitt)
```

### **Problem: "Permission denied (publickey)"**
```powershell
# Dein SSH-Key ist nicht richtig
# Nutze stattdessen Token über HTTPS:
git remote set-url origin "https://mivolkma:$token@github.com/mivolkma/MCP-Chrome_VW_eCom.git"
```

### **Problem: "remote: Repository not found"**
```powershell
# Repo-Name prüfen:
git remote -v
# Sollte zeigen: MCP-Chrome_VW_eCom

# Oder neue Remote setzen:
git remote remove origin
git remote add origin "https://mivolkma:$token@github.com/mivolkma/MCP-Chrome_VW_eCom.git"
```

---

## 📚 **Weitere Resourcen**

- [GitHub Docs: Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- `.secrets/GITHUB-TOKEN-README.md` - Technische Details
- `setup-github-token.ps1` - Automation Script
- `agents.md` § Fehler 4 - Sicherheits-Regeln

---

**Bereit?** → Folge den 5 Minuten Quick-Start oben! 🚀

