# P2-9037 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 74 instruction bytes in 0x530BBC..0x530C08 match the pinned image; mapped literal words match their source locations.
- The header formatter writes eight bytes in the shown order, including low-16 length+4 split across bytes 2–3, then original low-16 length, then type. It calls 52AD04 and returns that child R0. The wrapper calls 52AEC6 and returns saved entry R7 through POP-to-R0.

Limitations:

- No length/pointer validity checks are shown; bytes after the eight-byte prefix are not directly changed by this helper. The downstream helper contract and wrapper meaning remain unresolved.
