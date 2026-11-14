# Prodotto

`py-boilerplate` è un prodotto interno al repository: un punto di partenza verificato per nuovi progetti Python sviluppati con agenti. Il suo valore non è la funzionalità `hello-world`, ma la catena di garanzie che la circonda.

## Intent

Rendere economico e sicuro l'avvio di un progetto Python agent-first, con:

- un'architettura che non richiede riscritture premature;
- un caso d'uso reale su più superfici;
- gate che impediscono all'agente di dichiarare "fatto" ciò che non è verificato;
- documentazione gerarchica che sopravvive ai cambi di sessione e di modello.

## Utenti

| Utente | Bisogno |
|---|---|
| Maintainer umano | Review piccole, decisioni tracciate, nessuna sorpresa in produzione |
| Agente di coding | Istruzioni canoniche, gate deterministici, feedback locale rapido |
| Sviluppatore che adotta il boilerplate | Placeholder chiari, checklist di adozione, confini già verificati |

## Comportamento osservabile

Il caso d'uso `hello-world` ha lo stesso significato su tutte le superfici:

- default: `Hello, world!`;
- nome valido: `Hello, <nome>!` con spazi rimossi;
- input vuoto o più lungo di 100 caratteri: errore `VALIDATION`;
- il log `saying hello` è emesso una volta per invocazione;
- nessun input viene mai interpretato come codice, SQL, template o espressione.

## Non-obiettivi

- Non è un prodotto SaaS, un'API pubblica o un framework.
- Non gestisce autenticazione, autorizzazione, persistenza o multi-tenancy.
- Non include una UI browser.
- Non promette compatibilità con versioni Python fuori dal range testato.
- Non è una vetrina di tutte le feature possibili: ogni aggiunta deve superare il costo di complessità.

## Criteri di successo

- Un nuovo sviluppatore completa `just setup`, `just doctor` e `just ci` su una clone pulita.
- Un agente può aggiungere un caso d'uso su tutte le superfici senza violare i confini.
- La CI blocca regressioni di comportamento, coverage, typing, architettura, sicurezza e packaging.
- La documentazione canonica resta sotto le 200 righe per `AGENTS.md` e non duplica il Vademecum.
- Il tempo della suite locale resta sotto il budget dei gate.

## Metriche

Il progetto non usa analytics di prodotto. Le metriche osservabili sono quelle dei gate: copertura, tempo della suite, risultati di lint, typing, architettura, sicurezza e package check. Non esiste telemetria runtime.
