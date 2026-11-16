# PDR-0003 — Tema chiaro/scuro e shell della UI web

- Stato: Accettata
- Data: 2026-11-16
- Supersede: PDR-0002 limitatamente alla presentazione, al tema e alla shell della UI; comportamento del caso d'uso e messaggi restano validi.

## Contesto

Il Vademecum CSS richiede che un frontend predisponga light e dark theme anche quando il prodotto viene rilasciato con un solo tema. La UI del boilerplate era già keyboard-first, ma non aveva un tema, una shell applicativa né token modificabili in un punto. Le app derivate avranno bisogno di questa base dal primo giorno.

Il tema è una scelta osservabile dall'utente: non può essere introdotta come dettaglio implementativo.

## Decisione

La UI web adotta una shell applicativa minima e un tema chiaro/scuro:

- il tema iniziale segue `prefers-color-scheme`;
- un controllo nell'header permette di passare da chiaro a scuro e viceversa, con nome accessibile e tooltip;
- la scelta viene persistita e ripristinata ai reload successivi;
- il tema viene applicato prima del primo paint per evitare il flash;
- lo shell include skip link, `main` semantico, header, footer e area toast globale;
- la schermata `hello-world` usa una card con form, stato iniziale vuoto, stato di caricamento, successo ed errore;
- i messaggi del caso d'uso restano `Hello, <nome>!`, il campo resta `Name`, il bottone resta `Greet` e il default resta `Hello, world!`;
- la UI resta keyboard-first: Enter invia, il focus è visibile e il bottone è un controllo di submit reale.

## Criteri di accettazione

- Il toggle cambia tema immediatamente e la scelta sopravvive a un reload.
- Con sistema in tema scuro, il primo paint è scuro; con sistema in tema chiaro, è chiaro.
- I flussi `hello-world` da tastiera e da bottone funzionano come prima.
- La home e i risultati non hanno violazioni axe automatiche nei flussi coperti.
- La UI è utilizzabile a 360 CSS px senza scroll orizzontale.
- Gli stati idle, loading, success e error sono visibili e comprensibili.
- Il contrasto del testo e dei controlli rispetta WCAG 2.2 AA nelle combinazioni testate.

## Conseguenze

- Il tema è una responsabilità applicativa, non dei singoli componenti: i componenti usano token semantici.
- Un umano può cambiare palette, radius, tipografia e durate di motion modificando `apps/web/src/design-system/theme/tokens.css` e verificando la UI.
- Non vengono introdotti routing, autenticazione, stato globale o altre schermate: restano fuori scope.
- I test E2E crescono di pochi flussi mirati (tema, accessibilità, viewport stretto).

## Alternative considerate

- **Nessun toggle, solo tema di sistema**: rispetta la preferenza del sistema ma non permette all'utente di scegliere; il vademecum richiede la gestione applicativa della preferenza.
- **Solo tema scuro o solo tema chiaro**: non prepara il sistema e costringerebbe a una migrazione visibile dopo.
- **Tema deciso da ogni feature**: duplica token e stati, rende incoerente l'interfaccia e viola il principio di una sola fonte di verità.
- **Persistenza senza bootstrap inline**: più semplice, ma produce un flash di tema al reload.
