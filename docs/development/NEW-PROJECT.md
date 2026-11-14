# Adottare il boilerplate

Questa checklist trasforma `py-boilerplate` in un progetto reale. Non saltare i passi che riguardano decisioni: il boilerplate è un punto di partenza, non una scelta di prodotto già fatta.

## 1. Decisioni iniziali

- Scegli la licenza e aggiungi il file `LICENSE`.
- Definisci il nome del progetto, il package Python e il prefisso degli errori.
- Decidi le superfici reali: CLI, API, MCP, job, UI. Rimuovi quelle che non servono.
- Scrivi la prima PDR sul prodotto e la prima ADR sull'architettura.
- Sostituisci il contenuto di `docs/PROJECT.md`.

## 2. Rinominare i placeholder

Cerca e sostituisci in modo controllato:

| Placeholder | Nuovo valore |
|---|---|
| `py-boilerplate` | nome del progetto o del comando |
| `py_boilerplate` | nome del package Python |
| `py-boilerplate-api` | entry point API, se resta |
| `py-boilerplate-mcp` | entry point MCP, se resta |
| `hello-world` | nome del primo caso d'uso reale |
| `HelloWorldInput`, `HelloWorldOutput` | DTO reali |
| `urn:py-boilerplate:error:` | URN del progetto |
| `@caliuf` in `CODEOWNERS` | maintainer o team reale |
| `caliuf/py-boilerplate` nei link | URL del nuovo repository |

Aggiorna anche `docs/INDEX.md`, `README.md`, `SECURITY.md`, `conventions.conf` e i test che citano i placeholder.

## 3. Rimuovere il blueprint

Quando il progetto non è più un boilerplate:

- rimuovi `docs/init/` e il riferimento nell'indice;
- rimuovi `docs/development/NEW-PROJECT.md` o sostituiscilo con la guida del progetto;
- rimuovi le ADR/PDR dimostrative se non descrivono più il progetto reale;
- mantieni la memory bank e aggiornala.

## 4. Configurare GitHub

- Crea il repository pubblico o privato e aggiorna il remote.
- Configura il ruleset con i check reali del nuovo progetto.
- Abilita Dependabot, dependency graph, secret scanning e push protection quando disponibili.
- Verifica che `CODEOWNERS` protegga i file di gate.
- Aggiorna il workflow CI se cambi job o nomi dei check.

## 5. Configurare la qualità

- Mantieni Ruff, mypy strict, pytest, coverage, Import Linter e deptry.
- Aggiorna i contratti Import Linter quando cambi i bounded context.
- Imposta la baseline di coverage sul valore reale del nuovo progetto, senza abbassare le soglie esistenti.
- Aggiorna `.python-version` e la matrix CI solo dopo aver verificato dipendenze e wheel.
- Aggiungi una ADR per ogni dipendenza significativa.

## 6. Configurare l'ambiente

- Aggiorna `.env.default` e `.env.example` con le variabili reali.
- Non committare segreti.
- Aggiorna `bin/` con il nome del comando reale.
- Verifica `just setup` e `just doctor` su una clone pulita.

## 7. Prima esecuzione completa

```bash
just setup
just doctor
just ci
```

`just ci` deve passare su una clone pulita, senza modifiche non committate e senza tool mancanti.

## 8. Primo ciclo agentico reale

Esegui almeno un task completo con un agente:

1. briefing;
2. lettura delle guide;
3. TDD;
4. `just precommit`;
5. `just prepush`;
6. PR e review umana;
7. report finale con output verbatim.

Correggi le parti del processo che risultano ambigue. Il boilerplate è vivo solo se il ciclo funziona davvero.
