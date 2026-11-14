# ADR-0001 — Stack Python e tooling

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

Il progetto nasce come derivazione Python di `ts-boilerplate`. Serve un toolchain unico, riproducibile e verificabile da agenti, senza moltiplicare package manager, linter o type checker. La data di riferimento è il 14 novembre 2026; le versioni sono state verificate sull'indice PyPI e sull'ambiente di sviluppo.

## Decisione

Adottiamo:

- Python minimo 3.13, pinnato a 3.14.5 in `.python-version`; CI su 3.13 e 3.14.
- `uv` come unico gestore di progetto, environment, Python e lockfile. `uv.lock` è versionato.
- `pyproject.toml` come unico manifest; build backend Hatchling.
- Ruff come formatter e linter, con regole selezionate e motivazione esplicita.
- mypy in modalità strict come type checker autorevole.
- pytest con `pytest-asyncio` per i test, coverage.py con branch coverage.
- Import Linter per i confini architetturali e deptry per le dipendenze dichiarate.
- Pydantic v2 e pydantic-settings ai confini; FastAPI per l'API; MCP Python SDK v2 per il server; structlog per il logging.
- `just` come unica interfaccia operativa.
- pymarkdown e cspell (su Node, solo tooling documentale) per la documentazione; lychee per i link; actionlint e zizmor per i workflow; gitleaks, Bandit e pip-audit per la sicurezza.

## Conseguenze

- Un solo lockfile e un solo environment per progetto; niente `requirements.txt`, Poetry, PDM o pip-tools in parallelo.
- Ruff sostituisce Black, isort, Flake8 e autopep8; non vengono affiancati.
- mypy è l'unica autorità di typing; non aggiungiamo basedpyright o ty come gate equivalente.
- Le versioni Python supportate sono quelle testate in CI. Allargare il range richiede una PR dedicata e una compatibility suite.
- Il tooling esterno è pinnato in `.mise.toml` e verificato da `just doctor`.

## Alternative considerate

- **Poetry o PDM**: aggiungono un secondo modello di project management senza un beneficio misurato.
- **Black + isort + Flake8**: più tool con configurazioni sovrapposte; Ruff copre le stesse regole con un solo comando.
- **basedpyright o ty come secondo gate**: costo di manutenzione e rumore senza una lacuna concreta di mypy.
- **setuptools**: funziona, ma Hatchling è più semplice e non richiede un `setup.py`.
