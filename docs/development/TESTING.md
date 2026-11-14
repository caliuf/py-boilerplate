# Testing

La suite è il gate principale del progetto. I test descrivono comportamento, non dettagli di implementazione. Un test che non è stato visto fallire è sospetto.

## Ciclo TDD

1. Scrivi il test che descrive il comportamento atteso.
2. Eseguilo e verifica che fallisca per la ragione giusta.
3. Implementa il minimo che lo rende verde.
4. Rifattorizza mantenendo il verde.
5. Esegui `just precommit`; prima della consegna `just prepush`.

Per un bug, il primo commit contiene un regression test che fallisce sul codice attuale.

## Piramide

| Livello | Directory | Cosa verifica | Velocità |
|---|---|---|---|
| Unit | `tests/unit/` | Dominio, contratti, renderer, adapter, settings | Millisecondi |
| Integration | `tests/integration/` | API con `TestClient`, MCP in-memory, wrapper `bin/`, smoke | Secondi |
| Contract | `tests/contract/` | CLI su processo reale e coerenza tra superfici | Secondi |
| E2E Python | `tests/e2e/test_full_stack.py` | Processi reali: CLI, API HTTP, MCP stdio | Secondi |
| Web unit | `apps/web/src/**/*.test.ts` | Contratti client e validazione Zod | Millisecondi |
| Web E2E | `tests/e2e/*.spec.ts` | Flussi browser reali con Playwright | Secondi |

La maggior parte dei test è integration o contract attraverso le API pubbliche. Gli unit test sono usati dove il comportamento è più chiaro in isolamento.

## Isolamento

- `tests/conftest.py` rimuove le variabili runtime che potrebbero cambiare il risultato.
- I test double vivono in `tests/support/` e non in `src/`.
- Il `MemoryLogger` registra livello, evento e contesto in memoria.
- I test API usano `TestClient` con dipendenze esplicite, senza stato globale.
- I test MCP usano il trasporto in-memory dell'SDK.
- I test E2E Python usano una porta effimera e terminano il processo nel `finally`.
- Playwright avvia API e Vite tramite `webServer`; Vite usa `strictPort` per non cambiare porta in silenzio.
- I test web non chiamano servizi esterni; il browser e il server locale sono sufficienti.
- Non usare `time.sleep` arbitrari; l'unico polling ammesso è l'attesa di readiness con timeout.

## Determinismo

- Nessuna chiamata a servizi esterni o LLM reali.
- Nessuna dipendenza dall'ordine dei test.
- Nessun filesystem condiviso non isolato: usa `tmp_path`.
- Nessun test che dipende dalla working directory: il repository root è risolto da `tests/support/process.py`.
- Niente snapshot fragili: le assertion verificano proprietà osservabili.

## Contract test

Il contract test cross-surface è il test più importante del boilerplate: verifica che CLI, API, MCP e UI accettino lo stesso input, producano lo stesso output e condividano la stessa tassonomia errori. Se cambi una superficie senza aggiornare le altre, il test fallisce.

`tests/contract/test_web_contract.py` verifica il contratto canonico Pydantic/OpenAPI usato dalla UI; `apps/web/src/contracts.test.ts` verifica il mirror Zod. I due livelli devono restare coerenti.

## Coverage

- Branch coverage attivo.
- Baseline in `coverage-thresholds.json`: 95% linee, 90% branch.
- La coverage attuale è al 100%; la baseline resta più bassa per non imporre test scritti solo per coprire righe.
- `just coverage` genera `coverage/coverage.json` e applica il gate.
- `just coverage-raise` alza le soglie ai valori correnti; non le abbassa mai.
- Le esclusioni sono limitate ai composition root avviati come processo, documentate in `pyproject.toml`.
- La coverage Python non misura il DOM della UI. La UI è coperta da Vitest per i contratti e da Playwright per i flussi browser; non viene inclusa nel report Python.

Non scrivere test tautologici o senza assertion. La coverage è un segnale, non un obiettivo isolato.

## Comandi

| Comando | Contenuto |
|---|---|
| `just test-unit` | Solo unit |
| `just test-integration` | Integration e contract |
| `just test-contract` | Solo contract |
| `just test-e2e` | Solo E2E |
| `just smoke` | Percorso pubblico minimo |
| `just coverage` | Suite non-E2E con coverage |
| `just test-compat` | Suite su Python 3.13 e 3.14 |
| `just test-related` | Unit se ci sono modifiche Python staged |
| `just web-test` | Vitest sui contratti client |
| `just web-check` | Biome, TypeScript, Vitest e build |
| `just test-e2e` | E2E Python e Playwright |

## Aggiungere un caso d'uso

1. Aggiungi il DTO o lo schema in `contracts/` e i test di validazione.
2. Aggiungi il test del dominio e dell'application layer.
3. Aggiungi il contract test che attraversa tutte le superfici.
4. Aggiungi l'integration test specifico della superficie.
5. Aggiungi l'E2E solo se il processo reale introduce un rischio che gli altri livelli non coprono.
6. Se il caso d'uso ha una UI, aggiungi il test Vitest del contratto client e il flusso Playwright.
7. Aggiorna la mappa delle superfici e la PDR.

## Diagnosticare un fallimento

- Riproduci il flusso con `LOG_LEVEL=debug`.
- Isola il livello: unit, integration, contract o processo.
- Non mascherare un fallimento con retry, sleep o skip.
- Se il fallimento è intermittente, cerca stato globale, porta condivisa, ordine dei test o dipendenza dalla rete.
- Se il gate fallisce e non trovi il rimedio, riporta l'output esatto; non aggirarlo.
