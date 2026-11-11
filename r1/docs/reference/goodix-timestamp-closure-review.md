# Goodix timestamp dependency closure

Three additional timestamp imports now use their pinned public-democode definitions: `GH3X2X_TimestampSyncAccInit` (`0x2adfa`, empty), `GH3X2X_TimestampSyncFillPpgSyncBuffer` (`0x2adfe`, empty) and `GH3X2X_TimestampSyncGetFrameDataFlag` (`0x2ae00`, returns one). The generated timestamp unit now retains five pinned functions. It still excludes the independently owned accelerometer sink and the unmapped send-to-algorithm helper. No vendor file or compile profile changes.

The identities follow native call paths, rather than matching shared no-op bytes:

- The accelerometer start/cache path calls `0x2adfa` at `0x6f988`, consistent with the pinned HAL's timestamp initializer before board start.
- Execution of the locked register-hook setup fragment (`0x2d994` to `0x2aadc`) captures all nine callback arguments. Its fifth argument is `0x6a4d9`, matching the frame-info hook's position and type in `GH3X2X_RegisterHookFunc`.
- That frame hook calls `0x2ae00` at `0x6a4dc` and can tail-call `0x2adfe` at `0x6a4f0`, with timestamp zero and the frame pointer. REA observes these instructions; its grouped procedure output also includes neighboring/tail-target bodies and does not establish a global function inventory boundary.

The existing AccInit and constant-one frontier/ownership entries now name the correct pinned interfaces. The earlier `goodix_primitives_constant_one_b` definition and declaration were removed. A manual supplement records the two-byte PPG-fill target, whose direct caller is identified above. This does not advance global pseudocode coverage or any G2 gate.

All 576 units compile without failures or duplicate strong symbols. Application imports decrease from 171 to 168, removing exactly these three names, with no added imports; bootloader imports remain 34. All 574 unrelated objects and all 320 other primitive function bodies/relocations are byte unchanged. The existing two PPG hook bodies are unchanged.

960 paired stock/C cases execute the complete five bodies. The four empty hooks preserve the tested integer registers, masks and flags without data accesses. The frame flag returns one and reproduces the native MOVS condition-flag effects. A deliberately zero-returning variant is rejected. These checks do not execute the full frame dispatcher, initialization or physical sampling path.

Five official qualification profiles compile and select all five complete bodies. The two prior regions receive no duplicate credit; only three new regions (eight C bytes) were merged into the existing canonical provider after overlap checks. The canonical application equals locked SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,945 source-built bytes, 642,215 stock fallback bytes and 248 resource bytes. Source completeness remains false. No timestamp algorithm is invented for these stock no-work hooks.

Current normal report: `build/sources-goal-r1-goodix-timestamp-closure/report.json`. [Machine-readable evidence](goodix-timestamp-closure-review.json) binds source ownership, REA, register-hook setup, native targets, body probes, audit, qualification and canonical image. Probes remain under ignored `build/goal-r1-goodix-timestamp-closure/`.
