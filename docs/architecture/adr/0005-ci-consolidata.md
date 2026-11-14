# ADR-0005 — CI consolidata e slow lane di sicurezza

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

Il repository è pubblico e sviluppato in gran parte da agenti. Servono gate deterministici, veloci sul diff e completi prima del merge. CodeQL, full-history secret scanning e link check esterni sono costosi e non devono rallentare ogni push. La configurazione GitHub deve essere riproducibile e verificabile.

## Decisione

La pipeline è divisa in tre workflow:

- `ci.yml` su pull request, push su `main` e dispatch manuale:
  - `quality`: Ruff format/lint, shellcheck, mypy, deptry, lock check, Import Linter, docs, workflow, secrets e security.
  - `integration-and-coverage`: suite unit, integration, contract, smoke, coverage e package check.
  - `python-compatibility`: matrix 3.13 e 3.14.
  - `e2e`: processi reali per CLI, API e MCP.
  - `dependency-review`: solo su PR pubbliche.
- `security.yml` settimanale o manuale: CodeQL per Python e gitleaks sulla storia completa.
- `scheduled.yml` settimanale o manuale: guard report-only e link check esterni.

La CI sincronizza con `uv sync --locked` e non modifica il lockfile. Le action sono pinnate a SHA completi e hanno permission minime. Il ruleset di `main` richiede i check `quality`, `integration-and-coverage`, `python-compatibility`, `e2e` e `dependency-review`.

## Conseguenze

- Il merge è bloccato da check nominati e stabili.
- CodeQL e la scansione della storia non rallentano ogni push.
- Un lockfile non aggiornato fa fallire la CI invece di essere corretto dal runner.
- La compatibilità Python è verificata su tutte le versioni dichiarate.
- La pipeline non pubblica artefatti né esegue deploy.

## Alternative considerate

- **CodeQL a ogni push**: più costoso e lento senza un beneficio proporzionato su un repository piccolo.
- **Un unico workflow monolitico**: più semplice da leggere, ma non consente check separati e paralleli.
- **Merge queue**: utile con molti agenti in parallelo; oggi il collo di bottiglia è la review umana, quindi la rimandiamo.
- **Rilascio automatico del package**: non esiste un consumatore esterno; il package check basta.
