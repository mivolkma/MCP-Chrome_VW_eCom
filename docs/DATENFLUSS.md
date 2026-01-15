# Datenfluss: Konfigurator → Checkout → Backends

Ziel: Den *tatsächlichen* Datenfluss zwischen Frontend und den wichtigsten Backend-Services im eCom/BTO-Checkout nachvollziehbar darstellen.

Hinweise:
- URLs/Query-Parameter/Token werden in unseren Artefakten redacted (Host+Path), keine Auth/Cookies.
- `processOpportunities` und `duc-leasing` werden typischerweise erst in späteren Checkout-Schritten getriggert (z.B. beim Klick auf „Zum Leasingantrag“).
- Optional: Wenn der Benutzer eingeloggt/registriert ist, kann ein Auth/Identity-Service Profil-/Stammdaten liefern (Prefill für Formularfelder).

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "16px"}, "flowchart": {"curve": "linear", "nodeSpacing": 55, "rankSpacing": 70}} }%%
flowchart LR
  U["Benutzer"]
  %% Frontend
  subgraph FE["Frontend"]
    direction TB
    C["Configurator<br/>Summary"] -->|CTA| E["Checkout App<br/>Journey"]
    E --> F["Forms<br/>(Personal/Dealer/Pickup)"]
    E --> P["Pricing UI"]
  end

  U -->|Click: Online leasen| C

  %% Backend
  subgraph BE["Backend"]
    direction TB
    AUTH_A["authproxy\n/app/authproxy/.../authenticated"]
    AUTH_U["authproxy\n/app/authproxy/.../user"]
    BFFN["/bff/navigation"]
    BFFC["/bff/checkout"]
    BFFV["/bff/duc-vehicle"]

    BFFF["/bff-forms/*"]

    DEAL["Dealer/SDS"]
    PICK["Pickup"]

    WC["Webcalc"]

    PO["processOpportunities"]
    DL["duc-leasing"]

    FSAG["FSAG Antrag"]
  end

  %% Fluss: Checkout orchestriert API Calls
  E -->|GET| AUTH_A
  E -->|GET| AUTH_U
  AUTH_U -->|"Prefill wenn eingeloggt"| F
  E -->|GET| BFFN
  E -->|GET| BFFC
  E -->|GET| BFFV

  F -->|POST/PUT| BFFF

  E -->|GET| DEAL
  E -->|GET| PICK

  P -->|"GET (Rate)"| WC

  %% Late-stage Calls
  E -->|"POST (Payload redacted)"| PO
  E -->|POST: Leasingantrag| DL
  DL -->|"Response: Link + Token (presence)"| E
  E -->|Navigate to Link| FSAG

  %% Evidence in this repo (optional view)
  subgraph EV["Automation/Evidence (dieses Repo)"]
    direction TB
    R["Runner: tools/execute_smoketest.py"]
    T["network_trace.jsonl"]
    A["api/*.json"]
    TC["technical_checkpoints.md/.json"]
  end

  R -.->|"Playwright Network Tap (optional)"| E
  R -->|writes| T
  R -->|writes| A
  R -->|writes| TC
```

## Mapping zu unseren Artefakten
- `network_trace.jsonl`: korrelierte Requests/Responses (inkl. Statuscodes) pro Run.
- `api/*.json`: redacted JSON-Evidence für ausgewählte Endpoints (z.B. `duc-leasing`, `processOpportunities`, Dealer/Pickup/Vehicle, wenn getriggert).
- `technical_checkpoints.md/.json`: maschinenlesbare/lesbare Auswertung (2xx/5xx, Treffer pro Bucket, Link/Token-Presence, etc.).
