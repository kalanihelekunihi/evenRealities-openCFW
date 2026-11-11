# Device-ID cache flag shares authorization storage

The stock device-ID reader at `0x6ab88` tests byte `0x20006da4`. This is also `device_id_cached_valid`, offset four in the existing authorization state at `0x20006da0`. The C reader previously allocated a separate `.r1.device.id.cache.valid` variable. Its branches could therefore diverge from authorization state changes in a source-linked image.

`native_device_id_reader.c` now reads the existing authorization-state field and removes the separate owner. Cache pointer/length owners and the native register-restoration boundary remain unchanged. This change introduces no new hardware behavior or assembly.

The [receipt](identity-shared-state-review.json) records 144 stock/C pairs covering validity bytes 0, 1, 2 and 255; cached lengths 0, 1, 12, 24, 25 and 255; controller success/failure; and three FICR word pairs. Comparison includes returned R0–R3, destination bytes, shared state, callback arguments, balanced stack and preserved registers. Controller/SVC109 and formatting are modeled. Cached copying executes actual implementations. A control restoring the old separate owner fails when shared validity is one.

The normal source report is `build/sources-goal-r1-identity-shared-state/report.json`: 725 compiled units, no failures or duplicate strong symbols, 178 application imports and 34 bootloader imports. Only the device-ID reader object changes from the preceding profile checkpoint; 724 objects are unchanged. `make sources-check` passes for both devices.

This is shared-state integration evidence. Physical controller execution, complete firmware linking and final RAM mapping remain unfinished. The retained assembly restores the actual saved register words, including controller writes; this review does not justify replacing that ABI boundary with ordinary C.

## Current source-link replay, 2026-11-11

The final-linked reader at `r1_native_device_id_read_boundary` now uses a C
frame wrapper and the shared authorization flag; the retained assembly
described in the historical receipt above is no longer in this source unit.
The ignored replay at
`build/r1-device-id-boundary-replay-20261111/report.json` executes locked
stock `0x6ab88` and the current source-linked reader for 168 paired cases.
It covers cached lengths 0, 1, 8, 24, 25 and 32; destination offsets 0, 1
and 3; eight seeds; and the uncached controller path. The full 64-byte
destination, provider call arguments/order, return SP and R4–R11 match in
every case. Cached copies execute the real linked `memcpy` implementations.
Controller SVC109 and the `snprintf` output are modeled at their entry
boundaries, so this does not verify peripheral behavior or the formatter
implementation. The wrapper's private frame depth and incidental R0–R3
returns are outside the comparison; source callers do not use those returns.

The replay is bound to source ELF SHA-256
`4b640ceffbf99a3102515d7138cadf74412bdd68e7ea67e18d4ce560b0377750`.
The corresponding strict application and bootloader receipts are
`build/r1-link-event-dispatch-ordered-20261111/report.json` and
`build/r1-boot-link-event-dispatch-ordered-20261111/report.json`. Both link
without undefined symbols or retained stock executable code in their
regions. The pinned SoftDevice and physical controller path remain outside
that proof.
