# Goodix frame-hook C correction

The registered stock frame hook at `0x6a4d8` checks the timestamp frame flag, optionally checks accelerometer enable, then tail-calls either PPG timestamp filling or the I/O dispatcher. It does not call `gh3x2x_rawdata_notify` or dereference frame fields after dispatch. The pinned vendor template adds that notification; the selected generated copy now omits those two lines. Pinned vendor files remain unchanged.

The generated unit also marks the I/O helper `noinline`, preserving the stock opaque call boundary instead of folding its template body into the wrapper. This review corrects the wrapper only. The I/O dispatcher body remains separate reconstruction debt; it is modeled in these probes and is not proved by this correction.

Identity and span evidence come from the existing REA/raw-instruction capture and register-hook setup proof: the fifth registered callback is `0x6a4d9`, and its contiguous entry is `0x6a4d8..0x6a4fd` (38 bytes). The previous frontier size of 376 aggregates noncontiguous tail-target bodies, while its recorded end already denoted the 38-byte entry. The record is now an explicit manual entry-span supplement, and its original fields are preserved in the receipt. This is not new accepted Ghidra coverage or global corpus validation.

384 paired stock/C cases check all timestamp/enable branch outcomes using modeled valid-byte returns, forwarded frame pointers (including null/unmapped values), caller-SP tail transfers, the eight-byte save frame, preserved registers and masks. The wrapper does not read frame data. The I/O and timestamp-fill providers are modeled; null-pointer forwarding here says nothing about safety inside those providers. A negative variant restoring the extra notification is rejected by the native tail-transfer/frame-access contract.

All 576 units compile without failures or duplicate strong symbols. Application imports decrease from 168 to 167, removing exactly `gh3x2x_rawdata_notify`; bootloader imports remain 34 and no imports are added. All 575 other objects, 15 other hook function bodies/relocations and resolved configuration macros are unchanged. The manifest retargets one existing unit to one generated copy; profiles stay unchanged.

Four Clang and four GCC9 qualification candidates compile, selecting no regions. The canonical source plan is unchanged. Its hybrid application still equals locked SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,945 source-built bytes, 642,215 stock fallback bytes and 248 resource bytes. Complete dispatcher/algorithm behavior, physical sampling and full firmware source completeness remain unproven; G2 gates remain unchanged.

Current normal report: `build/sources-goal-r1-goodix-frame-hook-final/report.json`. [Machine-readable evidence](goodix-frame-hook-c-review.json) binds original metadata, native identity, generator changes, probes, audits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-goodix-frame-hook/`.

Follow-up: the dispatcher now has a [bounded C policy/native-frame implementation](goodix-io-dispatch-c-review.md). That separate evidence does not extend this wrapper receipt to physical execution or exact byte identity.
