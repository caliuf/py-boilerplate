#!/usr/bin/env bash
# run-checks.sh — esegue una lista ordinata di comandi di gate.
#
# Con GNU parallel installato i comandi girano in parallelo (uno slot per core),
# ma stdout/stderr restano raggruppati per comando e stampati nell'ordine
# originale della lista (--keep-order), non in ordine di completamento.
# Senza GNU parallel i comandi girano in sequenza, nello stesso ordine.
#
# Fail-late: TUTTI i comandi girano sempre, anche dopo un fallimento
# (--halt never), così un singolo giro mostra ogni problema. Lo script esce
# non-zero se almeno un comando ha fallito.
#
# Colori: su terminale interattivo esporta FORCE_COLOR=1, JUST_COLOR=always e
# RUN_CHECKS_COLORS=1; con NO_COLOR o output non-TTY resta plain.
#
# Carico: sulla macchina di sviluppo principale (whoami = caio) i comandi
# girano sotto nice -n 19. In CI l'utente non è mai caio.
#
# Uso:
#   tools/scripts/run-checks.sh "just format-check" "just lint" ...
#
# Escape hatch: RUN_CHECKS_SEQUENTIAL=1 forza il percorso sequenziale.
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: run-checks.sh <command> [<command>...]" >&2
  exit 64
fi

if [ -n "${NO_COLOR+x}" ] || [ ! -t 1 ]; then
  export NO_COLOR=1
  unset FORCE_COLOR
elif [ -z "${FORCE_COLOR+x}" ]; then
  export FORCE_COLOR=1
  export JUST_COLOR=always
  export RUN_CHECKS_COLORS=1
fi

nice_cmd=()
if [ "$(whoami)" = "caio" ]; then
  nice_cmd=(nice -n 19)
fi

if [ "${RUN_CHECKS_SEQUENTIAL:-0}" != "1" ] && command -v parallel >/dev/null 2>&1; then
  parallel --no-notice --keep-order --halt never --jobs 0 "${nice_cmd[@]}" bash -c ::: "${@/#/exec 2>&1; }"
else
  rc=0
  for cmd in "$@"; do
    "${nice_cmd[@]}" bash -c "$cmd" 2>&1 || rc=1
  done
  exit "$rc"
fi
