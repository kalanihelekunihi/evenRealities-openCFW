# Exact native PMIC nine-byte read

Stock `0x35268` passes `(register=0, length=9, output=incoming R0)` to the native
read adapter at `0x3540c`; `0x50748` forwards to it. The frontier previously
assigned these entries to `yhm2710_read_register_9(device,out)`, a contextual
vendor helper that reads one byte at register 9 and returns a Boolean. That
helper remains a separate API; it no longer owns these native entries.

`board/native_yhm_frontend.c` now supplies the correct native block-read entry
and branch. The read wrapper is explicitly noninline so the native call boundary
is retained. `tools/build/qualify_sources.py` selects both exact bodies: ten
bytes plus four bytes. Without that boundary, GCC inlined the read wrapper and
branched directly to the lower record provider; the initial qualification
rejected that root. No executable bytes were hand-authored.

The existing eight-byte read-byte adapter is requalified with its direct
`r1_yhm_register_read_native -> 0x3540d` binding. This replaces the older
relocation alias that bound `r1_yhm_register_read_record` to the wrapper's
address. Its linked bytes and region hash remain unchanged. The existing
Clang six-byte read selection remains untouched. Compiler arguments for the
updated GCC source-plan unit are unchanged; qualification's extra temporary
read-only filesystem mount is not needed by the canonical unit.

The actual native and C wrapper chains pass 3,605 paired cases: 448 per new
entry, 2,688 for the existing byte-read adapter, and 21 null-pointer boundary
cases. Tests cover raw provider statuses, destination alignments, high register
words, untouched/partial/full destination mutations and sentinel preservation.
They check provider arguments, preserved registers, zero stack depth, tail LR,
raw return values and interrupt masks. Null pointers are only passed through
a modeled record provider. Wrong register/count/pointer and Boolean-return
variants are rejected. The record provider and physical transport remain
unverified boundaries.

All 581 R1 units compile, with 164 application / 34 bootloader imports. All 580
other objects, manifest and existing frontend section bytes are unchanged;
the byte-read relocation target name changes intentionally. The hybrid has
4,083 source-built bytes, 642,077 binary fallback bytes and 248 resource bytes.
Its application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Complete source-only rebuilding, arbitrary transport faults/aliases and
concurrency remain unproven. Reproducible qualification, REA readbacks, runtime
fixtures and audits are under `build/goal-r1-yhm-block-read-c`; durable results
are in the adjacent JSON.
