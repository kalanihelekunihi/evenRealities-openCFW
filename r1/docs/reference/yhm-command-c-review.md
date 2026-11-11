# PMIC command-byte C adapter

`board/native_pmic_charge_decode.c` now supplies command `0x35684` and its
forwarding branch `0x50848`. The command writes byte `0xf8` to register 2,
with count one, through `r1_yhm_register_write_native` at `0x35760`. It keeps
the saved incoming R3 word's high bytes and restores the entire word after
the transport call, including any provider modifications. The raw transport
status is returned unchanged. The historical single-wire name does not replace
the actual YHM transport boundary with a separate inferred driver.

Both root and branch pass 896 paired stock/C cases covering seven raw statuses,
four saved-R3 seeds, no/byte/halfword/word provider writes and four mutation
values. Live callee registers, final R0/R3, SP and interrupt masks are checked.
Wrong command, high-byte clearing and discarded transport-status variants are
rejected. REA readback independently confirms the native command and branch.

The root remains a behavior candidate: C exposes a 16-byte provider frame and
buffer at caller SP-12, while native uses eight bytes and SP-8. The fixture
explicitly normalizes that pointer; it does not prove stack-layout equivalence.
Normal/O2/Oz and frame-pointer probes did not produce a compatible root in the
examined configurations. Arbitrary stack aliases and electrical PMIC behavior
remain unproven, and transport is modeled.

`tools/build/qualify_sources.py` selects only the exact four-byte forwarding
branch. Its C source-plan unit binds the branch to the native command entry;
the command body remains fallback in the hybrid. No opcode data or hand-written
branch was added. All 581 R1 units compile with the same 164/34 import sets.
The 580 unrelated objects and previous two PMIC function sections/relocations
are unchanged. The hybrid now contains 4,065 source-built bytes, 642,095 binary
fallback bytes and 248 resource bytes; application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

Reproducible probes, counterexamples, REA evidence and qualification are under
`build/goal-r1-yhm-command-c`; durable evidence is in the adjacent JSON.
Complete source-only firmware identity and physical validation remain open.
