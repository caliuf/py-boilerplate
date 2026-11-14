# CodeScene

Code Health e debito tecnico per gli agenti, via MCP e REST API. Decisione: [ADR-0010](../architecture/adr/0010-codescene.md). CodeScene non è un hook autonomo: i gate locali lo incapsulano nelle recipe `just`, mentre i tool MCP restano obbligatori quando l'MCP è connesso invece di indovinare la maintainability.

Progetto Cloud: `87780` — <https://codescene.io/projects/87780/jobs/8428088>. Baseline misurata il 2026-11-14: Hotspot Code Health `9.10`, Average Code Health `9.76`.

## Due livelli

- **MCP locale**: analisi fresca sul working tree. Usato da `just codescene-safeguard` (staged/modificati) e `just codescene-changeset` (branch vs base).
- **REST API**: ratchet di progetto (`just codescene-ratchet`), perché Hotspot e Average non sono esposti dai tool MCP. Il ratchet legge la scansione Cloud, che è in ritardo rispetto ai commit locali e per questo **non** è un gate di commit/push.

## Configurazione MCP

Il server è in `.kilo/kilo.jsonc`:

```json
{
  "mcp": {
    "codescene": {
      "type": "local",
      "command": ["npx", "-y", "@codescene/codehealth-mcp"],
      "enabled": true,
      "environment": {
        "CS_DEFAULT_PROJECT_ID": "87780"
      }
    }
  }
}
```

L'estensione VS Code "CodeScene CodeHealth MCP" serve Copilot, non Kilo. Kilo parla solo al server registrato in `kilo.jsonc`.

## Prerequisiti

1. Il server `codescene` risulta connesso nella sessione; riavvia o ricarica i server MCP se lo hai appena aggiunto.
2. Sessione autenticata. Se i tool rispondono unauthenticated, esegui `npx -y @codescene/codehealth-mcp auth` (apre il browser) o chiama il tool MCP `login`.
3. Il progetto Cloud `87780` punta al remote `https://github.com/caliuf/py-boilerplate.git`.
4. Per il ratchet serve un REST API token: `CODESCENE_API_TOKEN`, `CODESCENE_TOKEN` o `~/.codescene/token`. L'OAuth dell'MCP non è la fonte prevista per il ratchet; se il token REST manca, il ratchet fallisce con un messaggio esplicito.

Se l'MCP non è raggiungibile, riporta il blocker. Non dichiarare un check CodeScene passato.

## Uso operativo

| Momento | Comando / tool | Cosa blocca |
|---|---|---|
| Prima di un commit di codice toccato dall'agente | `just codescene-safeguard` o `pre_commit_code_health_safeguard` | Regressioni su staged/modificati |
| Prima di aprire una PR | `just codescene-changeset` o `analyze_change_set` | Branch vs base, verdetto improved/degraded/stable |
| Periodicamente o prima di un refactor | `just codescene-ratchet` | Hotspot e Average sotto i floor |

I tool `*_for_project*` richiedono CodeScene Core (OAuth o PAT) e il progetto selezionato. Score, review, safeguard e change-set girano in locale sul working tree.

## Soglie e ratchet

`.codescene-thresholds` contiene i floor:

```text
HOTSPOT_THRESHOLD=9.10
AVERAGE_THRESHOLD=9.76
```

`just codescene-ratchet`:

- fallisce se Hotspot o Average sono sotto il floor;
- se sono sopra, aggiorna il file e fallisce intenzionalmente, così il nuovo floor viene committato;
- non abbassa mai una soglia.

La baseline è reale, non un 10.0 inventato. I punteggi possono solo salire; un refactor che migliora il progetto alza il floor con un commit dedicato.

## CI

Nessun workflow corrente esegue il gate MCP: richiede una sessione OAuth locale e non va esposto come secret. Il ratchet può essere aggiunto a un workflow dedicato con un repository secret `CODESCENE_API_TOKEN`:

```yaml
- name: CodeScene ratchet
  env:
    CODESCENE_API_TOKEN: ${{ secrets.CODESCENE_API_TOKEN }}
    CODESCENE_PROJECT_ID: "87780"
  run: tools/scripts/codescene-ratchet.sh
```

Non committare token, contenuto di `~/.codescene/token` o configurazioni OAuth.

## Ignore

`.codesceneignore` esclude `docs/init/`, virtualenv, dipendenze Node, coverage, build e `.kilo/`. Il blueprint congelato e il tooling agentico non sono codice applicativo misurato dal ratchet.

## Diagnostica

- `just codescene-safeguard` e `just codescene-changeset` passano per `.kilo/scripts/codescene_gate.py`, che parla MCP su stdio, estrae `quality_gates` dal payload e restituisce `0` passed, `1` gate falliti, `2` tool non raggiungibile.
- Per un file degradato, usa il tool MCP `code_health_review` o `code_health_score`.
- Se il gate segnala un file `degraded`, rifattorizza o ripristina il comportamento; non aggirare il gate.
