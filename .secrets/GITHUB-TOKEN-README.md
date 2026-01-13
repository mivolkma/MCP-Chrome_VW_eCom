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
```
GitHub → Settings → Developer settings → Personal access tokens (classic)
→ "Generate new token (classic)"
→ Scopes:
  ✅ repo (Full control of repositories)
  ✅ read:org (Read org membership)
  ✅ workflow (GitHub Actions)
→ "Generate token"
```

### **Schritt 2: Token kopieren (wird NUR 1x angezeigt!)**
```
github_pat_11A2K3VBQ0trudsR863J3q_5Qj5YZgV3b3pRmmLWNfwjqlRWoR8Pr9...
↑ Kopieren bevor Seite geschlossen wird!
```

### **Schritt 3: Token lokal speichern**

**Option A: PowerShell**
```powershell
$token = "github_pat_DEIN_TOKEN_HIER"
$token | Out-File "$env:USERPROFILE\Documents\AI_WorkDir\.secrets\github_token" -Encoding UTF8 -NoNewline
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

### **Mit Token in Remote-URL (nicht empfohlen, aber möglich):**
```powershell
$token = Get-Content ".secrets\github_token" -Raw
$user = "mivolkma"
$repo = "MCP-Chrome_VW_eCom"

git remote set-url origin "https://$($user):$($token)@github.com/$($user)/$($repo).git"
git push origin master
```

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
