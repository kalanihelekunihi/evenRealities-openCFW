# Exact PMIC byte adapters

Two previously unowned routines now live in `board/native_charger_state.c`:

- `0x50690`: call the chip-ID checker, store its low byte through the incoming
  pointer, then return one independently of the checker result.
- `0x5069e`: branch to the existing charge-state byte getter.

The stock name of the first routine suggests status, but its actual callee is
`r1_yhm_chip_id_native` at `0x3530c`. No charger interpretation was substituted.

`tools/build/qualify_sources.py` independently linked the manifest C against
unambiguous stock function bindings and selected the exact 14-byte routine and
4-byte branch. The existing selected charger-state branch remains unchanged.
Only these two regions were appended to its existing source-plan unit.

The actual qualified ELF bodies each pass 4,096 paired stock/C runtime cases:
all low-byte values, four upper-word patterns, and four destination alignments.
The tests check the exact single-byte effect, surrounding sentinels, return,
callee stack depth, preserved registers and tail-call LR. Callees are modeled.

All 580 R1 units compile. The 579 unrelated objects and import sets remain
unchanged. The hybrid now contains 4,061 source-built bytes, 642,099 binary
fallback bytes and 248 resource bytes; its application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
This proves these adapter selections and canonical hybrid identity, not source
completeness or physical hardware operation. Reproducible qualification,
REA readback, runtime fixtures and audits are under
`build/goal-r1-pmic-byte-adapters`; durable evidence is in the adjacent JSON.
