# ADR-0008 — Memory bank portabile in `docs/memory/`

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

Gli agenti perdono contesto tra sessioni, cambi di modello e cambi di client. La memoria nativa di un agente è opzionale, specifica del client e non versionata. Un progetto sviluppato in gran parte da agenti ha bisogno di un contesto operativo che sopravviva a un clone su un'altra macchina.

## Decisione

Manteniamo una memory bank in `docs/memory/`:

- `project.md`: fatti operativi stabili, obiettivi, vincoli e stato sintetico.
- `environment.md`: strumenti, versioni, setup, limiti e peculiarità dell'ambiente.
- `corrections.md`: correzioni e vincoli scoperti durante il lavoro.
- `sessions/`: digest di sessioni rilevanti, non trascrizioni.

Regole:

- All'inizio di ogni task l'agente legge `project.md`, `environment.md`, `AGENTS.md` e `docs/PROJECT.md`.
- Una decisione formale va in ADR o PDR; la memory bank ne riporta solo sintesi e riferimento.
- Le informazioni obsolete vengono rimosse o marcate come tali.
- Un digest di sessione contiene stato, task aperti, test eseguiti, rischi e prossima azione.
- La memory bank non duplica la documentazione canonica e non è un cestino di appunti.

## Conseguenze

- Il contesto operativo è versionato e portabile.
- La memoria nativa dell'eventuale client resta complementare, non autoritativa.
- La memory bank richiede manutenzione: un'informazione stantia è peggio di un'informazione assente.
- I guard verificano la presenza dei file fondamentali; la qualità del contenuto resta una responsabilità di review.

## Alternative considerate

- **Solo memoria nativa dell'agente**: non portabile e non versionata.
- **Un wiki esterno**: fuori dal repository, soggetto a drift e a permessi diversi.
- **Trascrizioni complete delle chat**: rumore, costo e rischio di dati sensibili.
- **Nessuna memoria**: ogni sessione ricomincia da zero, con context rot e decisioni ripetute.
