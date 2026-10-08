# P2-20745 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed; image SHA-256 and source/fresh receipt hashes verified.

78B/24-byte frame: entry R1 tested full-width; zero path diagnostics overwrite saved SP0/SP4 argument slots and explicit R0 zero branches to pending epilogue 47B6DA. Nonzero preserves live entry args into next slice.

No final epilogue behavior is inferred beyond the mapped branch. No whole-firmware coverage or data ownership claim is made. No source/gate files changed.
