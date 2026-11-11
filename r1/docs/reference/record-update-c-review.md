# Persistent profile-record update in C

`r1_event_service_0006c66c` now uses ordinary C with explicit previous/updated
record pointers. It retains the stock null guards, validation of the updated
record, full 12-byte comparison, persistence-before-apply ordering, and the live
record views after persistence. It does not invent a persistence-status gate or
copy a record snapshot before calling the providers.

REA evidence `ev_610c041b62e190f1857b8a78e75590f85cc78fc4270f28bfc67b25fd2f791f71`
comes from the stock ELF SHA-256
`25b4a29af80ec8edab5bd861ba9b74a6e22eab29dc3d7a809a16869e8a140f04`.
Its decoded assembly and pseudocode confirm the sequence. Ghidra reports a
noncontiguous 196-byte body including the separately owned apply routine at
0x6c53c; only the entry sequence 0x6c66c..0x6c6a5 is replaced here. The existing
C apply provider remains canonical. The preserved REA receipt records this
boundary limitation rather than treating the combined pseudocode as one new
implementation.

## Verification

`build/goal-r1-record-update-c/verify.py` compares actual locked application
instructions with the compiled C replacement:

- 360 cases use controlled provider results and mutations, covering both null
  pointers, equal and overlapping/unaligned views, zero/positive/high-bit
  validation and comparison results, and mutations during validation,
  comparison and persistence.
- 512 further cases execute the actual stock/C validator and comparison
  providers. Half enter through the actual stock/source event callback
  0x425b0 with valid or rejected payload lengths and a modeled record read.
- Provider call order/arguments, record bytes, externally visible RAM,
  callee-saved registers, stack restoration and interrupt masks are compared.
  Source execution is prohibited from entering stock code.
- Four separately compiled defects—skipping validation, comparing only eleven
  bytes, bypassing comparison and applying before persistence—are detected.
  A final clean rerun passes.

Persistence and apply are modeled boundaries in this probe; their independently
reviewed implementations are retained. Private stack bytes, incidental return
registers of the void update/callback functions, caller-clobbered registers and
condition flags are outside this C API contract. The real event callback ignores
the update function's return register. This is not physical KV/flash validation.

## Composition audit

`build/sources-goal-r1-record-update-c/report.json`: 777/777 units compile with no
failures or duplicate strong symbols. Application imports remain 124 and
bootloader linker imports remain 22. The update object changes. Another object
hash changes because the generated boot crypto source has a different build
path in debug metadata; its source hash, allocated bytes and allocated-section
relocations are identical. The other 775 payload object hashes are identical.
A strict bootloader link from the current report succeeds with no undefined
symbols. No source-qualification selection or source-plan entry is added.

R1 manifest validation passes. Global sources-check retains the pre-existing
unlisted G2 `resident_rom_thumb_set.S` failure. No device was flashed; full
application linking, physical startup and DFU activation remain outstanding.
