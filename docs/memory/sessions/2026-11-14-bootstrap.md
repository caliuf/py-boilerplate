# Sessione 2026-11-14 — Bootstrap

## 2026-11-14 — Bootstrap del progetto

- Obiettivo: creare `py-boilerplate` da `ts-boilerplate`, applicando il Vademecum Python e mantenendo il caso d'uso `hello-world` su più superfici.
- Fatto: package `src/py_boilerplate` con contratti, dominio, application layer, adapter structlog, CLI, API FastAPI e MCP; toolchain uv/Ruff/mypy/pytest/coverage/Import Linter/deptry; gate locali e CI; docs, ADR, PDR e memory bank; repository pubblico e ruleset.
- Test eseguiti: `just ci` (91 test, 100% linee e branch), `just test-compat` su 3.13 e 3.14, E2E reali, `just package-check`, workflow `ci`, `scheduled` e `security` verdi.
- Decisioni: ADR-0001..0008 e PDR-0001; singola distribuzione; niente UI browser; cspell su Node solo per la documentazione; errori condivisi tra superfici.
- Rischi aperti: licenza non scelta; CodeScene non configurato; il ruleset richiede review e il maintainer usa il bypass per i merge da solo.
- Prossima azione: usare il boilerplate per un caso d'uso reale o mantenerlo come riferimento.
