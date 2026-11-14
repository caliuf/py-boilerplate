# Memoria di progetto

## Identità

- Repository: `caliuf/py-boilerplate`.
- Scopo: boilerplate Python agent-first derivato da `ts-boilerplate`, con il Vademecum Python in `docs/init/`.
- Caso d'uso dimostrativo: `hello-world` su CLI, API HTTP e MCP.
- Distribuzione: un solo package, `py_boilerplate`, con tre entry point.

## Obiettivi stabili

- Architettura a confini verificati: dominio puro, application layer, porte e adapter.
- Validazione runtime ai confini con Pydantic.
- Typing rigoroso con mypy strict.
- TDD e suite comportamentale con contract test cross-surface.
- Gate locali e CI che impediscono scorciatoie.
- Documentazione gerarchica e memory bank portabile.

## Vincoli

- Python minimo 3.13; pin 3.14.5; CI su 3.13 e 3.14.
- `uv` è l'unico package manager; `uv.lock` è versionato.
- Nessuna UI browser, nessun database, nessuna coda, nessun worker.
- Nessuna chiamata a servizi esterni a runtime.
- La prosa non usa hard wrap.
- `docs/init/` è congelato.
- Il maintainer in `CODEOWNERS` è il decisore finale.

## Stato sintetico

- Dominio, contratti, CLI, API, MCP e package check sono implementati e verdi.
- La suite locale copre unit, integration, contract ed E2E.
- La coverage misurata è 100% linee e 100% branch; la baseline è 95/90.
- La CI include quality, integration-and-coverage, python-compatibility, e2e e dependency-review.
- La slow lane include CodeQL, gitleaks storico, guard e link check.
- CodeScene non è configurato per questo repository.
- La licenza non è ancora stata scelta.

## Prossimi passi possibili

- Scegliere la licenza.
- Aggiungere un caso d'uso reale in un progetto derivato.
- Valutare CodeScene se il maintainer adotta un progetto Cloud.
- Aggiungere una UI solo con una nuova PDR e una nuova ADR.
