# Vademecum per progetti Python sviluppati con agenti AI

> Documento riutilizzabile come base per nuovi repository.
> **MUST** = requisito standard; **SHOULD** = default derogabile tramite ADR; **MAY** = facoltativo o dipendente dal progetto.
>
> Questa versione adatta all'ecosistema Python il vademecum TypeScript di riferimento. Mantiene il modello *Guides, Gates, Guards* (3G), le contromisure ai failure modes degli agenti AI e la governance del repository, sostituendo le scelte specifiche Node/TypeScript con strumenti e convenzioni Python.
>
> Date, versioni e stato dei progetti citati sono point-in-time: **riverificarli a ogni bootstrap**. La versione verificata di questo documento è il **13 novembre 2026**. Non aggiornare automaticamente le versioni senza verificare anche la compatibilità delle dipendenze applicative, dei wheel nativi, dei sistemi di deploy e degli strumenti di sviluppo.

---

## 1. Modello operativo: Guides, Gates, Guards (3G)

Tutto ciò che governa il lavoro dell'agente è di tre tipi. Questo modello è la chiave di lettura dell'intero documento: ogni regola SHOULD essere classificabile in una delle tre categorie, e il criterio guida è **spostare il più possibile dalle guide ai gate**.

| Tipo | Cosa è | Quando agisce | Affidabilità |
|------|--------|---------------|--------------|
| ↪️ **Guides** | Regole in linguaggio naturale: `AGENTS.md`, questo vademecum, ADR/PDR | Contesto iniziale del lavoro | **Non affidabili al 100%**: l'agente le ignora una parte delle volte |
| 🔄 **Gates** | Controlli deterministici che **bloccano** codice non conforme: lint, typecheck, test, coverage, controlli architetturali, hook, CI | Durante il lavoro, a ogni commit/push/PR | Deterministici: la parte **più importante** |
| ↩️ **Guards** | Procedure di fallback (tipicamente schedulate) per ciò che sfugge ai gate | Dopo il lavoro | Ultima linea di difesa contro il degrado |

### Principi operativi

1. **Gate-first.** Se una regola può essere espressa come controllo automatico bloccante, non deve vivere solo come istruzione testuale. Le regole architetturali stanno in Import Linter, non solo nei README.
2. **Soglie a cricchetto (ratchet).** Le soglie di qualità (coverage, code health, budget di tempo) possono solo **salire**, mai scendere. Dopo ogni miglioramento della salute del codebase, l'agente alza la soglia nello stesso lavoro o in uno dedicato.
3. **Divieto di aggiramento.** Un agente che fallisce ripetutamente un gate senza saper rimediare cerca workaround: salta test, abbassa soglie, estende ignore-list, usa `SKIP`, `--no-verify` o commenti di suppression generici. Questo è il failure mode più pericoloso: i divieti devono essere espliciti nelle guide (§ 8), i file che definiscono i gate devono essere protetti (§ 11) e le guide devono insegnare **il rimedio**, non solo il divieto (TDD, procedure di fix, § 6).
4. **Mai lavorare sotto soglia.** Non si inizia lavoro nuovo su un codebase con gate rossi: prima si ripristina la salute, poi si sviluppa la feature.
5. **Loop engineering > prompt engineering.** L'intero processo è un loop da ingegnerizzare: retrospettive che aggiornano le guide, guard che creano task, cricchetti che alzano i gate. L'obiettivo non è la velocità iniziale ma **non degradare nel tempo**.
6. **L'umano decide** le tre cose ad alto leverage: *cosa* costruire, *come* lato prodotto, *cosa è abbastanza buono*. Tutto il resto è automatizzabile.
7. **Bias verso il progresso.** Meglio rilasciare ciò che è utile anche se imperfetto e iterare sul feedback reale, che inseguire la prima versione perfetta.
8. **Il typing non è una validazione runtime.** Le annotazioni Python aiutano l'analisi statica, ma il runtime non le applica automaticamente. Ogni dato esterno deve essere validato al confine, anche quando una funzione è annotata con un tipo preciso (§ 3, *Contratti e dati esterni*).

---

## 2. Scelte tecniche fondamentali

### Stack predefinito

| Area | Scelta |
|---|---|
| Linguaggio | Ultima versione stabile di **Python**, con versione esatta fissata per lo sviluppo |
| Implementazione | **CPython** come runtime autorevole |
| Package/project manager | **uv**, versione fissata e `uv.lock` versionato |
| Metadati e configurazione | `pyproject.toml` secondo gli standard PyPA/PEP 621 |
| Ambiente virtuale | `.venv/` locale al repository, creato e gestito da `uv` |
| Versione Python | `.python-version` per il pin locale; `project.requires-python` per il range supportato |
| Build backend | **Hatchling** come default per package ordinari; alternativa tramite ADR |
| Task runner pubblico | **just** |
| Architettura | Modular monolith, functional core / imperative shell, ports & adapters |
| Formattazione e lint | **Ruff**, unico formatter e linter autorevole |
| Typecheck | **mypy** in modalità strict |
| Architettura import | **Import Linter** |
| Dipendenze inutilizzate | **deptry**; **vulture** MAY come segnale advisory |
| Test | **pytest**, `pytest-cov` e `coverage.py`; Hypothesis quando utile |
| E2E browser | Playwright se esiste una UI web |
| API web | **FastAPI** come default; Starlette per esigenze ASGI più minimali; Django per applicazioni full-stack con esigenze proprie |
| CLI | `argparse` fino a pochi comandi; **Typer** per CLI strutturate e tipizzate |
| Persistenza relazionale | **SQLAlchemy 2.x** + Alembic, quando serve un ORM/unit of work |
| Validazione dati | **Pydantic v2** ai confini; dataclass e tipi di dominio nel core |
| Server MCP | SDK Python ufficiale MCP v2, quando il progetto espone tool ad agenti |
| Logging | `logging` standard come infrastruttura; `structlog` come adapter consigliato per log strutturati |
| CI/CD | GitHub Actions |
| Hosting del codice | GitHub con ruleset, CodeQL, Dependabot/Renovate e security scanning |

Lo stack è un default, non un catalogo da installare integralmente. Si aggiungono soltanto i componenti richiesti dai deployable e dai casi d'uso effettivi.

### Policy Python e CPython

Un nuovo progetto parte dalla più recente release stabile di CPython con bugfix e aggiornamenti di sicurezza, **non** da una pre-release o da una build di sviluppo. Alla verifica del 13 novembre 2026, la versione stabile più recente è **Python 3.15.2**, pubblicata il 25 ottobre 2026; la serie 3.15 è in fase di bugfix e ha supporto previsto fino a ottobre 2031. ([Python Downloads](https://www.python.org/downloads/), [status delle versioni Python](https://devguide.python.org/versions/))

La scelta di 3.15.2 è il target iniziale, non un obbligo cieco: prima di fissarla occorre verificare che tutte le dipendenze critiche, gli eventuali moduli con estensioni native, le immagini container e i servizi di deployment supportino la versione. FastAPI, per esempio, ha aggiunto supporto a Python 3.15 nella serie 0.162; ciò non dimostra automaticamente la compatibilità di ogni altra libreria del progetto. ([FastAPI release notes](https://fastapi.tiangolo.com/release-notes/))

Regole:

- `.python-version` contiene il pin esatto usato in sviluppo e localmente, ad esempio `3.15.2`;
- `pyproject.toml` dichiara il range realmente supportato con `project.requires-python`, ad esempio `>=3.14` se il codice e le dipendenze sono compatibili con 3.14;
- la versione minima dichiarata non deve essere più bassa di quella effettivamente testata;
- CI testa almeno la versione minima dichiarata e la versione stabile più recente adottata;
- per applicazioni con un solo runtime di produzione, si distribuisce una versione patch fissata nell'immagine e aggiornata tramite PR;
- per librerie pubblicate, il range supportato è una promessa pubblica: testare tutte le minor dichiarate e non restringerlo implicitamente;
- le pre-release (alpha, beta, release candidate) non entrano nel runtime di produzione senza ADR e suite di compatibilità dedicata.

Gli upgrade di Python:

1. avvengono tramite PR dedicata;
2. aggiornano `.python-version`, `requires-python` se necessario, immagini e configurazioni CI;
3. eseguono l'intera compatibility suite, inclusi i test d'installazione/build;
4. non vengono mescolati a feature applicative;
5. aggiornano documentazione, runbook e lockfile;
6. verificano anche le dipendenze native e non solo quelle pure Python.

### Policy uv, packaging e dipendenze

`uv` è lo strumento autorevole per versioni Python, ambiente virtuale, risoluzione, sincronizzazione, esecuzione, build e pubblicazione. La configurazione di progetto vive in `pyproject.toml`; il lockfile `uv.lock` viene committato e non si modifica a mano. `uv` produce un lockfile universale che può contenere risoluzioni condizionali per sistema operativo, architettura e versione Python: la compatibilità va verificata sull'intero range dichiarato. ([uv — projects](https://docs.astral.sh/uv/guides/projects/), [uv — lockfile e risoluzione](https://docs.astral.sh/uv/concepts/resolution/))

Regole:

- una sola fonte autorevole per le dipendenze: `pyproject.toml` + `uv.lock`;
- le dipendenze applicative sono dichiarate in `[project].dependencies` o nei gruppi di dipendenze definiti nel progetto;
- strumenti di sviluppo, test e documentazione stanno nei gruppi di sviluppo, non nelle dipendenze runtime;
- `uv sync --locked` è il percorso standard di installazione riproducibile in CI;
- l'agente usa `uv run` o le recipe `just`, non `pip install` globale;
- `.venv/` è locale e gitignored;
- `uv.lock` è versionato; nessun intervento manuale sul suo contenuto;
- la modifica di una dipendenza aggiorna lockfile, test, licenze e report di sicurezza nello stesso lavoro;
- le dipendenze dirette devono essere intenzionali: non affidarsi a una dipendenza transitiva come se fosse un contratto del progetto;
- le dipendenze Git, URL dirette e repository non standard richiedono motivazione, pin immutabile e verifica della provenienza;
- i pacchetti pubblicati devono essere costruiti e provati installandoli in un ambiente pulito, non soltanto importati dalla working tree.

`requirements.txt` MAY essere generato come artefatto di interoperabilità per sistemi esterni che non possono usare `uv`, ma non deve diventare una seconda fonte di verità aggiornata manualmente. `pip`, Poetry, PDM e Pipenv non si affiancano a `uv` per gestire lo stesso progetto senza ADR.

### Policy di typing Python

Python è dinamico: le annotazioni non vengono enforce-ate automaticamente dall'interprete. Il progetto SHOULD essere tipizzato in modo rigoroso e verificato con uno strumento statico, ma deve mantenere la validazione runtime indipendente.

Policy predefinita:

- annotare tutte le funzioni e i metodi di produzione, inclusi i tipi di ritorno;
- annotare attributi, collezioni, callback e confini di protocollo;
- usare `object` quando il valore è sconosciuto e deve essere ristretto; usare `Any` soltanto ai confini inevitabilmente dinamici e con motivazione;
- preferire `Protocol` per contratti strutturali e porte, non classi base create solo per il typing;
- preferire `TypedDict`, `Literal`, union discriminate, `Enum`/`StrEnum`, `NewType` e `dataclass` quando rappresentano chiaramente il dominio;
- usare `dataclass(frozen=True, slots=True)` per value object semplici e immutabili, dove compatibile con il caso d'uso;
- usare `TypeGuard`/`TypeIs` solo quando la funzione dimostra realmente il narrowing dichiarato;
- usare `assert_never` per rendere esplicita l'esaustività di `match` e delle union;
- non confondere `cast()` con una conversione o validazione: `cast` non modifica né controlla il valore a runtime;
- non usare annotazioni come sostituto della validazione di input, output LLM, JSON, environment o dati persistiti.

`mypy --strict` è il type checker predefinito e il gate statico autorevole. `ty` di Astral è molto promettente, ma al 13 novembre 2026 risulta ancora in **beta**: MAY essere provato in parallelo o in una branch dedicata, ma non sostituisce `mypy` nel gate principale finché stabilità, copertura delle feature di typing e compatibilità con le librerie usate non sono sufficienti. Non installare contemporaneamente mypy, Pyright, basedpyright e ty come quattro gate equivalenti: scegliere un'autorità. ([mypy](https://mypy.readthedocs.io/en/stable/), [ty](https://docs.astral.sh/ty/), [stato beta di ty](https://github.com/astral-sh/ty))

Configurazione di base indicativa:

```toml
[project]
name = "example-project"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []

[dependency-groups]
dev = [
  "mypy",
  "pytest",
  "pytest-cov",
  "ruff",
  "import-linter",
  "deptry",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
target-version = "py314"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "RUF", "T20"]

[tool.mypy]
python_version = "3.14"
strict = true
warn_unreachable = true
show_error_codes = true
pretty = true
mypy_path = "src"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-config --strict-markers"

[tool.coverage.run]
branch = true
source = ["example_project"]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 85
```

Il frammento è una baseline, non una configurazione universale: il `target-version` di Ruff, il `python_version` di mypy, `requires-python` e le versioni della matrice CI devono essere coerenti con la versione minima effettivamente supportata. Le regole Ruff vanno calibrate e documentate; aggiungere un set enorme di plugin di lint sovrapposti non migliora automaticamente la qualità. Ruff copre formattazione e numerose famiglie di regole, ma **non** sostituisce il type checker. ([Ruff](https://docs.astral.sh/ruff/))

### Portabilità e runtime alternativi

CPython è il runtime autorevole. PyPy, build free-threaded (`python3.15t`) e runtime sperimentali non sono target standard: possono essere adottati solo se esiste un beneficio misurato e una suite di compatibilità separata.

Regole:

- niente dipendenze dal layout interno di CPython o da API private;
- niente assunzioni sulla presenza del GIL come garanzia di correttezza;
- non usare thread, processi o task asyncio come se avessero lo stesso modello di condivisione e cancellazione;
- I/O, clock, casualità, processi, filesystem, database e rete devono stare dietro porte o adapter;
- evitare dipendenze da estensioni native se una soluzione pure Python è ragionevole e non compromette obiettivi misurati;
- se si adotta free-threaded Python, verificare la compatibilità di tutte le estensioni native, dei driver e delle librerie concorrenti, oltre ai race test;
- lo spike deve coprire packaging, wheel, SDK, subprocess, worker, streaming, tracing, crash recovery, profiling, debugging e deployment.

Non aggiungere più implementazioni Python o runtime solo per il gusto della portabilità: il costo di manutenzione deve essere giustificato da un requisito reale.

---

## 3. Architettura del repository

### Struttura consigliata

Per un progetto singolo, il default è il layout `src/`: il package importabile risiede in `src/` e i test sono separati. Questo evita che la directory corrente mascheri il package installato e rende più realistico il test del pacchetto costruito. Ogni package ordinario SHOULD avere `__init__.py` espliciti; namespace package impliciti solo quando servono davvero e con ADR.

```text
.
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md
├── GEMINI.md -> AGENTS.md                  # opzionale
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── justfile
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── .githooks/
│   ├── pre-commit
│   └── pre-push
│
├── docs/
│   ├── INDEX.md
│   ├── PROJECT.md
│   ├── architecture/
│   │   ├── OVERVIEW.md
│   │   ├── BOUNDARIES.md
│   │   └── adr/                            # ADR_PATH configurabile
│   ├── product/
│   │   ├── OVERVIEW.md
│   │   ├── GLOSSARY.md
│   │   ├── VISION.md                       # opzionale
│   │   └── pdr/                            # PDR_PATH configurabile
│   ├── development/
│   │   ├── GETTING-STARTED.md
│   │   ├── CODING.md
│   │   ├── TESTING.md
│   │   ├── WORKFLOWS.md
│   │   └── SECURITY.md
│   └── operations/
│       └── runbooks/
│
├── src/
│   └── <project_package>/
│       ├── __init__.py
│       ├── domain/
│       ├── application/
│       ├── ports/
│       ├── adapters/
│       └── entrypoints/                    # se più superfici nello stesso deployable
│
├── apps/                                   # solo per deployable realmente separati
│   ├── api/
│   ├── worker/
│   ├── cli/
│   ├── mcp/
│   └── web/                                # se esiste una UI
│
├── packages/                               # workspace uv, se il monorepo lo richiede
│   ├── <bounded-context>/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/<context_package>/
│   ├── contracts/
│   ├── adapter_<technology>/
│   └── testkit/                             # non importabile dal codice di produzione
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── contract/
│   └── fixtures/
│
├── tools/
│   └── scripts/
│
└── .github/
    ├── copilot-instructions.md
    ├── instructions/
    ├── CODEOWNERS
    ├── dependabot.yml                       # o configurazione Renovate
    ├── PULL_REQUEST_TEMPLATE.md
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

La struttura è una guida, non un invito a creare tutte le cartelle. Non creare directory vuote, package fittizi, layer senza responsabilità o deployable ipotetici. Un progetto piccolo può iniziare con un solo package in `src/`; la separazione in workspace e app indipendenti si introduce quando esiste una reale esigenza di versionamento, deploy o responsabilità autonoma.

Per un monorepo `uv` supporta workspace con più package, ognuno con il proprio `pyproject.toml` e un lockfile condiviso alla radice. Il workspace non deve diventare un pretesto per frammentare un modular monolith in package amministrativi. ([uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/))

Non creare `apps/web`, browser test o dipendenze UI se non esiste una UI. Non creare un package separato per ogni singola classe o cartella tecnica.

### Convenzioni di package e moduli Python

- package e moduli in `snake_case`;
- classi in `PascalCase`, funzioni e variabili in `snake_case`;
- costanti di modulo in `UPPER_SNAKE_CASE`;
- nomi di moduli semantici: `payments`, `report_generation`, `user_registration`, non `manager`, `misc`, `utils`;
- import assoluti dal package principale come default;
- niente modifiche di `sys.path`, import basati sulla working directory o manipolazioni del `PYTHONPATH` per far funzionare test e runtime;
- niente `import *` nel codice di produzione;
- `__init__.py` deve restare leggero: niente query, startup, registrazioni globali o import di framework che producano side effect;
- evitare grandi moduli-monolite e grandi `__init__.py` che riesportano l'intero package;
- le API pubbliche di un bounded context sono esplicite e documentate; i moduli interni non sono importabili da altri bounded context;
- i moduli non devono eseguire lavoro applicativo quando vengono importati;
- evitare import circolari e dipendenze risolte con import locali usati per nascondere un confine architetturale errato.

### `docs/PROJECT.md`

È il primo documento di orientamento del progetto e deve contenere:

- obiettivo e non-obiettivi;
- versione Python fissata e range `requires-python` supportato;
- tabella dei deployable esistenti;
- presenza o assenza di UI, API, worker, CLI, MCP e mobile;
- package e bounded context, con responsabilità;
- data store utilizzati e ownership dei dati;
- servizi esterni e provider;
- flussi critici e invarianti;
- classificazione dei dati e requisiti di privacy;
- command map e mappa delle superfici (caso d'uso × canale: CLI, API, MCP, UI, job);
- principali ADR/PDR;
- schema delle dipendenze tra package;
- budget di performance, concorrenza e test;
- stato delle funzionalità;
- procedure di bootstrap e deploy.

### `docs/development/GETTING-STARTED.md`

È il documento di onboarding tecnico, linkato da `docs/INDEX.md` e richiamato da `docs/PROJECT.md`. Deve contenere:

- prerequisiti (CPython, `uv`, `just`, tool esterni, Docker se necessario) e come verificarli con `just doctor`;
- setup iniziale tramite `just setup`;
- come viene fissata la versione Python e come viene sincronizzato `.venv`;
- rimando alla tabella delle recipe (§ 5) invece di duplicarla;
- come eseguire test, typecheck e debug;
- come attivare `LOG_LEVEL=debug` e recuperare i log di un flusso;
- come lanciare API, CLI, worker e MCP realmente presenti;
- mappa commentata dei package e delle cartelle principali.

Vincolo di freschezza: ogni comando citato deve esistere davvero nel `justfile`; un comando inventato o rinominato è un docs bug bloccante in review. Le versioni indicate devono corrispondere ai pin effettivi.

### Documenti di recap come *viste*

`docs/INDEX.md`, gli `OVERVIEW.md` e gli eventuali `ARCHITECTURE.md`/`ABSTRACTIONS.md` sono **viste sullo stato corrente**: riportano solo le decisioni *attive*, in forma sintetica. Evitano all'agente di rileggere decine di ADR/PDR per ricostruire l'esistente; i decision record servono per lo zoom-in storico. Regola: una decisione `superseded` sparisce dalle viste di recap e resta solo nei record.

### README dei package / bounded context

Ogni package o bounded context deve documentare:

```text
Responsabilità
Non-responsabilità
Invarianti
API pubblica e simboli esportati
Dipendenze consentite
Dipendenze vietate
Entry point e superfici che lo utilizzano
Strategia di validazione dei dati
Test da eseguire
ADR/PDR rilevanti
```

### Regole di dipendenza

```text
domain
  ↓
application + ports
  ↓
adapters
  ↓
apps / composition root
```

- `domain` non importa framework, database, filesystem, rete, SDK esterni o runtime infrastrutturali.
- `application` orchestra il dominio attraverso porte e coordina transazioni e policy applicative.
- gli adapter implementano le porte e traducono protocolli esterni nel modello interno.
- gli entrypoint compongono l'applicazione e non contengono logica di dominio.
- gli adapter di ingresso (CLI, HTTP, MCP, UI, worker) non contengono logica: parsing → validazione → caso d'uso → mappatura del risultato (§ 3, *Superfici di ingresso*).
- i bounded context comunicano solo tramite API pubbliche e contratti espliciti; non importano internals reciproci.
- il codice di produzione non può importare `testkit` o package di test.
- niente dipendenze circolari tra package o layer.
- niente cartelle generiche `utils`, `helpers`, `common`, `misc` o `shared` senza una responsabilità esplicita.
- niente service locator, container di dependency injection o reflection/metaprogrammazione senza ADR.
- niente grandi oggetti mutabili con stato nascosto, singleton globali o stato applicativo nel modulo.
- logging e observability sono porte: il dominio non conosce il logger; niente `print()` nel codice di libreria e niente logging configurato all'import (§ 3, *Logging e observability*).
- l'ORM e i suoi modelli non devono diventare il modello di dominio per semplice comodità.
- le dipendenze tra package sono direzionali e verificate con Import Linter (§ 4).

Preferire:

- value object immutabili e dataclass frozen quando appropriato;
- tipi nominali (`NewType`) per distinguere ID con la stessa rappresentazione, senza fingere che `NewType` validi il valore a runtime;
- `Protocol` per porte e contratti strutturali;
- `TypedDict`, `Literal`, `Enum` e union discriminate per dati con forme alternative;
- errori di dominio espliciti: eccezioni specifiche per condizioni eccezionali e risultati/varianti tipizzate per alternative attese;
- funzioni di transizione pure e invarianti esplicite;
- `match` esaustivi, `assert_never` e controllo delle union;
- dipendenze esplicite nel costruttore o nella funzione;
- clock, ID generator, random e I/O iniettati;
- context manager per risorse con lifecycle determinato;
- transazioni e confini di commit espliciti.

Python non ha un tipo `Result` standard né un sistema di union discriminante identico a TypeScript: non introdurre una libreria Result per imitazione. Usare eccezioni tipizzate per errori che interrompono un caso d'uso e oggetti risultato/union quando il chiamante deve scegliere tra esiti di business normali. Non usare eccezioni generiche per il normale branching.

Tutte le regole sui layer devono essere codificate in Import Linter e, dove opportuno, in check dedicati; non affidarle soltanto alla documentazione (principio gate-first, § 1).

### Superfici di ingresso: CLI, API, MCP, UI e worker

**Un caso d'uso, molte superfici.** Ogni capability del sistema esiste **una sola volta**, come caso d'uso nell'application layer di un bounded context. CLI, API HTTP, server MCP, UI e consumer di job sono **adapter di ingresso (driving)** intercambiabili che proiettano lo stesso caso d'uso su canali diversi. La duplicazione tra superfici è il sintomo di un caso d'uso mancante: se due entrypoint contengono la stessa logica, questa va spostata nell'application layer, mai copiata.

Ogni entrypoint ha la stessa anatomia, e **nient'altro**:

```text
parse input → valida a runtime → chiama il caso d'uso → mappa il risultato sul canale
```

- Niente logica di dominio o orchestrazione negli entrypoint. È un **gate** Import Linter: `apps/**` importa solo le API pubbliche dei package, mai gli internals di `domain/` o degli adapter.
- Il wiring (costruzione di config, adapter, transazioni e casi d'uso) vive nel **composition root** dell'app: `main.py`, `cli.py`, `server.py` o factory esplicite. Il composition root fa bootstrap e dispatch; non diventa un contenitore di regole applicative.
- Input e output dei casi d'uso sono DTO/contratti condivisi, insieme agli schemi di validazione e alla **tassonomia degli errori**. La stessa definizione viene riutilizzata da CLI, API, MCP e client, senza ridefinizione manuale.
- I modelli Pydantic sono ammessi al confine e nei contratti condivisi; il dominio non deve dipendere dal framework HTTP o da oggetti Request.
- **Naming parallelo**: lo stesso caso d'uso ha lo stesso nome su ogni canale — `user create` in CLI, `POST /users` in API, tool `user_create` in MCP, mutation equivalente nella UI, `CreateUserJob`/handler dedicato per i job. La corrispondenza è documentata nella mappa delle superfici di `docs/PROJECT.md`.

Anatomia indicativa delle app:

```text
apps/
├── cli/
│   └── src/<cli_package>/
│       ├── main.py                    # composition root sottile
│       ├── commands/                  # un modulo per subcommand
│       │   ├── user/
│       │   │   ├── create.py
│       │   │   └── list.py
│       │   └── report/
│       │       └── generate.py
│       ├── registry.py                # registro dichiarativo dei comandi
│       └── output.py                  # renderer human/JSON, exit code
├── api/
│   └── src/<api_package>/
│       ├── main.py                    # composition root ASGI
│       ├── routes/                    # un handler per caso d'uso
│       └── error_mapper.py            # errori dominio → Problem Details
├── mcp/
│   └── src/<mcp_package>/
│       ├── server.py                  # composition root + transport
│       └── tools/                     # un modulo per tool esposto
├── worker/
│   └── src/<worker_package>/
│       ├── main.py                    # bootstrap del consumer
│       └── handlers/                  # un handler per tipo di messaggio/job
└── web/
    └── src/
        ├── features/<feature>/        # componenti, client e test colocati
        └── design-system/
```

#### CLI

Default: **un solo eseguibile con albero di subcommand** (`<progetto> <gruppo> <verbo>`). Comandi separati solo quando audience, lifecycle di deploy o bounded context sono genuinamente disgiunti; la scelta è un'ADR. In entrambi i casi ogni bin resta un composition root sottile sugli stessi package.

- **Un modulo per subcommand**, con path che rispecchia il comando (`commands/user/create.py` → `cli user create`): l'albero dei file è la tabella di routing, greppabile e navigabile dagli agenti.
- Framework: fino a pochi comandi può bastare `argparse` della standard library; per una CLI strutturata con typing, help e gruppi usare **Typer**; **Click** è una scelta valida quando serve controllo esplicito sul framework. Il framework resta confinato in `apps/cli`: i casi d'uso non lo conoscono.
- **Contratto agent-first** — la CLI sarà operata anche da agenti AI, quindi l'output è un'API a tutti gli effetti:
  - stdout porta **solo dati**; spinner, progress, warning e log vanno su stderr;
  - ogni comando supporta `--json` o un formato machine-readable equivalente; in contesto non-TTY l'output JSON è il default, mentre la tabella leggibile resta per l'uso interattivo;
  - errori strutturati su stderr anche in modalità JSON, con codice stabile, messaggio sintetico e dettagli sicuri;
  - tassonomia di exit code fissata in ADR (es. `0` ok, `1` errore interno, `2` input non valido, `3` auth, `4` non trovato, `5` conflitto), mappata dalla tassonomia condivisa;
  - `--dry-run` e `--yes` per le operazioni distruttive; operazioni idempotenti dove possibile (gli agenti ritentano);
  - `--help` completo con esempi: è il meccanismo con cui un agente esplora la CLI;
  - rispettare `NO_COLOR`; niente codici ANSI su stream non-TTY;
  - i comandi non devono richiedere input interattivo implicito; i prompt vanno disattivati in modalità non-TTY o sostituiti da parametri espliciti.
- Il contratto è un **gate**: una integration suite verifica per ogni comando `--help`, `--json`, exit code, separazione degli stream, input mancante e comportamento non-TTY.

#### API HTTP

- **FastAPI** è il default per nuove API Python che beneficiano di validazione Pydantic, OpenAPI e ASGI; **Starlette** è preferibile se si vuole il livello ASGI più essenziale senza le funzionalità aggiuntive di FastAPI. Django è una scelta architetturale per un'applicazione full-stack con admin, ORM, auth e convenzioni integrate, non un'alternativa da installare insieme a FastAPI.
- Un handler per caso d'uso: valida l'input con schema condiviso, chiama il caso d'uso, mappa il risultato. Niente logica nei controller/route handler.
- Pydantic v2 produce JSON Schema; i contratti condivisi devono essere la fonte per request, response e tool schema. Evitare classi Pydantic duplicate che rappresentano la stessa informazione con differenze casuali. ([Pydantic JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema/))
- Errori: la tassonomia condivisa è mappata su **Problem Details RFC 9457** (`application/problem+json`), con status coerenti con gli exit code della CLI.
- Non esporre stack trace, query SQL, percorsi locali, segreti o dettagli interni nelle risposte di produzione.
- Le chiamate di rete sincrone non devono bloccare un event loop ASGI. Scegliere in modo coerente driver, sessioni e handler sync/async; non convertire indiscriminatamente ogni funzione in `async def`.
- Frontend e client consumano OpenAPI/schema/DTO generati o condivisi: nessuna ridefinizione manuale non verificata dei contratti API.
- Il framework rimane nell'adapter `apps/api`; il dominio non importa FastAPI, Starlette, Pydantic HTTP types o `Request`/`Response`.

#### Server MCP

- Il server MCP è un adapter di ingresso come gli altri: ogni tool è un modulo in `tools/`, dichiara description e input schema e delega a un caso d'uso. Niente logica nei tool handler.
- Usare l'**SDK Python ufficiale MCP v2**, la linea stabile documentata alla data di verifica; il pacchetto richiede Python 3.11+ e supporta stdio, Streamable HTTP e SSE. Non copiare API o esempi della linea v1 senza verificare la versione installata. ([documentazione SDK Python MCP](https://py.sdk.modelcontextprotocol.io/), [repository ufficiale](https://github.com/modelcontextprotocol/python-sdk))
- Trasporto **stdio** come default per l'integrazione locale con gli agenti; **Streamable HTTP** con autenticazione quando serve accesso remoto. SSE soltanto per esigenze di interoperabilità specifiche.
- **Tool curati, non generati in massa**: esporre un sottoinsieme deliberato di casi d'uso, con `description` scritte per il modello (cosa fa, quando usarlo, prerequisiti, side effect, cosa restituisce e come fallisce). Non esporre automaticamente l'intera API come tool: la superficie grezza degrada la selezione del tool da parte dell'LLM.
- Output dei tool: contenuto strutturato derivato dagli stessi DTO dei contratti; errori di dominio mappati su errori MCP con la stessa tassonomia.
- Sicurezza: default read-only; i tool di scrittura richiedono scope espliciti, conferme/guardrail coerenti con il rischio e idempotency key quando serve; niente segreti in descrizioni e output.
- Se il server MCP avvolge lo stesso core della CLI e ne condivide il lifecycle, MAY essere un subcommand (`<progetto> mcp serve`) invece di un deployable separato.

#### Worker e job

- Il consumer di una queue è un adapter di ingresso: deserializza, valida il messaggio e invoca un caso d'uso.
- Il payload deve avere schema/versione espliciti; messaggi vecchi, duplicati o sconosciuti hanno un comportamento deciso e testato.
- Retry, backoff, dead-letter queue, deduplicazione e idempotenza sono policy applicative/infrastrutturali esplicite, non decorazioni casuali sul singolo handler.
- I job devono essere osservabili tramite correlation ID, identificatore del job, tentativo, durata, esito e causa terminale.
- Non assumere che il broker garantisca exactly-once: progettare per consegna almeno una volta, salvo prova documentata del contrario.
- Le funzioni worker non importano SDK specifici del broker nel dominio.

#### UI web

- Struttura per **feature colocate** (`features/<feature>/`: componenti, client API, logica UI e test), non per tipo tecnico (`components/`, `hooks/` globali): ogni feature è comprensibile ed eliminabile in un solo posto.
- Se la UI è React/Vite, il frontend resta un'app distinta dal backend Python; non duplicare le regole di dominio nel client.
- Un'interfaccia server-rendered Python (per esempio Django templates o un frontend HTML minimale) è MAY quando riduce davvero la complessità; non introdurre due stack UI senza una necessità esplicita.
- Il design system vive nell'app UI (o in un package condiviso se esistono più frontend); elementi HTML grezzi restano vietati fuori dal design system quando il progetto lo richiede.
- Le chiamate API passano da un client tipato sui contratti; lo stato server (cache, refetch) è tenuto separato dallo stato UI.

#### Navigabilità per gli agenti

Regole strutturali che rendono il repository percorribile senza esplorazione esaustiva:

- **Screaming architecture**: i nomi di package, cartelle e file dicono cosa fa il sistema (`billing/`, `commands/report/generate.py`), non quali framework usa.
- **Un caso d'uso = un modulo** `verbo_nome.py` con test colocato o chiaramente collegato: trovare il comportamento significa trovare il modulo.
- **Registry espliciti**: ogni app ha un punto unico e dichiarativo che elenca la propria superficie (comandi, route, tool, job). Non è un mega `__init__.py`: importa e registra, non riesporta tutto.
- **Mappa delle superfici** in `docs/PROJECT.md`: tabella caso d'uso × canale (CLI/API/MCP/UI/worker), aggiornata a ogni aggiunta. È l'indice che evita all'agente la scansione di tutte le app.
- Convenzioni costanti: stessa struttura interna per ogni bounded context, stesso naming su ogni canale, stessa anatomia per ogni entrypoint. La predicibilità è la feature.

| Cosa | Dove |
|---|---|
| Regola di business | `src/<package>/domain/` |
| Caso d'uso | `src/<package>/application/<verbo>_<nome>.py` |
| Porta verso l'esterno | `src/<package>/ports/` |
| Adapter (db, fs, SaaS, queue) | `src/<package>/adapters/` o package adapter dedicato |
| DTO, schemi, tassonomia errori | package `contracts` o modulo contratti del bounded context |
| Subcommand CLI | `apps/cli/.../commands/<gruppo>/<verbo>.py` |
| Endpoint HTTP | `apps/api/.../routes/` |
| Tool MCP | `apps/mcp/.../tools/` |
| Job/consumer | `apps/worker/.../handlers/` |
| Schermata o flusso UI | `apps/web/src/features/<feature>/` |
| Wiring e composition root | `apps/<app>/.../{main,cli,server}.py` |

### Logging e observability

Il logging è I/O: vive dietro una **porta** (`Logger` definita come `Protocol` o interfaccia equivalente), con un adapter basato sulla standard library `logging`. Per log strutturati il default consigliato è `structlog` integrato con il sistema standard, configurato nel composition root. Il dominio non logga: restituisce valori, eventi o errori tipizzati; è l'application layer a decidere cosa registrare. `print()` è vietato nel codice di libreria (`src/**`) e il divieto è un **gate di lint**, non una convenzione: stdout non è un canale governabile — niente livelli, redazione dei segreti, formato strutturato o separazione dai dati prodotti dalla CLI.

**Il debug logging resta centrale anche con gli agenti AI.** Un agente *può* pilotare un debugger, ma è uno strumento interattivo, lento e assente in CI e in produzione; i log invece sono **sensori**: artefatti testuali che l'agente può produrre, rileggere, filtrare e citare come evidenza nel report finale. Un buon logging di debug serve quindi due volte: all'umano che scorre il terminale e all'agente che diagnostica un bug senza doverlo indovinare.

Regole:

- **Livelli standard** `debug`/`info`/`warning`/`error`/`critical` della standard library; un livello `trace` personalizzato MAY essere introdotto solo se serve e se rimane interoperabile con gli aggregatori. La variabile `LOG_LEVEL` è validata all'avvio come il resto dell'environment: default `DEBUG` in sviluppo, `INFO` in produzione e nei test.
- **Doppio formato**: JSON strutturato in produzione e CI (leggibile da macchine, agenti e aggregatori); console pretty in sviluppo (leggibile da umani). Stessa porta, formatter differenti. Emoji MAY come marcatori visivi, ma stabili nel tempo e greppabili, mai come unico segnale.
- **Dove loggare**: ai confini — entrypoint, adapter, chiamate esterne, transizioni di stato rilevanti — non dentro le funzioni pure di dominio. Child logger con contesto e correlation/request ID propagato a ogni entry.
- **Contesto asincrono**: usare `contextvars` o il meccanismo dell'adapter per propagare correlation ID in async task; evitare stato globale condiviso e pulire il contesto ai confini della richiesta.
- **Cosa non loggare**: segreti, token, PII, payload interi (troncare o filtrare), credenziali, prompt con dati personali e contenuti sensibili; mai loggare in hot loop senza una motivazione misurata. La redazione è responsabilità dell'adapter.
- **Configurazione**: avviene una sola volta nel composition root; i moduli di libreria non chiamano `basicConfig`, non aggiungono handler e non decidono il livello globale.
- **Eccezioni**: registrare lo stack trace una sola volta al confine che gestisce o termina il flusso; non loggare e rilanciare la stessa eccezione a ogni layer.
- **CLI**: i log e i messaggi diagnostici vanno su stderr; stdout è riservato all'output del comando.
- **Per gli agenti**: in diagnosi SHOULD rieseguire il flusso con `LOG_LEVEL=DEBUG` e citare l'output rilevante nel report invece di ipotizzare il comportamento; i log temporanei aggiunti per diagnosticare vanno rimossi o convertiti in chiamate di livello appropriato prima della consegna — un `print()` dimenticato è un gate rosso.
- **Telemetria di prodotto (se esiste)**: gli eventi analytics sono definiti nei contratti condivisi, non contengono PII o segreti e sono emessi tramite una porta dedicata, mai con chiamate dirette al provider dal dominio o dagli entrypoint. La conformità è verificata dal telemetry guard (§ 10).

La telemetria copre due esigenze distinte, con tool e finalità separate:

- **crash reporting**: cattura di eccezioni e crash con stack trace e contesto tecnico, nient'altro. Sentry è un'opzione diffusa; l'adapter vive nel backend Python e, se esiste, nel frontend separato;
- **product analytics**: eventi di utilizzo anonimi per capire come il prodotto viene usato. PostHog è un'opzione self-hostable/cloud. Gli eventi sono definiti nei contratti e non contengono mai PII.

Le due porte restano separate: il crash reporting non diventa un canale analytics e viceversa. OpenTelemetry MAY essere aggiunto per tracing, metriche e propagazione del contesto; non confondere automaticamente tracing tecnico e analytics di prodotto. La scelta dei tool avviene tramite ADR; quelli citati sono opzioni di riferimento, non un obbligo. ([structlog](https://www.structlog.org/), [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/))

### Contratti e dati esterni

Ogni dato proveniente dall'esterno deve essere validato a runtime, prima di entrare nel dominio:

- HTTP request e response di provider esterni;
- database, soprattutto dati legacy o letti da schema non controllato dal processo;
- environment e file di configurazione;
- queue, eventi, webhook e payload persistiti;
- API esterne e SDK;
- output LLM, tool call e structured output;
- input CLI e file caricati dall'utente.

È vietato confondere una dichiarazione di tipo con la validazione:

```python
import json
from typing import cast

payload = json.loads(raw)
result = cast(CreateUserRequest, payload)  # VIETATO: cast non valida il dato
```

Il progetto seleziona una sola libreria di schema per ciascun confine condiviso tramite ADR. Default consigliato: **Pydantic v2** per DTO e dati esterni che necessitano di validazione, serializzazione e JSON Schema. `TypeAdapter` può validare tipi che non richiedono un `BaseModel`. Non creare una seconda definizione manuale dello stesso contratto in JSON Schema, TypedDict, modello ORM e schema HTTP: i derivati devono essere generati o verificati dalla fonte canonica.

Regole Pydantic:

- `model_validate`/`TypeAdapter.validate_python` per dati Python non attendibili;
- `model_validate_json`/`TypeAdapter.validate_json` per input JSON;
- configurare esplicitamente `extra` e il livello di coercizione; per input sensibili preferire rifiuto dei campi extra e validazione strict dove compatibile con il contratto;
- `model_dump` e serializzazione solo dopo la validazione;
- schemi JSON derivati dalle definizioni canoniche;
- separare DTO di input/output dai modelli di dominio e dai modelli SQLAlchemy;
- non usare `model_construct` su dati non attendibili: bypassa la validazione;
- evitare validator con side effect o accessi I/O;
- versionare i contratti pubblici e gestire esplicitamente compatibilità/migrazione.

Per il dominio: dataclass e tipi Python ordinari sono preferiti quando non è necessaria la validazione/serializzazione Pydantic. Pydantic è una scelta per i confini e i contratti, non una dipendenza obbligatoria di ogni modulo.

Per la configurazione:

- i file `.env` reali sono sempre gitignored;
- nel repository vive un `.env.example` con valori finti ma strutturalmente validi;
- l'environment viene validato all'avvio, preferibilmente tramite `pydantic-settings` o una soluzione esplicita;
- i default non sensibili sono documentati e versionabili; segreti e credenziali non vivono in `.env.example`, log, test fixture o immagini;
- `.envrc`/direnv sono MAY come comodità locale, non un prerequisito nascosto per CI o deploy;
- i valori obbligatori mancanti o malformati devono produrre un errore iniziale leggibile, non un errore casuale ore dopo;
- non leggere l'environment in decine di moduli: caricare una configurazione tipizzata nel composition root e passarla esplicitamente.

### Persistenza e transazioni (se applicabili)

- **SQLAlchemy 2.x** è il default per database relazionali quando serve un ORM o un'unit of work; non è obbligatorio per query semplici o storage non relazionale.
- Alembic gestisce le migration; ogni migration è versionata, revisionata e testata su un database reale o temporaneo equivalente.
- La sessione/unit of work è posseduta da un singolo flusso applicativo e non viene condivisa accidentalmente tra thread, task asyncio o richieste concorrenti.
- Non conservare sessioni ORM globali né importare modelli ORM nel dominio.
- Le transazioni hanno un proprietario e un confine di commit espliciti; evitare commit nascosti dentro metodi di repository elementari.
- Le migration devono essere compatibili con la strategia di deploy (expand/contract quando occorre); il rollback deve essere ragionato, non presunto.
- I test integration usano un database temporaneo e realistico; SQLite non sostituisce automaticamente PostgreSQL se il progetto usa caratteristiche specifiche di PostgreSQL.
- Query N+1, lock, isolation level, pool e timeout sono verificati con dati e carichi rappresentativi, non risolti tramite ipotesi.

### Async, concorrenza e risorse

- `async`/`await` è usato per I/O concorrente, non come decorazione o come sinonimo di prestazioni.
- Non chiamare operazioni bloccanti (filesystem lento, SDK sincroni, CPU-bound) dentro l'event loop; usare adapter appropriati, executor o processi secondo il caso misurato.
- Non creare task fire-and-forget senza ownership, supervisione, gestione errori e shutdown.
- Ogni task, processo e worker ha lifecycle, timeout, cancellazione e cleanup espliciti.
- Le code in memoria sono bounded; la backpressure è definita invece di accumulare lavoro illimitato.
- Le operazioni ripetibili sono idempotenti quando possibile; retry con backoff e jitter solo per errori transitori e con budget massimo.
- Testare timeout, cancellazione, retry, race condition e shutdown graceful per i flussi che li richiedono.
- Non assumere che il GIL elimini i race condition; lo stato condiviso resta un problema architetturale.
- Preferire API standard (`asyncio`, `contextvars`, `concurrent.futures`) e isolare AnyIO/Trio o framework specifici dietro adapter quando la portabilità è un requisito.

---

## 4. Tooling statico

| Scopo | Tool predefinito | Note |
|---|---|---|
| Formattazione | Ruff Formatter | Autorevole; non affiancare Black |
| Lint | Ruff | Autorevole; include regole di più famiglie Flake8 e import sorting |
| Typecheck | mypy `--strict` | Gate separato dal lint |
| Architettura e cicli | Import Linter | Contratti forbidden, layers, independence e acyclic siblings |
| Dipendenze dichiarate | deptry | Rileva dipendenze mancanti, inutilizzate o classificate male |
| Codice morto | MAY: vulture | Advisory; attenzione a plugin, reflection, registrazioni dinamiche |
| Test | pytest | Suite principale |
| Coverage | coverage.py + pytest-cov | Line, statement e soprattutto branch coverage |
| Property testing | Hypothesis | Quando utile per invarianti e input combinatori |
| E2E | Playwright | Solo se esiste una UI browser |
| Mutazione test | MAY: mutmut o equivalente | Solo su componenti critici e in slow lane |
| Vulnerabilità dipendenze | pip-audit e/o OSV-Scanner | Verificare il lockfile/ambiente effettivamente usato |
| SAST | Bandit / Semgrep CE | Bandit per controlli Python mirati; Semgrep quando serve copertura più profonda |
| Segreti | Gitleaks | Staged diff e storia in CI |
| Workflow GitHub | actionlint | Sintassi e semantica dei workflow |
| Sicurezza GitHub Actions | zizmor | Permessi, injection e pattern rischiosi |
| Markdown | markdownlint-cli2 | Regole versionate |
| Ortografia | typos o cspell | Glossario di progetto |
| Link | lychee | Preferibilmente slow lane |
| Environment per-directory | direnv | MAY; mai requisito implicito per CI/deploy |
| Shell | ShellCheck | Se esistono script shell |
| Container/IaC | Hadolint e Trivy | Se applicabili |
| Qualità continua e quality gate | MAY: SonarQube | Vedi *Code health e hotspot* |
| Hotspot e analisi git-history | MAY: CodeCharta o CodeMaat | Nel health guard (§ 10) |
| Code health pro | MAY, solo a regime: CodeScene o Codacy | Solo se il progetto e il ritorno atteso lo giustificano |

Ruff rimane **sia il formatter sia il linter autorevole**. mypy rimane il type checker autorevole. Import Linter rimane l'autorità sui confini architetturali. Non duplicare sistematicamente le stesse regole nei tool diversi e non confondere lint con typecheck: Ruff individua molte classi di errore statico, ma non sostituisce un controllo dei tipi completo. ([Ruff](https://docs.astral.sh/ruff/), [mypy](https://mypy.readthedocs.io/en/stable/))

### Policy di lint e formatting

- `ruff format --check` verifica la formattazione; `ruff format` la applica.
- `ruff check` esegue il lint; `ruff check --fix` applica soltanto fix automatici sicuri e previsti.
- La configurazione vive in `pyproject.toml`, salvo necessità documentata.
- Il progetto seleziona famiglie di regole comprensibili e motivate; non attiva centinaia di regole senza sapere quali comportamenti impongano.
- L'agente non disattiva regole in blocco per ottenere un risultato verde.
- Le regole specifiche per file sono ammesse solo quando il contesto è realmente diverso e la deroga è circoscritta.
- Formatter e linter sono eseguiti localmente prima della CI.
- Versione Python target di Ruff allineata a `requires-python` e alla versione minima realmente supportata.

ESLint, Flake8, isort, Black e autopep8 non vengono installati per default in un progetto Python che usa Ruff. Possono essere aggiunti tramite ADR soltanto se un controllo indispensabile non è coperto o se esiste un vincolo di interoperabilità.

### Typecheck rigoroso

Configurazione normativa: mypy in modalità strict su codice di produzione e test. I progetti con codice legacy possono introdurre il controllo gradualmente per package, ma il nuovo codice e i file modificati non devono peggiorare il livello raggiunto.

La configurazione SHOULD includere almeno:

- `strict = true`;
- `warn_unreachable = true`;
- error code visibili nei report;
- package e directory esplicitamente inclusi;
- stub mancanti e dipendenze non tipizzate valutati, senza trasformare l'intero progetto in `Any`;
- eccezioni locali e temporanee, mai un'esenzione globale non motivata.

La strictness non è un fine in sé. Un tipo più preciso deve rappresentare una garanzia vera: è vietato inventare un tipo per zittire il checker quando il dato non è stato verificato. `cast()`, `Any`, `# type: ignore` e stub scritti a mano possono nascondere errori reali.

`ty` può essere eseguito in una prova controllata e confrontato con mypy, ma al momento della verifica è Beta: la sua velocità non basta a renderlo automaticamente l'autorità di progetto. Una eventuale sostituzione richiede ADR, baseline dei diagnostic, verifica delle feature di typing impiegate, controllo delle librerie terze e migrazione dei gate. Non usare due type checker come gate duplicati per abitudine: una seconda analisi MAY vivere in una pipeline sperimentale o di confronto. ([ty — stato del progetto](https://github.com/astral-sh/ty), [mypy release notes](https://mypy.readthedocs.io/en/latest/changelog.html))

### Architettura e dipendenze

**Import Linter** rende eseguibili i confini tra moduli e package. Può imporre layer, moduli vietati, indipendenza tra bounded context e assenza di cicli. Ogni regola critica di dipendenza SHOULD avere un contratto nominato e leggibile nel repository. ([Import Linter](https://import-linter.readthedocs.io/en/stable/))

Esempi di contratti da imporre, adattandoli al package reale:

- `domain` non importa `application`, `adapters`, `apps`, framework, SDK o librerie infrastrutturali;
- `application` importa `domain` e `ports`, non adapter concreti;
- `adapters` implementano porte e non sono importati dal dominio;
- bounded context distinti non si importano reciprocamente se devono restare indipendenti;
- `apps/**` non importa moduli privati di un altro package;
- `src/**` non importa `tests/**` o `testkit`;
- le dipendenze tra sibling package sono acicliche.

**deptry** verifica la coerenza tra import e dipendenze dichiarate: dipendenze non dichiarate, inutilizzate o collocate nel gruppo sbagliato. Va eseguito nell'ambiente di progetto, così può confrontare i package effettivamente installati con le dichiarazioni di `pyproject.toml`. ([deptry](https://deptry.com/))

**vulture** MAY essere usato come indicatore di codice potenzialmente morto, ma non come verità assoluta: plugin, entry point, import dinamici, dependency injection e callback registrati indirettamente possono apparire inutilizzati. I risultati devono essere verificati prima di eliminare codice. Il gate deve essere calibrato sui falsi positivi osservati e non deve crescere un'ignore-list generalizzata.

La Python runtime introspection e il sistema di plugin rendono la dead-code analysis meno deterministica di un semplice grafo di import. Per questo il gate più forte è la combinazione di `deptry`, Ruff, Import Linter, test, report coverage e review delle API pubbliche; vulture resta un guard/report o un gate solo dove il progetto è sufficientemente statico.

### Code health e hotspot: free di default, pro solo a regime

Questi strumenti rispondono a un'esigenza precisa del modello 3G: forniscono un **punteggio misurabile** su dimensioni che lint e coverage non coprono (hotspot, complessità, accoppiamento temporale, duplicazione), rendendo applicabili la Boy Scout Rule misurata (§ 12) e le soglie a cricchetto (§ 1). Restano MAY, ma quando si adottano si parte dallo **stack gratuito**; i commerciali si aggiungono solo quando il progetto diventa importante.

**Qualità continua, duplicazione e quality gate:**

- **SonarQube Community Build**, self-hosted, è una possibile base per analisi Python, bug, code smell, vulnerabilità, duplicazione, complessità, debito tecnico, import di coverage e quality gate. Verificare la matrice effettiva delle feature incluse nella versione adottata.
- **SonarQube Cloud** è l'alternativa gestita senza infrastruttura; limiti di LOC, membri e PR dipendono dal piano corrente e vanno verificati prima dell'adozione.
- Policy invariata: gate di **0 issue sul codice nuovo**; toccando codice preesistente si correggono anche le issue dei file toccati.
- Se serve SAST più profondo del livello base incluso: Semgrep CE, con ADR e regole mirate.
- Bandit MAY essere sufficiente per controlli Python di sicurezza più circoscritti, ma non sostituisce dependency scanning, segreti e review di autorizzazione.

**Hotspot dalla storia git (churn × complessità), knowledge map e change coupling:**

- **CodeCharta** (open source, locale) può combinare metriche statiche con cronologia e accoppiamento git; verificare parser Python e metriche della versione adottata.
- **CodeMaat** è l'alternativa minimale e language-agnostic basata sulla storia git, con output analizzabile da script.
- Esecuzione: **mai nella fast lane** — girano nel health/refactoring guard (§ 10) su `scheduled.yml` e producono report e task, non auto-fix.
- Se basta un gate di complessità senza server né dashboard: **lizard** o una regola SonarQube con soglia di complessità ciclomatica, calibrata sul repository.

**Pro, solo a regime** (progetto con utenti reali, business o team multiplo): CodeScene e/o Codacy, eventualmente esposti all'agente via MCP; prima verificare linguaggi, piani, condizioni, qualità dei report e rapporto costo/beneficio. Non introdurre uno strumento pro solo per sostituire una dashboard che nessuno consulta.

### Sicurezza del codice e della supply chain

- **Gitleaks** blocca segreti nello staged diff e scandisce la storia in CI.
- **pip-audit** analizza le vulnerabilità note dei package Python; eseguire contro l'ambiente risolto e/o un export deterministico del lockfile, secondo il supporto della versione adottata.
- **OSV-Scanner** MAY affiancare l'audit se il formato di lock/SBOM e il linguaggio sono supportati.
- **Bandit** controlla pattern Python sospetti; Ruff con regole `S` può fornire un primo livello, evitando duplicazioni non governate.
- **Semgrep CE** MAY essere introdotto per regole SAST più profonde o regole aziendali.
- **Trivy** controlla immagini container, filesystem, SBOM e vulnerabilità applicabili.
- **Dependabot o Renovate** aggiornano le dipendenze Python e GitHub Actions; verificare che lo strumento scelto aggiorni davvero `uv.lock` nel formato e nella versione adottati.
- Le nuove vulnerabilità introdotte dal diff devono bloccare la pipeline; le vulnerabilità preesistenti devono essere tracciate, valutate e avere una policy esplicita.

### Escape hatch

Queste costruzioni devono fallire il lint/typecheck o richiedere una motivazione locale e circoscritta:

- `Any` non confinato a un boundary dinamico;
- `cast()` usato come falsa validazione;
- `# type: ignore` senza error code e motivazione;
- `# noqa`, `# pragma: no cover`, `# nosec`, `# pyright: ignore` e suppression equivalenti generiche;
- `assert` usato per validare dati esterni o garantire invarianti runtime in produzione;
- `except Exception: pass`, `except: pass` o catch silenziosi;
- return `None` o valori sentinella per nascondere un errore non rappresentato nel contratto;
- `eval`, `exec`, `pickle` su dati non attendibili;
- import dinamici usati per nascondere dipendenze o cicli;
- `sys.path` manipolato per correggere una struttura di package errata;
- `asyncio.create_task()` senza ownership o gestione dell'eccezione;
- chiamate bloccanti in un event loop;
- `subprocess` con shell o input non sanitizzato senza motivazione e controlli;
- `print()` o scrittura diretta su stdout nel codice di libreria;
- patch globale o monkeypatch permanenti fuori dai test;
- test saltati o esclusi per rendere verde la pipeline.

Ogni suppression deve avere una motivazione sulla stessa riga o immediatamente sopra, un ambito minimo e, quando possibile, un riferimento a issue/ADR. Le suppression inutilizzate devono essere segnalate. Le eccezioni temporanee devono avere un proprietario o una condizione di rimozione, non restare per sempre.

---

## 5. Interfaccia standard tramite `just`

Gli agenti devono usare esclusivamente le recipe pubbliche di `just`. I comandi dei singoli strumenti e le configurazioni di `uv` restano dettagli implementativi: l'interfaccia operativa del repository è stabile e documentata.

| Comando | Funzione |
|---|---|
| `just setup` | Installa/sincronizza dipendenze e configura gli hook |
| `just doctor` | Verifica Python, uv, tool, ambiente e configurazione |
| `just dev` | Avvia lo sviluppo |
| `just fix` | Applica Ruff format e fix sicuri |
| `just format-check` | Verifica la formattazione |
| `just typecheck` | mypy strict |
| `just lint` | Ruff lint |
| `just dead-code` | deptry e, se configurato, report vulture |
| `just arch` | Import Linter e regole architetturali |
| `just docs-check` | Markdown, spelling e link locali |
| `just docs-bundle` | MAY: genera il bundle `agent-docs/` (§ 7) |
| `just workflows-check` | actionlint e zizmor |
| `just secrets` | Gitleaks |
| `just security` | Audit dipendenze e controlli SAST previsti |
| `just test-unit` | Piccola suite specialistica |
| `just test-integration` | Suite principale |
| `just test-related` | Test collegati ai file modificati |
| `just test-e2e` | Flussi end-to-end, se esiste UI |
| `just test-live` | Servizi reali/LLM; mai implicito |
| `just test-compat` | Matrice di versioni Python supportate, se applicabile |
| `just coverage` | Suite con branch coverage |
| `just coverage-raise` | Alza i threshold al valore corrente (solo salita) |
| `just smoke` | Sottoinsieme critico di integration |
| `just package-check` | Build e installazione del package in ambiente pulito, se pubblicabile |
| `just guards` | Esegue i guard in modalità report-only (§ 10) |
| `just precommit` | Controlli rapidi su staged/related |
| `just prepush` | Static analysis e integration principali |
| `just ci` | Esatta pipeline CI locale |

Le recipe non pertinenti a un progetto (ad esempio `test-e2e` senza UI, `package-check` per un'app non distribuibile o `test-compat` per un deployable con un solo runtime) non devono essere create come stub: si documenta la loro assenza e si aggiorna la command map.

Budget consigliati:

```text
precommit:      ≤ 10 secondi
smoke:          ≤ 20 secondi
prepush:        ≤ 60 secondi
suite CI piena: ≤ 10 minuti
```

Se questi budget vengono superati, ottimizzare suite, fixture, avvio di servizi e confini architetturali prima di introdurre un nuovo task orchestrator. Il budget dei 10 minuti della suite completa è mantenuto dal testing guard (§ 10): un feedback loop lento degrada l'intero loop di sviluppo.

### Matrice gate × stage

Mappa consolidata dei controlli sui tre stage di esecuzione. Ogni riga corrisponde a una recipe `just` eseguibile in locale: **l'intera pipeline è sempre riproducibile in locale** (singole recipe per un controllo puntuale, `just ci` per il check completo); la CI esegue le stesse recipe e resta l'autorità finale, mai il primo punto di rilevamento.

| Controllo | Recipe | precommit | prepush | CI |
|---|---|:---:|:---:|:---:|
| Formattazione | `format-check` | ✅ | ✅ | ✅ |
| Lint | `lint` | ✅ | ✅ | ✅ |
| Typecheck strict | `typecheck` | opzionale/related | ✅ | ✅ |
| Dipendenze | `dead-code` | ❌ | ✅ | ✅ |
| Regole architetturali | `arch` | ❌ | ✅ | ✅ |
| Docs | `docs-check` | ✅ | ✅ | ✅ |
| Workflow GitHub | `workflows-check` | se toccati | ✅ | ✅ |
| Segreti | `secrets` | ✅ (staged) | ✅ | ✅ (+ storia) |
| Audit sicurezza | `security` | ❌ | ✅ | ✅ |
| Test unit | `test-unit` | related | ✅ | ✅ |
| Test integration | `test-integration` | ❌ | ✅ (principali) | ✅ |
| Smoke | `smoke` | ❌ | ✅ | ✅ |
| Coverage e cricchetto | `coverage` | ❌ | ✅ | ✅ |
| E2E | `test-e2e` | ❌ | ❌ | ✅ |
| Compatibilità Python | `test-compat` | ❌ | ❌ | ✅ (job separato) |
| Build/install package | `package-check` | ❌ | se applicabile | ✅ |
| Link esterni | lychee | ❌ | ❌ | slow lane |
| Guard | `guards` | ❌ | ❌ | `scheduled.yml` |

Per applicazioni con un solo interpreter di produzione non serve una suite multi-runtime artificiale: il job compat verifica il range dichiarato o le versioni che il prodotto supporta realmente. Per librerie pubblicate il job è obbligatorio e copre la versione minima e quella massima.

### Fast path per diff docs-only

Quando il diff tocca **esclusivamente** `docs/**`, `*.md`, `.github/workflows/**` e `.githooks/**` — lista esatta e completa mantenuta nel justfile — i gate si riducono ai controlli pertinenti:

- `just precommit` esegue solo `docs-check` e, se i workflow sono toccati, `workflows-check`;
- `just prepush` aggiunge la verifica di freschezza del bundle `agent-docs/`, se esiste (§ 7);
- la CI esegue soltanto i job minimi di docs e lint/workflow.

Invarianti:

- la lista dei path è protetta da CODEOWNERS come ogni altro file di gate (§ 11);
- un diff misto (docs + codice) percorre sempre il percorso completo;
- nessuna soglia viene abbassata: i controlli saltati non sono ridotti, sono non pertinenti al diff;
- `just ci` resta sempre disponibile in locale per la pipeline completa.

Gli hook versionati chiamano soltanto:

```sh
just precommit
just prepush
```

I gate devono vivere **in locale prima che in CI**: l'hook dà feedback immediato all'agente, che può correggere subito nello stesso ciclo. La CI esegue le stesse recipe e resta l'autorità finale, non il primo punto di rilevamento.

Il bootstrap degli hook deve essere idempotente e documentato. Il repository può usare `core.hooksPath=.githooks`; non è obbligatorio adottare un framework di hook esterno se `just` e gli script versionati soddisfano già il requisito.

---

## 6. Strategia di testing: la “coppa”

```text
         pochi E2E
    moltissimi integration
        pochi unit
   ampia base di static checks
```

### TDD come ciclo di default

Il modo di lavoro predefinito dell'agente è **red → green → refactor**:

1. scrivere prima il test che descrive il comportamento atteso e **vederlo fallire**;
2. implementare il minimo per farlo passare;
3. rifattorizzare a test verdi.

Motivo determinante in un progetto AI-only: **un test che non è mai stato visto fallire è sospetto** — può essere tautologico, non assertivo, disabilitato, scollegato dal package importato o scritto su un path che non esercita il codice sotto test. Il ciclo TDD è la contromisura strutturale ai test fantasma (§ 9), oltre che il rimedio da insegnare quando un gate di coverage fallisce.

In Python prestare particolare attenzione al fatto che:

- un test può importare il package dalla working tree invece del package installato;
- un fixture autouse o session-scoped può nascondere dipendenze tra test;
- un `monkeypatch` può cambiare globali e lasciare stato contaminato se la patch non è confinata;
- un test async può non attendere davvero il task o non osservare un'eccezione;
- un'asserzione su un mock può verificare che il mock è stato chiamato senza verificare il comportamento dell'utente;
- `assert` nel codice di produzione non equivale a una validazione runtime, e può essere eliminato con l'ottimizzazione dell'interprete.

### Qualità dei test

Il riferimento sono i [Test Desiderata di Kent Beck](https://medium.com/@kentbeck_7670/test-desiderata-94150638a4b3). In sintesi operativa, ogni test deve essere:

- **isolato**: nessuna dipendenza da altri test o dal loro ordine;
- **deterministico**: stesso input, stesso esito, sempre;
- **veloce**: niente attese, timer reali o I/O non necessaria;
- **comportamentale**: verifica comportamento osservabile, non struttura interna;
- **specifico**: un motivo di fallimento, un segnale chiaro;
- **leggibile**: si capisce l'intento senza leggere l'implementazione;
- **veritiero**: il test esercita il package e il percorso applicativo previsti, non un mock del sistema che dovrebbe verificare.

### Static checks

Devono fornire la prima linea di difesa:

- Ruff format e lint;
- mypy strict;
- codice/import inutilizzati e dipendenze dichiarate;
- dipendenze e cicli architetturali;
- validazione degli schemi e delle migration;
- workflow GitHub;
- segreti e vulnerabilità;
- artefatti generati non aggiornati;
- build/installazione del package, se pubblicabile;
- verifica delle versioni Python dichiarate.

I type checker non dimostrano che i dati ricevuti siano validi a runtime. Questa garanzia viene dai parser/schema e dai test sui confini.

### Unit test: pochi e specialistici

Usarli soprattutto per:

- algoritmi puri;
- parser e normalizzatori;
- state machine complesse;
- calcoli combinatori;
- property-based testing;
- invarianti con molte combinazioni;
- casi limite difficili da riprodurre tramite un flusso completo;
- policy di retry, backoff e transizione quando il comportamento è isolabile.

Non testare getter, wiring banale, dataclass-generated repr o dettagli interni solo per aumentare la coverage. Non scrivere un test per ogni metodo: scrivere test per i comportamenti che possono rompersi e che hanno un significato per il sistema.

### Integration test: la parte principale

Testare i casi d'uso attraverso la loro API pubblica, collegando più componenti reali:

- dominio;
- application service;
- adapter;
- database temporaneo o container effimero;
- filesystem temporaneo (`tmp_path`);
- server HTTP locale / ASGI test client;
- queue o processi locali, quando economicamente possibile;
- serializzazione e validazione dei contratti;
- transazioni, commit e rollback.

Mock e fake devono essere applicati ai **confini esterni**, non alle funzioni interne:

- provider LLM;
- email;
- pagamenti;
- servizi SaaS;
- clock e casualità;
- HTTP provider esterni;
- servizi troppo costosi o non deterministici;
- code gestite da terzi quando non è disponibile un broker effimero realistico.

Preferire fake con comportamento esplicito, server locali e strumenti di intercettazione HTTP sul confine di rete. Non mockare repository, domain service o use case se l'obiettivo è verificare che collaborino correttamente: è il caso tipico in cui un mock conferma solo il codice scritto nel test.

Usare fixture pytest per lifecycle e risorse, non come service locator implicito. La fixture deve rendere visibili dipendenze, scope e cleanup. Preferire `tmp_path`, `monkeypatch`, `caplog`, `capsys` e fixture dedicate invece di directory condivise, environment globale e file fissi. Evitare fixture autouse che modificano il comportamento di tutto il repository senza che il test lo dichiari. La fixture session-scoped è ammessa per infrastruttura costosa ma deve essere isolata e ripetibile. ([pytest fixtures](https://docs.pytest.org/en/latest/reference/fixtures.html))

Quando si testa una UI, non mockare la UI stessa: renderizzare componenti e flussi reali e simulare l'utente. Mockare eventualmente il confine HTTP mediante server fake o strumenti dedicati.

#### Test async e concorrenza

- Scegliere **un solo** modello principale per i test async: plugin pytest-asyncio oppure integrazione AnyIO, secondo framework e runtime; non configurare più modalità `auto` concorrenti.
- Testare le funzioni async attraverso l'interfaccia pubblica e attendere esplicitamente task e cleanup.
- Simulare timeout, cancellazione, errori di rete e shutdown; non usare `sleep()` arbitrari per sperare in una race condition.
- Non condividere sessioni ORM o client non thread-safe tra task concorrenti.
- I test di concorrenza devono essere riproducibili e avere sincronizzazione esplicita (eventi, barrier, queue), non dipendere dalla velocità della macchina.
- Le prove stress/load non appartengono alla normale fast lane; eseguire in job dedicati o slow lane.

### E2E: pochi flussi ad alto valore

Coprono:

- journey utente critici;
- autenticazione e autorizzazione;
- integrazione frontend/backend;
- avvio reale dei processi;
- integrazione con il database e i servizi essenziali;
- deployment smoke test;
- errori ad alto rischio e recovery.

Playwright deve conservare trace, screenshot e log sui fallimenti, non su ogni esecuzione. Se non esiste una UI browser, E2E può significare avvio completo dei processi e chiamate ai confini pubblici: non installare Playwright browser solo per dare un nome a una integration suite.

**Keyboard-first** (progetti con UI): gli agenti sono deboli con il mouse e con i dettagli pixel-perfect. Il prodotto SHOULD essere interamente usabile da tastiera e i test E2E SHOULD preferire interazioni da tastiera quando equivalenti. In fase di implementazione UI, usare sempre i componenti del design system del progetto, mai elementi HTML grezzi fuori dal design system, e studiare il linguaggio visivo esistente prima di aggiungerne.

### Property-based testing

**Hypothesis** MAY essere usato per verificare invarianti su insiemi di input generati: serializzazione round-trip, parsing, normalizzazione, invarianti di dominio, ordinamento, date, calcoli e state machine. È particolarmente utile quando il numero di combinazioni supera quello gestibile con esempi manuali. Quando trova un caso fallente, Hypothesis riduce l'esempio e permette di aggiungerlo come regressione deterministica.

Non applicare property testing a ogni funzione. Definire strategie con vincoli realistici, limitare i costi della suite e salvare i regression example quando un bug viene scoperto. ([Hypothesis](https://hypothesis.works/))

### Test LLM, se presenti

La CI deterministica usa:

- provider fake;
- output registrati/versionati, quando il contenuto non è sensibile;
- validazione degli structured output con lo schema runtime canonico;
- simulazione di timeout, rate limit, retry, errori di rete e output malformati;
- verifica dei tool call e dei permessi;
- golden test solo per contratti stabili, senza dipendere da variazioni cosmetiche del testo generato.

Le chiamate live appartengono a:

```text
just test-live
```

o a workflow schedulati. Non bloccano la normale fast lane salvo decisione esplicita. I test con provider reali hanno budget, chiavi isolate, limiti di costo e policy privacy; non devono essere eseguiti accidentalmente da un agente durante `just ci`.

### Regole generali

Per ogni bug fix (**zero-bugs policy**: i bug hanno priorità sulle feature e vanno replicati e corretti al più presto):

1. riprodurre il problema con un test fallente;
2. verificare che fallisca per la causa corretta;
3. implementare il fix;
4. verificare il caso originale e i casi adiacenti.

Per ogni feature:

- happy path;
- errori previsti;
- boundary case;
- dati esterni mancanti, malformati o non validi;
- permessi;
- retry/idempotenza, quando rilevanti;
- timeout/cancellazione, quando rilevanti;
- compatibilità dei contratti esistenti.

I test devono verificare comportamento osservabile, non dettagli d'implementazione. Un refactoring che non cambia comportamento non dovrebbe richiedere la riscrittura della suite.

Il progetto usa `pytest` come test runner. Alla data di verifica pytest 9.2.0 include il supporto ufficiale a Python 3.15; `coverage.py` 7.17.2 supporta Python 3.11–3.16 alpha e misura la branch coverage. Le versioni esatte sono point-in-time e vanno riverificate in bootstrap. ([pytest changelog](https://pytest.org/en/stable/changelog.html), [coverage.py](https://coverage.readthedocs.io/en/7.17.2/))

### Coverage

La coverage è un guardrail, non l'obiettivo finale.

Policy:

- includere tutti i file sorgente del package, anche quelli mai importati dai test;
- monitorare line/statement e soprattutto branch coverage;
- conservare threshold versionati;
- impedire qualsiasi diminuzione rispetto a `main`;
- richiedere copertura significativa del codice modificato;
- documentare ogni esclusione e motivarla;
- non imporre automaticamente il 100%;
- non scrivere test privi di valore soltanto per coprire una riga;
- misurare il package installato, non una copia o una directory diversa da quella effettivamente distribuita.

La branch coverage è importante perché il 100% delle righe non implica che entrambe le diramazioni di un `if` siano state esercitate. `coverage.py` supporta branch measurement e contesti dinamici che aiutano a risalire al test che ha eseguito una riga. ([coverage.py — branch coverage](https://coverage.readthedocs.io/en/latest/branch.html), [contexts](https://coverage.readthedocs.io/en/latest/contexts.html))

I threshold sono **a cricchetto** (§ 1): la recipe

```text
just coverage-raise
```

può alzarli automaticamente al valore corrente, ma nessun comando deve poterli abbassare. Una modifica che abbassa i threshold nel diff è un segnale di aggiramento del gate e deve bloccare la review.

Se disponibile nel piano GitHub o tramite un servizio dedicato, caricare un report Cobertura/coverage supportato e configurare il ruleset con:

- minimum coverage;
- maximum coverage drop pari a zero;
- eventuale coverage minima del codice nuovo.

In assenza di funzionalità native, usare il quality gate di SonarQube, Codecov o uno script CI che confronta il report corrente con `main`. La soglia di base è stabilita su una baseline reale del repository, non inventata per partire dal 100%.

### Testing del package distribuito

Se il progetto produce un package installabile:

- `just package-check` esegue la build source distribution e wheel;
- installa il wheel in un virtualenv temporaneo e pulito;
- esegue smoke test e import dal package installato;
- verifica metadata, entry point, package data e file inclusi;
- prova l'installazione fuori dalla directory del repository, per rilevare import shadowing;
- non considera sufficiente un `pytest` che importa accidentalmente il package dalla working tree.

---

## 7. Documentazione e decision record

### La documentazione è infrastruttura per l'AI

In un progetto sviluppato da agenti, la documentazione non è (solo) per gli umani: è **il meccanismo principale per iniettare buon giudizio nell'AI**. Le regole astratte vengono ignorate con una certa frequenza; le decisioni passate, concrete e motivate, vengono seguite con affidabilità molto maggiore. Per questo i decision record non sono burocrazia: sono il modo in cui il progetto accumula giudizio riutilizzabile.

### Gerarchia delle fonti

```text
PDR            → comportamento e decisioni di prodotto
ADR            → decisioni tecniche e architetturali
Test           → comportamento eseguibile
Codice         → implementazione
Runbook        → operazioni
AGENTS.md      → modalità di lavoro degli agenti
```

Evitare la duplicazione: ogni informazione ha una fonte canonica e gli altri documenti la collegano.

Usare Markdown, JSON, TOML e Mermaid. Non affidare informazioni importanti esclusivamente a immagini o diagrammi non testuali. I frammenti di configurazione in documentazione devono essere aggiornati e verificabili; quando possibile, mantenere esempi eseguibili o testati.

### ADR — Architecture Decision Record

Convenzioni:

- **una decisione per file**, nome `NNNN-titolo-breve.md`, numerazione monotona, ID mai riusati;
- un'ADR `active` **non viene mai modificata**: una nuova ADR la sostituisce marcandola `superseded`;
- l'ADR nasce **nello stesso commit** del codice che implementa la decisione;
- le ADR sono anche l'**artefatto di review** per l'umano: più leggibili del diff riga per riga;
- la directory delle ADR è configurabile nel `conventions.conf` in radice (`ADR_PATH`, default `docs/adr`); il comando/skill `/create-adr`, se presente nel client, mantiene anche il `README.md` indice della directory — unica fonte dell'elenco e dello stato delle decisioni.

Quando serve un'ADR: nuova dipendenza significativa, strategia di storage, framework runtime, modello di concorrenza, astrazione core, pattern cross-cutting, supporto di nuove versioni Python, scelta di type checker, strategia di packaging, deroga a uno SHOULD di questo vademecum.

Quando **non** serve: bug fix, styling, refactoring che preservano il comportamento, aggiornamento patch di dipendenza già approvato dalla policy di manutenzione.

Formato:

```markdown
---
type: ADR
id: "0001"
title: "Titolo breve della decisione"
status: proposed   # proposed | active | superseded | rejected
date: YYYY-MM-DD
superseded_by: "0007"   # solo se status: superseded
---

## Context
Situazione, forze e vincoli che hanno portato alla decisione.

## Decision
**Cosa è stato deciso.** In una o due frasi, in grassetto.

## Options considered
- **Opzione A** (scelta): descrizione — pro / contro
- **Opzione B**: descrizione — pro / contro

## Consequences
Cosa diventa più facile o più difficile. Cosa triggererebbe una rivalutazione.

## Enforcement
Come la decisione è verificata automaticamente: Ruff, mypy, Import Linter, test, CI.

## Migration / rollback
Piano di migrazione e rollback, se rilevanti.

## Advice
*(opzionale)* Input ricevuti prima della decisione.
```

### PDR — Product Decision Record

Serve una PDR quando viene introdotta o modificata una regola osservabile dall'utente o dal business — **ogni decisione di prodotto genuinamente nuova**, indipendentemente dalla dimensione del lavoro (un'epica può non introdurre nulla di nuovo, una piccola storia può introdurre un pattern importante). Non serve per pattern già consolidati. Un agente non deve inventare autonomamente una nuova regola di prodotto in presenza di ambiguità: apre una PDR `proposed` o chiede.

La directory delle PDR è configurabile nel `conventions.conf` in radice (`PDR_PATH`, default `docs/pdr`); il comando/skill `/create-pdr`, se presente, mantiene anche il `README.md` indice della directory — unica fonte dell'elenco e dello stato delle decisioni.

Formato:

```markdown
---
type: PDR
id: "0001"
title: "Titolo breve"
status: proposed   # proposed | active | superseded | rejected
date: YYYY-MM-DD
superseded_by: ""   # solo se superseded
---

## Intent 👁️
Problema e valore per l'utente: cosa deve riuscire a fare.

## Design 🎨
Regole di prodotto decise, con esempi e casi limite.

## Tradeoffs ⚖️
Alternative considerate e scartate, con il perché.

## Non-obiettivi
Cosa questa decisione esclude esplicitamente.

## Acceptance criteria
Criteri di accettazione verificabili.

## Metriche
*(se applicabili)*
```

### Glossary e Vision

`docs/product/GLOSSARY.md` è l'equivalente di prodotto degli overview architetturali: mappa le **astrazioni di dominio** (componenti UI ma anche concetti non-UI: workflow, integrazioni, entità) descrivendo per ognuna perché esiste, a cosa serve e come si usa. È un documento vivo, *derivato* dalla somma delle PDR attive, e va aggiornato quando una PDR introduce o modifica un'astrazione. Il suo scopo operativo è ancorare le specifiche generate dall'AI e ridurre il rework dovuto a nomi e concetti incoerenti.

`docs/product/VISION.md` (MAY): principi di prodotto stabili, usati dall'AI per brainstorm e bozze di spec. L'*intent* resta umano; la Vision gli dà forma verificabile.

### Bundle `agent-docs/` per lookup machine-friendly (MAY)

Un progetto MAY generare un bundle di documentazione derivato, ottimizzato per il lookup degli agenti: `agent-docs/index.md`, `all.md`, `search-index.json` ed eventuali pagine per sezione.

Regole:

- è generato da `just docs-bundle` (script in `tools/scripts/`), mai editato a mano;
- è un **artefatto derivato**, non una seconda fonte: la fonte canonica resta `docs/` e il bundle non introduce contenuto nuovo, quindi non viola il divieto di frammentazione delle regole (§ 8, § 14);
- se committato nel repository, un gate anti-stale verifica che sia aggiornato rispetto a `docs/`; in alternativa è gitignored e generato on demand;
- il deploy opzionale su GitHub Pages vive in `deploy-docs.yml` (§ 11).

---

## 8. Istruzioni per gli agenti AI

### Vincoli su `AGENTS.md`

- **Un solo file canonico**, sempre caricato dall'agente. Semplicità deliberata: niente frammentazione in decine di file di regole.
- **Corto: <200 righe.** Il contesto dell'agente è la risorsa scarsa. Ogni riga deve guadagnarsi il posto; il dettaglio vive nei documenti canonici linkati.
- **Mantenuto dall'AI, approvato dall'umano.** Periodicamente (retrospettiva, § 10) l'agente propone aggiornamenti basati sui problemi incontrati; entrano via PR. Serve una procedura di pulizia contro il *context rot*: regole mai violate perché ormai coperte da un gate vanno rimosse.
- Regola di trasferimento: **quando una guida si dimostra critica e violabile, la si trasforma in un gate** e la si rimuove o alleggerisce dalla guida.
- Le istruzioni sono client-agnostic: i riferimenti a Kilo, Claude Code, Codex, Gemini o Copilot devono essere bridge sottili verso il file canonico, non versioni divergenti delle regole.

### `AGENTS.md` minimale

```md
# Agent instructions

## Start here

1. Read `docs/PROJECT.md` and `docs/INDEX.md`.
2. Read the README of every package/bounded context you will modify.
3. Read the relevant active ADRs and PDRs.
4. Read `docs/memory/project.md` and `docs/memory/environment.md` when present.
5. Use only root-level `just` recipes to build, test and validate changes.

## Working rules

- Keep the change limited to the requested scope. One task = one branch/worktree.
- Before starting, check that gates are green. Never start new work on a
  below-threshold codebase: restore health first, or report the blocker.
- Work test-first: red → green → refactor. For a bug, the first commit is a
  failing regression test. A test you have never seen fail is suspect.
- Leave the code you touch better than you found it, measured by repo gates.
  Do NOT perform unrelated refactors or dependency upgrades.
- Do not add a dependency unless necessary; significant ones require an ADR.
- Preserve existing public APIs unless the task explicitly changes them.
- Keep domain and application code independent from frameworks and runtimes.
- Validate all external data at runtime; annotations and casts are not validation.
- Keep Python code typed; do not introduce unbounded `Any` or unjustified casts.
- When diagnosing runtime behavior, rerun the flow with `LOG_LEVEL=DEBUG`
  and cite the relevant log output as evidence; never leave `print()` or
  temporary debug output behind.
- Do not use `# type: ignore`, `# noqa`, `# pragma: no cover` or `# nosec`
  without a narrow scope, reason and (when applicable) error code.
- Do not edit generated files, `uv.lock` or coverage thresholds manually.
- Before using a library API, verify it exists in the installed version
  (read installed source/stubs/docs); do not rely on memory.
- Do not introduce a product decision without a PDR, nor an architectural
  decision without an ADR, in the same commit as the code.
- Maintain `tmp/commit-message.md` with the proposed commit message for the
  work in progress: reset it when starting from a clean `git status`,
  integrate or fix it otherwise. `tmp/` is gitignored.

## Gate circumvention — prohibited

- NEVER use `--no-verify`, `SKIP`, or otherwise skip hooks/gates.
- NEVER lower coverage or quality thresholds; they only ratchet up.
- NEVER extend ignore-lists, exclusions or suppressions to make a gate pass.
- If a gate fails and you cannot find the fix, stop and report the exact failure.
  Do not work around it.

## Testing

- Prefer integration tests through public APIs; unit tests only where clearer.
- Mock only external or non-deterministic boundaries.
- Tests must be isolated, deterministic, fast and behavioral.
- Never call live external services or LLMs unless explicitly requested.
- Test supported Python versions and package installation where applicable.
- UI: use design-system components; prefer keyboard-driven interactions.

## Validation

- During development run `just precommit`.
- Before completion run `just prepush`.
- If a required command cannot run, report the exact reason.
- Never claim a check passed unless you executed it successfully; quote the
  actual command output in the final report.

## Git safety

- Do not use destructive Git commands.
- Do not rewrite existing commits or force-push unless explicitly requested.
- Do not delete unrelated or untracked files.

## Final report

Report:
1. what changed;
2. tests added or changed;
3. commands executed, with verbatim results;
4. coverage and quality-score deltas;
5. security and static-analysis results;
6. ADR/PDR and documentation updated;
7. Python version and package/lockfile changes;
8. remaining risks or unresolved questions.
```

Creare i bridge, se supportati dall'ambiente:

```sh
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md GEMINI.md
```

Se l'ambiente non supporta i symlink, generare copie e verificarne l'uguaglianza in CI. Le istruzioni specifiche di un client devono solo indicare il documento canonico; non duplicarne le regole.

### `.github/copilot-instructions.md`

Mantenerlo molto breve:

```md
Follow `/AGENTS.md` as the canonical development contract.

During code review, report only concrete correctness, security, regression,
architectural and test-coverage problems. Do not comment on formatting or
style handled automatically by repository tooling.
```

Le istruzioni path-specific vanno aggiunte solo quando esistono regole realmente differenti, per esempio:

```text
.github/instructions/api.instructions.md
.github/instructions/tests.instructions.md
.github/instructions/migrations.instructions.md
.github/instructions/web.instructions.md
```

Non trasformare `AGENTS.md` in un manuale completo: deve indirizzare verso le fonti canoniche senza consumare inutilmente il contesto dell'agente.

### Memoria a breve-medio termine (memory bank del repository)

Gli agenti perdono il contesto tra sessioni, cambi di modello e cambi di client. Gli eventuali sistemi di memoria nativi di un agente sono complementari, ma possono essere opt-in, client-specifici e non versionabili in Git.

Il progetto SHOULD mantenere una memory bank portabile in `docs/memory/`:

- `docs/memory/project.md`: fatti operativi stabili, obiettivi, vincoli e stato sintetico;
- `docs/memory/environment.md`: strumenti, versioni, setup, limiti e peculiarità dell'ambiente;
- `docs/memory/decisions.md`: soltanto sintesi e collegamenti alle ADR/PDR, non una seconda cronologia;
- `docs/memory/sessions/`: digest di sessione rilevanti, non trascrizioni di ogni chat.

Regole:

- all'avvio di ogni task l'agente legge i due file fondamentali `project.md` e `environment.md`, oltre a `AGENTS.md` e `docs/PROJECT.md`;
- quando si fa una decisione, una correzione o si scopre un vincolo significativo, si aggiorna il file appropriato nello stesso commit del codice o in un commit docs dedicato;
- i fatti che stabilizzano e meritano una traccia formale vanno in ADR/PDR; la memory bank ne riporta solo riferimento e sintesi;
- i session digest contengono stato utile a riprendere il lavoro, task aperti, test eseguiti, rischi e prossima azione, non un diario verbatim;
- le informazioni obsolete vengono rimosse o marcate come tali; la memory bank non è un cestino di appunti.

In questo modo il contesto operativo sopravvive anche quando la memoria nativa non è attiva, quando si clona il repository su un'altra macchina o quando un altro membro apre il progetto con un client diverso.

---

## 9. Failure modes degli agenti e contromisure

Tabella di riferimento. La colonna 3G indica dove vive la contromisura principale.

| Failure mode | Causa | Contromisura | 3G |
|---|---|---|---|
| L'agente **ignora le istruzioni** | Insito nei modelli | Regole critiche espresse come controlli automatici, non solo testo | Gate + Guard |
| L'agente **aggira i gate**: abbassa soglie, salta test, estende ignore-list, usa `--no-verify`/`SKIP` | Troppi fallimenti senza rimedio noto | Divieti espliciti in `AGENTS.md`; soglie a cricchetto; guide che insegnano il rimedio (TDD, fix); file di gate protetti da CODEOWNERS; review dei diff sui config | Guide + Gate |
| **Telephone game**: la richiesta viene fraintesa tra orchestratore e coding agent e viene implementata la cosa sbagliata | Passaggi di contesto | Task piccoli; spec ancorate a PDR/Glossary/Vision; review umana sull'artefatto ADR/PDR prima del codice | Guide |
| **Test fantasma**: test senza assertion, tautologici, scollegati dal codice | Pressione implicita verso il "verde"; import errati; fixture che nascondono il percorso reale | TDD: il test deve essere visto fallire; branch coverage; test dell'installazione reale; review comportamentale | Gate |
| **API allucinate**: uso di simboli o parametri di librerie che non esistono nella versione installata | Il modello si affida alla memoria o a documentazione di un'altra major | Regola esplicita di verifica su package installato, stub e documentazione della versione; typecheck e test falliscono l'uso inventato | Guide + Gate |
| **Typing cosmetico**: `Any`, `cast()` e ignore comment rendono verde il typecheck senza verificare il dato | Il modello confonde il tipo statico con la validazione runtime | `mypy --strict`, review delle suppression, validazione schema ai boundary, rifiuto di cast usati come parser | Gate |
| **Completamento parziale dichiarato "done"**: feature cablata a metà | Ottimismo del modello | Definition of Done; integration test sul flusso completo; report con output verbatim | Gate |
| **Report allucinati**: "i test passano" senza averli eseguiti | Insito nei modelli | Regola evidence-based nel report; la CI riesegue e fa fede | Gate |
| **Import shadowing**: un test funziona solo dalla working directory | `src/` non usato, `sys.path` manipolato o package non installato | src layout; package check in virtualenv pulito; esecuzione dalla directory esterna | Gate |
| **Side effect all'import**: import che configura logging, apre connessioni o avvia worker | Moduli Python usati come script globali | Moduli import-safe; bootstrap nel composition root; test d'importazione | Guide + Gate |
| **Stato globale contaminato** tra test o richieste | Singleton, monkeypatch, cache e fixture con scope troppo ampio | Dependency injection esplicita; fixture isolate; cleanup; test paralleli e integration | Gate |
| **Async bloccato o abbandonato** | Chiamate sync nell'event loop, task fire-and-forget | Ownership dei task, timeout, cancellazione, queue bounded, test async dedicati | Guide + Gate |
| **Docs che marciscono**: ADR mancanti, documenti obsoleti, comandi inventati | Judgment call non deterministiche | Docs guard (§ 10), check comandi e bundle anti-stale | Guard + Gate |
| **Context rot**: degrado in sessioni lunghe o per accumulo di regole morte | Contesto degradato/gonfiato | Task piccoli; `AGENTS.md` <200 righe; documenti di recap; retrospettive di pulizia | Guide + Guard |
| **Scope creep**: modifiche non correlate "già che ci si" | Eccesso di zelo | Diff minimo; un task un branch; review del diff; divieto di refactor non correlati | Guide + Gate |
| **Schema drift**: DTO, Pydantic, database e documentazione descrivono contratti diversi | Definizioni replicate manualmente | Schema canonico; generazione/verifica; contract test; migration review | Gate |
| **Degrado lento del sistema**: duplicazione, performance drift, suite lenta | Singole modifiche corrette in isolamento | Guard schedulati; budget di tempo; cricchetto; hotspot git | Guard |
| **Fast path abusato**: diff misto fatto passare per docs-only per saltare i gate | Pressione per chiudere in fretta | Lista dei path esatta nel justfile e protetta da CODEOWNERS; review del diff sui file che definiscono i gate | Gate |
| **Dependency drift**: dipendenze runtime non dichiarate o transitive usate direttamente | Installazione locale più permissiva della build pulita | deptry, lockfile frozen, build e install del wheel in ambiente pulito | Gate |
| **Security suppression creep**: commenti `noqa`/`nosec` usati per silenziare alert | Falsi positivi o fretta di chiudere | Suppression puntuali con motivo e scadenza/issue; code owner review; guard sulle ignore-list | Gate + Guard |

---

## 10. Guards: procedure di fallback

I guard coprono ciò che i gate non possono catturare: *judgment call* (serviva un ADR? una nuova stringa da localizzare? un evento analytics?) e *big picture* (una modifica corretta in isolamento può degradare il sistema nel tempo).

Regole:

- i guard **non modificano direttamente il codice**: producono report e aprono issue/task nel backlog, che il normale flusso di lavoro raccoglie;
- girano tramite `just guards` in locale e tramite `scheduled.yml` in CI (frequenza notturna o settimanale); in assenza di scheduling, l'esecuzione manuale periodica resta obbligo del maintainer;
- ogni guard è report-only: nessun auto-fix, nessun commit automatico;
- ogni alert deve contenere evidenza riproducibile, path, comando, metriche, baseline e azione suggerita;
- i guard non devono diventare un secondo lint rumoroso: ogni segnale deve avere un proprietario e una policy di triage.

Guard predefiniti:

| Guard | Cosa rileva |
|---|---|
| **Docs guard** | Modifiche che avrebbero richiesto ADR/PDR; recap disallineati dalle decisioni attive; link e riferimenti rotti; comandi citati nella documentazione ma assenti dal justfile |
| **Testing guard** | Suite oltre il budget dei 10 minuti; test lenti a basso segnale; fixture globali o test intermittenti; crescita anomala di retry/rerun |
| **Health/refactoring guard** | Hotspot e accoppiamento temporale (CodeCharta/CodeMaat), duplicazione e complessità crescenti (SonarQube), dipendenze inutilizzate o non aggiornate, opportunità di alzare le soglie a cricchetto |
| **Type health guard** | Aumento di `Any`, `cast`, `type: ignore`, moduli non tipizzati, dipendenze non tipizzate e deroghe mypy; trend per package |
| **Security guard** | Nuove vulnerabilità, segreti, permission GitHub eccessive, suppression `nosec`/ignore-list ampliate |
| **Performance guard** | Rallentamenti misurati da probe, regressioni di query, memoria o cold start, se esistono probe |
| **Concurrency guard** | Task non supervisionati, chiamate bloccanti note nel percorso async, queue non bounded, timeout o shutdown non rispettati, se automatizzabile |
| **Localization guard** | Stringhe non tradotte, se esiste i18n |
| **Telemetry guard** | Eventi analytics non tracciati rispetto ai contratti o contenenti PII/segreti, se esiste telemetria di prodotto |
| **Package guard** | Wheel/sdist non riproducibile, file mancanti, entry point rotti, import shadowing o range Python incoerente |

### Retrospettiva di processo

È un guard speciale, da eseguire con cadenza regolare (settimanale o a fine ciclo di lavoro intenso): l'agente analizza i problemi incontrati — gate falliti ripetutamente, istruzioni ignorate, workaround tentati, task riaperti, API allucinate, regression test insufficienti — e propone aggiornamenti a `AGENTS.md`, alle guide e ai guard stessi, tramite PR. È il meccanismo che chiude il loop del § 1: il sistema di regole migliora in base all'evidenza, non per accumulo.

La retrospettiva dovrebbe distinguere:

- regole testuali che continuano a essere ignorate e vanno trasformate in gate;
- gate rumorosi o costosi che devono essere migliorati, non rimossi;
- regole ormai garantite automaticamente che possono essere eliminate dalle guide;
- failure mode nuovi che richiedono test, controlli o runbook;
- istruzioni obsolete che alimentano context rot.

---

## 11. Integrazione GitHub

### Workflow minimi

```text
ci.yml
security.yml
package.yml           # se il progetto produce package/release
e2e.yml               # se esiste una UI o un journey browser
scheduled.yml         # guards, slow test, live eval, compatibility
release.yml           # se esistono release
deploy-docs.yml       # se esiste un bundle agent-docs o un sito docs
```

I workflow devono reagire almeno a:

- `pull_request`;
- push su `main`;
- `merge_group`, se viene usata la merge queue;
- `workflow_dispatch`.

Job consigliati:

```text
quality
integration-and-coverage
package-build         # se applicabile
python-compatibility  # se il range Python lo richiede
security
e2e                   # condizionale
dependency-review
```

`quality` esegue le recipe statiche aggregate. La CI sincronizza l'ambiente in modalità locked (`uv sync --locked` o comando equivalente previsto dalla versione fissata) e **non modifica il lockfile**. Un lockfile non aggiornato rispetto a `pyproject.toml` deve far fallire la pipeline, non essere corretto implicitamente dal runner.

`scheduled.yml` ospita l'esecuzione automatica dei guard (§ 10): apre issue con i risultati, senza committare codice.

### Matrice Python e build

- Eseguire la suite sulla versione Python minima dichiarata e sulla versione stabile target adottata.
- Aggiungere versioni intermedie solo se il progetto supporta davvero quel range o se una dipendenza critica richiede un test mirato.
- Per librerie, verificare l'installazione e i test di ogni minor supportata.
- Per estensioni native, verificare wheel disponibili per OS/architettura e testare i build necessari.
- Per app con deploy unico, la CI principale deve corrispondere il più possibile al runtime di produzione.
- Non aggiornare automaticamente la minor Python in un workflow di produzione senza PR e compatibility suite.

### Ruleset di `main`

Configurare:

- modifiche soltanto tramite PR;
- status check obbligatori;
- conversazioni risolte;
- nessun force push;
- nessuna cancellazione del branch;
- squash merge;
- approvazione umana per PR prodotte da agenti;
- Code Owner review per file critici;
- code scanning, dependency review e coverage gate, quando disponibili;
- merge queue se operano molti agenti in parallelo.

Il default è un solo agente di coding alla volta: il collo di bottiglia è la validazione umana, non la generazione. Il lavoro parallelo di più agenti (worktree, merge queue) va introdotto solo quando la capacità di review lo sostiene.

Progetti personali a singolo maintainer MAY adottare un flusso trunk-based con commit frequenti direttamente su `main` e hook come gate unico, ma la scelta va registrata in un'ADR e i divieti di aggiramento restano identici.

I ruleset GitHub possono richiedere status check, risultati CodeQL, Dependency Review, Code Quality e controlli coverage disponibili nel piano e nel repository. La disponibilità e il nome delle funzionalità GitHub cambiano nel tempo: configurare soltanto controlli realmente presenti e attivi.

### `CODEOWNERS`

Proteggere almeno:

```text
/.github/
/AGENTS.md
/CLAUDE.md
/docs/architecture/
/docs/product/
/migrations/
/SECURITY.md
```

E, in quanto **file che definiscono i gate** (contromisura all'aggiramento, § 1 e § 9):

```text
/justfile
/.githooks/
/pyproject.toml
/uv.lock
/.python-version
/.importlinter
```

Se lint, typecheck o coverage hanno configurazioni esterne, proteggere anche quelle:

```text
/ruff.toml
/.ruff.toml
/mypy.ini
/.coveragerc
/coverage.ini
```

I pattern che non esistono nel repository vanno omessi. Le soglie di coverage e i budget di qualità sono file critici, non normali dettagli di implementazione.

### Sicurezza

Abilitare, quando disponibili:

- CodeQL per Python e gli altri linguaggi presenti;
- Dependabot alerts;
- Dependabot security updates;
- Dependabot version updates per ecosistema Python e GitHub Actions, oppure Renovate configurato per aggiornare il lockfile effettivo;
- Dependency Review;
- secret scanning;
- push protection.

Gli aggiornamenti di dipendenze devono produrre PR verificabili, non modifiche dirette a `main`. Gli aggiornamenti patch/minor compatibili possono essere raggruppati con cautela; gli aggiornamenti major richiedono review esplicita e test completi. Il lockfile è parte della supply chain: nessun aggiornamento viene accettato senza controllare versione risolta, licenza, provenienza, vulnerabilità, wheel e test.

Per GitHub Actions:

- permission di default read-only;
- permission elevate solo sul singolo job;
- action esterne fissate a full commit SHA;
- Dependabot incaricato di aggiornarle;
- evitare `pull_request_target` salvo revisione di sicurezza;
- usare OIDC per il deployment invece di credenziali cloud persistenti;
- usare protected environment per produzione;
- non esporre secrets a workflow eseguiti su codice di fork o input non attendibili.

Localmente e in CI:

- `actionlint` verifica sintassi e semantica dei workflow;
- `zizmor` rileva pattern di sicurezza nelle Actions;
- Gitleaks blocca segreti nello staged diff e scandisce la storia in CI;
- pip-audit/OSV-Scanner controllano le dipendenze Python;
- Trivy controlla immagini e artifact distribuiti, se applicabile.

OIDC consente di ottenere credenziali cloud temporanee senza conservare segreti a lunga durata; va preferito quando il provider e la piattaforma lo supportano.

### Artefatti CI

Conservare sui fallimenti:

- log completi e rilevanti;
- report JUnit;
- report coverage e confronto con la baseline;
- trace Playwright, screenshot e video soltanto sui fallimenti;
- output di crash recovery e worker;
- report di static analysis e sicurezza;
- log della build/installazione del package;
- core dump solo quando necessari e senza contenuti sensibili.

Per container o binari/package pubblicati, generare SBOM e artifact attestation quando il livello di rischio e la pipeline lo giustificano. Non allegare artifact con segreti, environment dump o dati personali.

---

## 12. Workflow operativo di un agente

### Prima di modificare codice

0. Verificare che i gate siano verdi: **mai iniziare lavoro nuovo su un codebase sotto soglia**. Se sono rossi, ripristinare la salute o segnalare il blocco.
1. Leggere `AGENTS.md`, `PROJECT.md` e l'indice.
2. Identificare bounded context, package e API pubbliche coinvolte.
3. Leggere test, ADR e PDR rilevanti.
4. Leggere la memory bank quando presente.
5. Verificare versione Python attiva, ambiente `uv` e lockfile; non creare un ambiente parallelo.
6. Verificare se la richiesta contiene ambiguità di prodotto (→ PDR `proposed` o domanda).
7. Definire un piano breve. Il task deve stare in una sessione di lavoro: se il piano non ci sta, spezzare il task prima di iniziare.
8. Creare branch o worktree dedicato.
9. Eseguire i gate di baseline prima di interpretare un errore come regressione propria.

### Durante la modifica

- lavorare in cicli TDD: red → green → refactor;
- produrre il diff minimo coerente;
- seguire pattern già presenti, senza replicare anti-pattern;
- consultare API/stub/documentazione della versione installata prima di usare una libreria;
- non aggiungere nuove astrazioni senza necessità;
- mantenere typing e validazione runtime distinti e corretti;
- eseguire continuamente `just precommit`;
- aggiornare test e documentazione insieme al codice;
- **Boy Scout Rule, riconciliata col diff minimo**: il codice *toccato* va lasciato migliore di come è stato trovato, misuratamente (issue dei gate risolte nei file modificati); refactoring di codice non correlato resta vietato;
- non silenziare check per ottenere una pipeline verde (§ 9);
- ADR/PDR nello stesso commit del codice che le implementa;
- aggiornare `uv.lock` soltanto tramite `uv` quando cambiano dipendenze o vincoli;
- non committare `.venv`, cache, file `.env`, artifact temporanei o credenziali.

### Prima della consegna

- eseguire `just prepush`;
- controllare `git diff` per intero, inclusi i file di configurazione e lockfile;
- verificare che non esistano file generati sporchi o modifiche involontarie;
- verificare coverage, typing, lint, architettura e security;
- se esiste un package, eseguire build e installazione da ambiente pulito;
- verificare che i test usino il package e l'interpreter previsti;
- aggiornare ADR/PDR e recap se necessario;
- compilare il report finale con evidenze verificabili (output verbatim dei comandi).

### Convenzione dei messaggi di commit (SHOULD)

I messaggi di commit SHOULD seguire una convenzione derivata dai conventional commits. È una guida, non un gate: niente commitlint obbligatorio.

Formato: una prima riga riassuntiva con prefisso, una riga vuota, poi una lista puntata Markdown che descrive le cose fatte con dettaglio maggiore ma sintetico:

```text
feat: add retry policy to the payments adapter

- introduce exponential backoff with injected clock in `src/payments/adapters/`
- map provider timeout errors to the shared error taxonomy
- add integration tests for retry, idempotency and terminal failure
```

Prefissi ammessi: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`.

L'agente che fa modifiche mantiene `tmp/commit-message.md` con il messaggio che intende proporre per il lavoro in corso: il file va **azzerato** quando si inizia una modifica partendo da `git status` pulito, **integrato o corretto** altrimenti. `tmp/` è gitignored. Il messaggio deve descrivere l'intero diff, non soltanto la prima parte implementata.

---

## 13. Definition of Done

Una feature o un fix è completo solo se:

- [ ] i criteri di accettazione sono soddisfatti;
- [ ] il comportamento è coperto da test appropriati;
- [ ] ogni bug fix possiede un regression test;
- [ ] ogni nuovo test è stato **visto fallire** prima dell'implementazione;
- [ ] happy path, errori, boundary case e permessi rilevanti sono coperti;
- [ ] timeout, retry, idempotenza e cancellazione sono coperti quando pertinenti;
- [ ] la coverage non è diminuita;
- [ ] nessuna soglia è stata abbassata e nessun gate è stato aggirato; il diff non contiene modifiche ingiustificate a justfile, hook, configurazione Ruff/mypy/coverage o regole architetturali;
- [ ] non esistono nuovi warning o suppression ingiustificate;
- [ ] il typing del codice nuovo e modificato passa il type checker autorevole;
- [ ] i dati esterni sono validati a runtime; non si è usato `cast()` come validatore;
- [ ] non esistono dipendenze runtime mancanti, inutilizzate o dichiarate nel gruppo errato;
- [ ] le regole architetturali passano e non sono stati introdotti cicli;
- [ ] non esistono nuovi import side effect o stato globale non intenzionale;
- [ ] ogni nuovo caso d'uso è esposto sulle superfici decise (CLI, route API, tool MCP, job) con naming parallelo e contratti condivisi, e la mappa delle superfici in `docs/PROJECT.md` è aggiornata;
- [ ] le migration, gli schemi e i contratti sono coerenti e testati;
- [ ] il lockfile è coerente con `pyproject.toml` e non è stato modificato manualmente;
- [ ] package, entry point e wheel sono verificati, se il progetto produce un package;
- [ ] documentazione, ADR e PDR sono aggiornate nello stesso commit;
- [ ] `just prepush` passa;
- [ ] il report finale cita l'output reale dei comandi eseguiti;
- [ ] il messaggio in `tmp/commit-message.md` segue la convenzione (§ 12) e descrive l'intero diff;
- [ ] rischi, dipendenze aggiornate e test non eseguiti sono dichiarati;
- [ ] il diff non contiene modifiche estranee.

---

## 14. Strumenti e pratiche da non aggiungere per default

Non introdurre senza una necessità misurata e un'ADR:

- microservizi;
- Nx o Turborepo solo per orchestrare task Python che `just` già gestisce;
- più package manager contemporaneamente (uv + Poetry + PDM + Pipenv + pip-tools) per lo stesso progetto;
- `requirements.txt` mantenuto a mano in parallelo a `pyproject.toml`/`uv.lock`;
- Black, isort, Flake8, autopep8 o ESLint affiancati integralmente a Ruff;
- più type checker come gate equivalenti (mypy + Pyright + basedpyright + ty);
- ty come unica autorità senza aver prima verificato uscita dalla beta e compatibilità (§ 4);
- tool di dependency analysis sovrapposti senza una lacuna concreta;
- framework web multipli nello stesso deployable (FastAPI + Flask + Django) senza confini espliciti;
- micro-layer e package per singola classe;
- dependency-injection container;
- service locator e registry magici;
- decorator e reflection per risolvere wiring che può essere esplicito;
- ORM Active Record nel dominio;
- Pydantic in ogni oggetto interno quando dataclass e tipi standard bastano;
- `Any`, cast e ignore comment globali per rendere il typecheck verde;
- `sys.path` hacks o import relativi al working directory;
- stato applicativo mutabile a livello di modulo;
- task asyncio fire-and-forget senza supervisione;
- broker, Celery, Dramatiq o altri orchestratori prima che esistano job che li richiedono;
- runtime alternativi o free-threaded come target obbligatori senza un beneficio verificato;
- test live nella normale CI;
- mandato di coverage al 100%;
- snapshot UI estesi;
- grandi `__init__.py` che riesportano tutto;
- test che verificano dettagli d'implementazione;
- skill o file di regole frammentati in parallelo ad `AGENTS.md`;
- auto-fix da parte dei guard o commit automatici in CI.

---

## 15. Ordine di bootstrap di un nuovo progetto

1. Compilare `docs/PROJECT.md` con obiettivo, non-obiettivi, superfici, bounded context e deployable reali.
2. Stabilire la versione minima Python supportata e il runtime target; verificare dipendenze, wheel, provider e deploy. Fissare la patch in `.python-version`.
3. Creare `pyproject.toml` con metadati, `requires-python`, build backend e dipendenze iniziali.
4. Inizializzare `uv`, creare `.venv`, generare `uv.lock` e verificarne l'installazione da clone pulita.
5. Creare il package con layout `src/` e import espliciti; non creare deployable ipotetici.
6. Creare `docs/INDEX.md`, glossario e overview architetturale.
7. Registrare le prime ADR sul runtime, packaging, stack e architettura.
8. Registrare le prime PDR sullo scope di prodotto e i flussi osservabili.
9. Definire dominio, application layer, porte e adapter dei primi bounded context.
10. Configurare Ruff, mypy strict, pytest e coverage.py.
11. Configurare Import Linter e i primi contratti architetturali; aggiungere deptry.
12. Creare una prima integration suite che eserciti il percorso reale più importante.
13. Fissare i threshold iniziali di coverage come **baseline del cricchetto**.
14. Configurare logging strutturato, validazione environment e schema dei confini esterni.
15. Creare il `justfile` e gli hook locali; mantenere i comandi pubblici coerenti con quelli documentati.
16. Aggiungere `AGENTS.md`, i bridge per gli altri agenti e la memory bank minima.
17. Scrivere `docs/development/GETTING-STARTED.md` (§ 3) e linkarlo da `docs/INDEX.md` e `docs/PROJECT.md`.
18. Configurare GitHub Actions, ruleset, CODEOWNERS (inclusi i file di gate) e Dependabot/Renovate per il lockfile scelto.
19. Abilitare CodeQL, secret scanning, dependency review e audit delle dipendenze.
20. Configurare `scheduled.yml` con i guard e calendarizzare la prima retrospettiva.
21. Verificare build/installazione del package se applicabile, e che `just ci` funzioni su una clone pulita.
22. Eseguire almeno un ciclo reale agentico: task, TDD, gate locale, PR, review umana e report finale; correggere le parti del processo che risultano ambigue.

MAY, se si adotta il bundle `agent-docs/` (§ 7): aggiungere la recipe `just docs-bundle` e il workflow `deploy-docs.yml`.

---

Il principio riassuntivo è:

> **Guide corte e vive, gate deterministici a cricchetto, guard che creano task invece di codice. Una sola interfaccia operativa, documentazione gerarchica come iniezione di giudizio, architettura verificata automaticamente, typing rigoroso senza confonderlo con la validazione runtime, TDD come ciclo di default, molti integration test comportamentali e pochi E2E ad alto valore. Il dominio resta indipendente dai framework; i confini validano i dati; il packaging è riproducibile. L'obiettivo non è la velocità iniziale ma non degradare nel tempo.**

---

## Fonti

- Vademecum TypeScript fornito come documento di partenza: struttura, modello 3G, workflow, failure modes, strategia di test, ADR/PDR, governance, guard, Definition of Done e bootstrap sono stati mantenuti e adattati dove pertinente.
- [Python Downloads](https://www.python.org/downloads/) e [Python Developer's Guide — Status of Python versions](https://devguide.python.org/versions/): release e ciclo di supporto Python; verifica puntuale del 13 novembre 2026.
- [Python 3.15 — What's New](https://docs.python.org/3.15/whatsnew/3.15.html): novità della serie 3.15.
- [uv — Working on projects](https://docs.astral.sh/uv/guides/projects/), [uv — Configuring projects](https://docs.astral.sh/uv/concepts/projects/config/), [uv — Python versions](https://docs.astral.sh/uv/concepts/python-versions/), [uv — Workspaces](https://docs.astral.sh/uv/concepts/workspaces/) e [uv — Resolution](https://docs.astral.sh/uv/concepts/resolution/): gestione Python, ambiente, project metadata, workspace e lockfile.
- [PyPA — Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) e [PyPA — src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/): packaging e struttura dei package.
- [Ruff](https://docs.astral.sh/ruff/): formatter, lint e configurazione Python.
- [mypy](https://mypy.readthedocs.io/en/stable/) e [mypy changelog](https://mypy.readthedocs.io/en/latest/changelog.html): type checking strict e supporto del linguaggio.
- [ty](https://docs.astral.sh/ty/) e [repository ty](https://github.com/astral-sh/ty): stato del type checker Astral; beta alla data di verifica.
- [pytest](https://docs.pytest.org/en/latest/) e [pytest changelog](https://pytest.org/en/stable/changelog.html): test runner, fixtures e supporto Python.
- [coverage.py](https://coverage.readthedocs.io/en/7.17.2/), [branch coverage](https://coverage.readthedocs.io/en/latest/branch.html) e [measurement contexts](https://coverage.readthedocs.io/en/latest/contexts.html): coverage e tracciamento dell'esecuzione per test.
- [Hypothesis](https://hypothesis.works/): property-based testing.
- [Import Linter](https://import-linter.readthedocs.io/en/stable/): contratti di dipendenza, layer, independence e cicli.
- [deptry](https://deptry.com/): controllo delle dipendenze dichiarate rispetto agli import.
- [Pydantic — JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema/) e [TypeAdapter](https://pydantic.dev/docs/validation/latest/concepts/type_adapter/): validazione runtime e generazione degli schemi.
- [FastAPI release notes](https://fastapi.tiangolo.com/release-notes/): stato delle release e supporto Python 3.15 alla data di verifica.
- [Typer](https://typer.tiangolo.com/): CLI tipizzate Python.
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/): ORM e Core.
- [MCP Python SDK v2](https://py.sdk.modelcontextprotocol.io/) e [repository ufficiale](https://github.com/modelcontextprotocol/python-sdk): server/client MCP, trasporti e requisiti Python.
- [structlog](https://www.structlog.org/) e [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/): logging strutturato e observability.
- [Test Desiderata — Kent Beck](https://medium.com/@kentbeck_7670/test-desiderata-94150638a4b3).
- [Sensors for coding agents — Birgitta Bockeler](https://martinfowler.com/articles/sensors-for-coding-agents.html).
- Sintesi del workflow AI di Luca Rossi (Refactoring): [My AI Coding Workflow](https://refactoring.fm/p/my-ai-coding-workflow-b09) (modello 3G), [How I Run the Tolaria Project](https://refactoring.fm/p/how-i-run-the-tolaria-project) (validazione, zero-bugs), [How to make AI better at product](https://refactoring.fm/p/how-to-make-ai-better-at-product) (PDR, Glossary), [How to Orchestrate AI Workflows](https://refactoring.fm/p/how-to-orchestrate-ai-workflows) (agents as scaffolding).
