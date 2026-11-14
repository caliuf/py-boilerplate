# GitHub CLI

Il repository usa `gh` per PR, issue, check e configurazione. Questa guida privilegia i comandi di sola lettura; le modifiche allo stato GitHub richiedono intenzione esplicita e review.

## Configurazione del repository

Il repository è pubblico e ha:

- merge commit, squash e rebase abilitati;
- cancellazione del branch dopo il merge;
- issues abilitate;
- ruleset `Default` sul branch `main` con PR obbligatoria, review CODEOWNERS e status check richiesti.

Comandi di ispezione:

```bash
gh repo view caliuf/py-boilerplate
gh api repos/caliuf/py-boilerplate/rulesets
gh api repos/caliuf/py-boilerplate/rulesets/<id>
```

## Status check richiesti

Il ruleset richiede:

| Check | Workflow | Cosa copre |
|---|---|---|
| `quality` | `ci.yml` | Formattazione, lint, typing, architettura, docs, workflow, secrets, security |
| `integration-and-coverage` | `ci.yml` | Suite non-E2E, coverage, package check |
| `python-compatibility (3.13)` | `ci.yml` | Matrix Python 3.13 |
| `python-compatibility (3.14)` | `ci.yml` | Matrix Python 3.14 |
| `e2e` | `ci.yml` | Processi reali CLI, API e MCP, più Playwright sulla UI |
| `dependency-review` | `ci.yml` | Review delle dipendenze sulle PR pubbliche |

I nomi devono corrispondere ai job. Se rinomini un job, aggiorna il ruleset nella stessa PR.

## PR

```bash
gh pr list --state open
gh pr view <numero>
gh pr checks <numero>
gh pr diff <numero>
gh pr create --fill
gh pr merge <numero> --squash
```

Prima di creare una PR, verifica lo stato:

```bash
git --no-pager status --short
git --no-pager diff --stat origin/main...HEAD
git --no-pager log --oneline --no-decorate origin/main..HEAD
```

Non fare force-push su un branch con review aperta salvo necessità e accordo.

## Workflow e run

```bash
gh workflow list
gh run list --limit 20
gh run view <run-id> --log-failed
gh run watch <run-id>
```

Per rieseguire un job fallito usa l'interfaccia GitHub o `gh run rerun`, dopo aver capito la causa. Non mascherare un fallimento con un rerun ripetuto.

## Dependabot

```bash
gh pr list --app dependabot
gh pr view <numero>
gh pr checks <numero>
```

Dependabot copre l'ecosistema `uv` (Python) e `npm` (root workspace, `apps/web` e tooling documentale), oltre a `github-actions`. Un aggiornamento patch/minor può essere raggruppato; un major richiede review esplicita, lettura del changelog e suite completa. Controlla sempre versione risolta, licenza, provenienza, vulnerabilità e wheel.

## CodeScene

Il progetto CodeScene Cloud è `87780`: <https://codescene.io/projects/87780/jobs/8428088>. La configurazione MCP sta in `.kilo/kilo.jsonc`; i gate locali sono `just codescene-safeguard`, `just codescene-changeset` e `just codescene-ratchet`. I dettagli sono in [`CODESCENE.md`](CODESCENE.md).

CodeScene non è un check richiesto dal ruleset: richiede OAuth locale e non va esposto in CI. Il ratchet può essere eseguito in un job dedicato con il secret `CODESCENE_API_TOKEN`.

## Sicurezza

Comandi utili:

```bash
gh api repos/caliuf/py-boilerplate --jq '.security_and_analysis'
gh api repos/caliuf/py-boilerplate/dependabot/alerts --jq 'length'
gh api repos/caliuf/py-boilerplate/code-scanning/alerts --jq 'length'
```

Alcune API richiedono scope o piani specifici. Se un comando restituisce 403 o 404, riporta il limite invece di assumere che il controllo sia attivo.

## Ruleset

Il ruleset è configurazione di repository, non codice. Una modifica va fatta con intenzione esplicita e documentata; non aggirarla con bypass o disattivazione temporanea. Il maintainer ha bypass `always` per emergenze, ma l'uso va dichiarato nel report.

Per creare o aggiornare un ruleset, usa l'API GitHub con un payload versionato e verifica il risultato con una lettura successiva. Non incollare token nella shell history.
