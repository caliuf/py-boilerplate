# CLI

La superficie CLI usa argparse, un registry dichiarativo e un renderer separato. Il comando `hello-world` valida l'input, invoca `say_hello` e scrive dati su stdout, diagnostica su stderr. In non-TTY il default è JSON; `--json` è idempotente. Gli exit code sono definiti in `contracts/errors.py`.

La documentazione completa è in [`docs/PROJECT.md`](../../../../docs/PROJECT.md) e [`docs/development/CODING.md`](../../../../docs/development/CODING.md).
