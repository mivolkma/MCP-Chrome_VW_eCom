# 🔐 Secrets Directory

Dieses Verzeichnis enthält alle sensiblen Informationen und ist durch `.gitignore` geschützt.

## Struktur

```
.secrets/
├── .gitignore           # Verhindert Commits
├── credentials.example.json  # Template (wird geteilt)
└── credentials.json     # ⚠️ NICHT teilen! (ignoriert)
```

## Dateiinhalt

### credentials.json
Lokale Datei mit echten Zugangsdaten:
- VW Staging Benutzername & Passwort
- API Keys
- OAuth Tokens
- **WIRD NIE COMMITTED!**

### credentials.example.json
Vorlage zum Teilen:
- Zeigt die Struktur
- Enthält Platzhalter
- Sichere Vorlage für andere User

## ⚠️ Sicherheitsregeln

✅ **Erlaubt zu teilen:**
- `.gitignore`
- `credentials.example.json`
- Architektur-Dokumentation

❌ **NIEMALS teilen:**
- `credentials.json`
- Alle Dateien mit echten Secrets
- API Keys oder Tokens

## Workflow für neue User

1. Clone Repository
2. `cp credentials.example.json credentials.json`
3. Editiere credentials.json mit echten Werten
4. Datei wird automatisch von Git ignoriert

---

**Version:** 1.0  
**Datum:** 13. Januar 2026
