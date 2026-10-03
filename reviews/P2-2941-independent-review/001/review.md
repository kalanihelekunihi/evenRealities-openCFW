# Independent review 2941/001

**REVISE_PROSE**; `accepted` remains false.

The locked source hash, image mapping, candidate output hashes, body digest, and all 311 instruction byte encodings match. The instructions tile the full half-open interval `[0x42B6B8, 0x42B9BA)` (770 bytes). All PC-relative literal values match the source bytes. Isolated replay passes. I independently accumulated the original subtract immediates, including the literal subtraction, and recovered all 24 dispatch keys and branch targets; they exactly match `dispatch.json`.

The pseudocode needs a gate-bit correction. At both selector sites the code executes `LDRB`, `LSLS ..., #31`, and `BPL`, so it tests bit 7 (`0x80`) of the freshly read byte at `0x2002708C`. Calling this the low bit is inaccurate. This is a static decode review; it does not validate dynamic inputs, physical MMIO behavior, global ownership, or canonical admission.

Candidate receipt SHA-256: `78a7254c7bd025889d90f1af707c22c0f2a8d1cd24bcdbf9317a7cc2f80eb065`.
