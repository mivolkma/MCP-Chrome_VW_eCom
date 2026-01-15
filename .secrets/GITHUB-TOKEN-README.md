# GitHub Token Management

**Version:** 1.0  
**Status:** ✅ Production-Ready  
**Zuletzt aktualisiert:** 13. Januar 2026

Sichere Verwaltung von GitHub Personal Access Tokens für Git Push/Pull Operationen.

---

## 📋 Übersicht

| Datei | Zweck | Git |
|-------|-------|-----|
| `github_token` | Aktueller Token (LOKAL) | ❌ IGNORED |
| `github_token.example` | Template & Anleitung | ✅ JA |
| `GITHUB-TOKEN-README.md` | Diese Datei | ✅ JA |

---

## 🔑 Token erstellen & speichern

### **Schritt 1: Neuen Token auf GitHub erstellen**

Du kannst entweder **Fine-grained** (empfohlen) oder **Classic** verwenden.

#### Option A: Fine-grained Personal Access Token (empfohlen)
Für `git push` reicht ein **Fine-grained PAT** mit Repo-Zugriff + minimalen Berechtigungen.

Navigation:
```
GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
→ "Generate new token"
```

Empfohlene Einstellungen:
- **Resource owner**: dein User oder deine Org
- **Repository access**: "Only select repositories" → dieses Repo auswählen
- **Permissions**:
   - **Contents: Read and write** (notwendig für Push)
   - **Actions: Read and write** (nur nötig, wenn du `.github/workflows/*.yml` pushen/ändern willst)
   - Alles andere: nur wenn wirklich benötigt

Hinweis:
- Fine-grained Tokens können strenger sein (z.B. Branch-Schutz, Org-Policies). Wenn Push trotz Token scheitert, prüfe Repo-/Org-Regeln oder nutze testweise Classic.

#### Option B: Personal access token (classic)
Navigation:
```
GitHub → Settings → Developer settings → Personal access tokens (classic)
→ "Generate new token (classic)"
```

Scopes (typisch/legacy):
- ✅ `repo`
- ✅ `workflow` (nötig, wenn du `.github/workflows/*.yml` pushen/ändern willst)
- ✅ `read:org` (nur wenn du Repo-Zugriff via Org/Teams brauchst)

### **Schritt 2: Token kopieren (wird NUR 1x angezeigt!)**
```
<DEIN_GITHUB_PAT_TOKEN>
↑ Token kopieren bevor Seite geschlossen wird!
```

### **Schritt 3: Token lokal speichern**

## ✅ Copy/Paste Quick-Setup (empfohlen, Remote bleibt clean)

Ziel: **Kein Token in Remote-URL**, keine Token-Ausgaben im Terminal, Credentials im **OS Credential Store** (Git Credential Manager).

```powershell
cd "$env:USERPROFILE\Documents\AI_WorkDir"

# 1) Remote sauber halten (OHNE Token)
git remote set-url origin "https://github.com/<GITHUB_USERNAME>/<REPO_NAME>.git"

# 2) Token lokal ablegen (nur für Setup-Script; Datei ist durch .gitignore geschützt)
$token = Read-Host "GitHub PAT Token (wird nicht angezeigt)" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
$plain | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline

# 3) Credentials in den Credential Manager schreiben (Remote bleibt clean)
.\setup-github-token.ps1

# 4) Optional: Token-Datei wieder entfernen (Credentials bleiben im OS-Store)
# Remove-Item ".secrets\github_token" -Force

# 5) Push testen
git push origin master
```

**Option A: PowerShell**
```powershell
$token = Read-Host "GitHub PAT Token (wird nicht angezeigt)" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
$plain | Out-File "$env:USERPROFILE\Documents\AI_WorkDir\.secrets\github_token" -Encoding UTF8 -NoNewline
```

**Option B: Manuell**
- Öffne `.secrets/github_token`
- Ersetze Inhalt mit deinem Token
- Speichern & Fertig!

---

## 🔒 Sicherheit - MUSS beachtet werden!

### **NIEMALS:**
```
❌ Token in agents.md, README.md, oder andere Dateien schreiben
❌ Token im Chat-Verlauf posten
❌ Token in Prompts oder Ergebnisse speichern
❌ Token in Git committen (würde funktionieren, ist aber UNSICHER!)
```

### **IMMER:**
```
✅ Token NUR in .secrets/github_token (wird ignoriert)
✅ Token LOKAL halten
✅ Regelmäßig regenerieren (monatlich empfohlen)
✅ Alt-Tokens löschen wenn neu erstellt
```

---

## 🔄 Git Push/Pull mit Token

### **Automatisch (mit Credential Manager):**
```powershell
cd "$env:USERPROFILE\Documents\AI_WorkDir"
git push origin master
# Git fragt nach Credentials
# → GitHub-Benutzername eingeben
# → GitHub Personal Access Token eingeben (aus .secrets/github_token)
```

### **Mit Token in Remote-URL**
Nicht empfohlen: Der Token landet dann in `.git/config` und kann versehentlich in Logs/Screenshots auftauchen.
Nutzen Sie stattdessen den Git Credential Manager oder das Script `setup-github-token.ps1` (speichert Credentials sicher im OS-Store, Remote-URL bleibt clean).

---

## 🚨 NOTFALL - Token kompromittiert!

**Wenn du merkst, dass dein Token öffentlich war:**

1. **SOFORT auf GitHub löschen:**
   ```
   GitHub → Settings → Developer settings → Personal access tokens
   → "Delete" → Bestätigen
   ```

2. **Neuen Token erstellen** (siehe oben)

3. **Lokale Datei updaten:**
   ```powershell
   $newToken | Out-File ".secrets\github_token" -Encoding UTF8 -NoNewline
   ```

4. **Weitermachen** - Token ist neu und sicher!

---

## 📝 Token-Rotation (regelmäßig!)

**Jeden Monat oder bei Bedarf:**

1. Neuen Token erstellen (GitHub)
2. `.secrets/github_token` updaten
3. Alten Token auf GitHub löschen
4. Fertig!

---

## 🔐 `.gitignore` Check**

```powershell
# Verifiziere, dass .secrets/ ignoriert wird:
cat .gitignore | grep secrets

# Output sollte zeigen:
# .secrets/credentials.json
# .secrets/github_token
```

---

## 📚 Referenzen

- GitHub Docs: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- agents.md § Fehler 4: Niemals Secrets in Chat!
- .secrets/README.md: Credentials-Management

---

**WICHTIG:** Diese Datei wird geteilt (OK in Git). Der Token NICHT!
