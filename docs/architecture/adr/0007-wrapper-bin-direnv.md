# ADR-0007 — Wrapper `bin/` e stratificazione environment con direnv

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

Gli agenti e gli umani lanciano gli stessi comandi da directory diverse. L'environment locale deve essere riproducibile, ma i segreti e le preferenze personali non devono finire nel repository. Le librerie Python non devono leggere file `.env` o variabili globali in autonomia: la configurazione va risolta nel composition root.

## Decisione

Adottiamo una stratificazione esplicita:

- `.env.default` è il floor committato, senza segreti.
- `.env` è locale e gitignored.
- `.envrc` carica `.env.default`, poi `.env`, poi `.envrc.local` (gitignored) via direnv.
- `bin/py-boilerplate-hello-world` risolve il repository, richiede `uv` e `direnv`, verifica che l'environment del chiamante sia autorizzato e lancia `uv run --project <repo> py-boilerplate hello-world`.
- L'applicazione legge solo variabili già presenti nell'environment; non carica `.env` da sola.

## Conseguenze

- Il floor è identico per tutti; le differenze locali restano fuori da Git.
- Il wrapper fallisce con un messaggio utile se `direnv` manca o l'`.envrc` non è autorizzato.
- I test coprono il caricamento dell'environment, la precedenza del flag CLI, il fallback al default, il blocco direnv e l'assenza di direnv.
- Il flusso è supportato su Linux e WSL; non è un obiettivo Windows nativo.
- `direnv allow` va eseguito una volta per directory; `just setup` lo fa per il repository.

## Alternative considerate

- **Caricare `.env` nell'applicazione**: nasconde la provenienza della configurazione e rende i test meno deterministici.
- **Nessun wrapper**: ogni chiamante deve conoscere il path del repository e il comando esatto.
- **Solo variabili globali della shell**: non riproducibile e soggetta a stato implicito.
- **Un file `.env` committato**: rischio di segreti e conflitti tra ambienti.
