# R1 RTC timestamp adapter register boundary

The C RTC timestamp adapter in `r1/src/application/board/structured_time.c` now clears its 64-byte request through the existing standard `memset` provider and passes the returned buffer to registry dispatch. Under the recorded Clang profile this removes the request-address temporary from active R4. Stock preserves incoming R4–R11 at the clear and dispatch boundaries; the previous C build held the request pointer in R4 and fails the new native comparison.

REA confirms stock `0x514bc` saves LR and allocates 68 bytes, totaling 72, then calls its zeroing helper. The revised C build also uses 72 bytes, with the request at provider SP and the epoch at request offset 44. It preserves active R4–R11 at the clear, registry dispatch and registered-handler boundaries. The source change introduces no inline assembly or new implementation of memory clearing or device dispatch.

Ninety-six paired native/C cases execute the actual pinned musl `memset` and existing C registry dispatch. They check a fully zeroed request, arguments and stack depth, all saved registers at the three boundaries, epoch values including high-bit/full-width values, ignored operation status, request mutation, cached-device replacement, null device, absent operation and null-table access fault. Only the registered RTC operation is modeled. Both the old R4-temporary candidate and a wrong epoch-offset variant are rejected.

This is a bounded boundary improvement, not complete frame or instruction identity. Native's private word at caller SP minus 8 is unused scratch; C saves R7 there. Aliases into that word are excluded. Native clear and standard memset are compared by their zeroing contract; their internal store widths/order differ. Active saved-register checks apply at call boundaries, and null-table fault scratch registers and physical exception delivery are outside the proof. The fixture executes no physical RTC.

All 576 R1 units compile and both relocatable compositions succeed without failures or duplicate strong symbols. Imports remain 164 application and 34 bootloader. All 575 other objects and the three other structured-time function bodies/relocations are unchanged, including the timestamp alias. `make sources-check` and `git diff --check` pass.

Four Clang and four GCC9 qualification candidates compile and select no regions. The exact source plan is unchanged. The canonical hybrid remains equal to locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: 3,961 source-built bytes, 642,199 fallback bytes and 248 resource bytes. Full source-only integration, hardware operation and source completeness remain unproven. No G2 gate advances.

[Machine-readable evidence](rtc-timestamp-frame-review.json) binds source/dependency hashes, REA observations, real-provider fixtures, rejected variants, audits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-rtc-timestamp-frame/`.
