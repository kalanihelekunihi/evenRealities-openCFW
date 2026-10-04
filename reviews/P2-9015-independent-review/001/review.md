# P2-9015 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The 16-byte table artifact matches the pinned image at 0x785250; its four little-endian words are 0x53119D, 0x531331, 0x5315B5, and 0x53135B.
- The table publisher writes to global 0x200610AC+60, while the direct reporter uses the separate global+88 callback slot. The following 14 bytes are exactly ASCII “AttcIndConfirm”.

Limitations:

- Table consumer indexing, bounds, and target meanings remain unresolved; these bytes are data evidence, not code coverage or semantic completeness.
