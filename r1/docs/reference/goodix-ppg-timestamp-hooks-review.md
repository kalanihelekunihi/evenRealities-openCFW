# Goodix PPG timestamp hooks from pinned C

`GH3X2X_TimestampSyncPpgInit` at `0x2ae04` and `GH3X2X_TimestampSyncSetPpgIntFlag` at `0x2ae06` are complete two-byte `BX LR` functions in locked stock. The pinned public democode's `gh3x2x_demo_accppg_sync.c` defines both as empty void functions with the matching GU32/GU8 argument types. They do no timestamp work in this firmware; implementing state changes would diverge from stock.

A generated subset unit selects exactly those two pinned definitions. Five other function definitions are removed from the generated copy to avoid introducing unverified identities or duplicating already-owned functions. The original vendor file, existing profiles and all 575 prior objects stay byte unchanged. The manifest has one new generator and one new source unit. The existing two named frontier entries now point to that unit; no new inventory coverage is inferred from shared `BX LR` bytes.

All 576 units compile without failures or duplicate strong symbols. Application unresolved imports fall from 173 to 171, removing exactly these two names; bootloader imports remain 34 and no imports are added.

384 paired stock/C executions cover register-bit patterns, interrupt masks and condition flags. Each function executes exactly one two-byte instruction, returns through caller LR, preserves R0–R12, SP/LR, BASEPRI, PRIMASK, CONTROL and XPSR, and performs no data read or write. A deliberately state-writing PPG-init variant is rejected. These are complete-body emulator checks, not physical timing or sampling validation.

Five official qualification profiles compile and select both complete bodies. Only their four bytes were appended to the canonical plan after overlap checks. The canonical application still equals locked SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,937 source-built bytes, 642,223 fallback bytes and 248 resource bytes. Full firmware source completeness and G2 gates remain unproven.

A related sweep of three pinned register-driver units compiles all twelve Clang and twelve GCC9 candidates. Both select only the already-covered `GH3X2X_SlotEnRegSet`; no duplicate byte credit is added.

Current normal report: `build/sources-goal-r1-goodix-ppg-hooks/report.json`. [Machine-readable evidence](goodix-ppg-timestamp-hooks-review.json) binds vendor/subset inputs, audit, behavior and negative probes, qualification and canonical image. Probes remain under ignored `build/goal-r1-goodix-ppg-hooks/` and `build/goal-r1-goodix-driver-qualification/`.
