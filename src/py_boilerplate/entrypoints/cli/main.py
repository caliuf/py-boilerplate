"""Bootstrap del console script CLI (composition root, escluso da coverage)."""

import os
import sys
from collections.abc import Sequence

from py_boilerplate.entrypoints.cli.app import run


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point del console script `py-boilerplate`."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    return run(
        arguments,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=os.environ,
        is_tty=sys.stdout.isatty(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
