# YHM2710 clear-tracking native C path

The native charger clear-tracking routine at `0x3543c` and dispatch tail at
`0x5074c` now have C providers in `board/native_yhm_system_track.c`.
The frontier points to this native ABI implementation. The separate high-level
`yhm2710_clear_system_track(device)` convenience API has a different signature
and read-failure policy; it is no longer the native candidate for these entries.

REA read the 204-byte stock code, padding, logging strings and literal envelope.
The C path preserves its 16-byte frame, incoming R2/R3 upper bytes, partial read
and write updates, ignored read status, bit-1 clearing, separate short-circuit
logging-mode reads, exact log strings and encodings, and raw write status.
Callbacks can mutate both exposed words. Empty register constraints retain R4
at provider calls and return the full final words in R2/R3. This unit contains
no executed inline assembly instructions.

The normal product object passes 16,512 paired stock/C cases, including 9,600
callback-mutation cases (33,024 executions). Checks include provider addresses,
stack depth, live R4-R11, strings, modes, final frame words, saved registers,
stack restoration and interrupt masks. Three compiled negative controls fail:
setting instead of clearing bit 1, clearing the upper word and truncating the
write status. Strict GCC compiles but its 32-byte frame fails the native
16-byte provider contract, so GCC behavior remains unqualified.

All 577 R1 units compile and compose without failures or duplicate strong
symbols. The other 576 objects and the existing setter function bytes and
relocations are unchanged. The manifest and import sets remain unchanged at
164 application / 34 bootloader. Official scoped qualification selects the
pre-existing initializer tail and the new four-byte clear tail. Only the new
tail was added to the canonical source plan; the full roots remain unqualified.

The canonical hybrid application still hashes to
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
It contains 4,039 selected source bytes, 642,121 binary fallback bytes and
248 resource bytes. Selected source counts include assembly and data elsewhere.
The normal report is `build/sources-goal-r1-yhm-clear-c/report.json`.

[Machine-readable evidence](yhm-clear-c-review.json) records source hashes,
REA observations, audits and qualification. Ignored probes live under
`build/goal-r1-yhm-clear-c/`. Transport and logging providers are modeled;
physical charger/I2C operation, interrupts, arbitrary private-frame aliases,
faults, concurrency, APSR and other caller-clobbered registers remain unproven.
Original Arm Compiler 5 is unavailable. Complete source-only firmware and
whole-image byte identity from source remain incomplete.
