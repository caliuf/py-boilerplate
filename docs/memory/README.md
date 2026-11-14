# Memory bank

La memory bank è il contesto operativo portabile del progetto. Vive nel repository, è versionata e sopravvive a cambi di sessione, modello, client e macchina.

## File

| File | Contenuto |
|---|---|
| `project.md` | Fatti stabili, obiettivi, vincoli e stato sintetico |
| `environment.md` | Tool, versioni, setup, limiti e peculiarità dell'ambiente |
| `corrections.md` | Correzioni e vincoli scoperti durante il lavoro |
| `sessions/` | Digest di sessioni rilevanti, non trascrizioni |

## Regole

- All'inizio di un task leggi `project.md`, `environment.md`, `AGENTS.md` e `docs/PROJECT.md`.
- Aggiorna il file appropriato nello stesso commit del codice o in un commit docs dedicato.
- Una decisione formale va in ADR o PDR; qui riporta solo sintesi e riferimento.
- Rimuovi o marca come obsoleto ciò che non è più vero.
- Non duplicare la documentazione canonica e non usare la memory bank come cestino di appunti.
- Non inserire segreti, token, dati personali o output di environment.

Il formato di un digest è descritto in [`sessions/README.md`](sessions/README.md).
