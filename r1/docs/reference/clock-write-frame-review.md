# RTC write-request register boundary

`r1_clock_rtc_write` in `r1/src/application/board/native_clock_port.c` now uses the pointer returned by standard `memset` to fill and dispatch its request. The preceding aggregate initializer kept the request address in R6 across clear and dispatch. Recorded normal Clang now preserves native active R4 = offset, R5 = epoch, and incoming R6-R11 at clear, registry dispatch and registered-handler entry. No new assembly is introduced.

Stock entry `0x50df0` uses eighty stack bytes: twelve saved bytes plus sixty-eight local/alignment bytes. The C build uses sixteen saved bytes plus a sixty-four-byte request. Both pass the request at caller SP minus 80. Their private save/padding layouts differ. The request is fully zeroed, then receives the epoch word at offset 44 and the truncated offset halfword at 48. Dispatch status is propagated.

REA read the complete 44-byte stock envelope: forty instruction bytes and a four-byte cached-device literal. Raw Thumb decoding establishes the request size, stores, dispatch and return. The fixture checks the locked application SHA.

The normal Clang candidate passes **480 paired cases / 960 executions**, using the actual pinned musl `memset` and existing C registry dispatch. Only the registered RTC operation is modeled. Cases vary full-width epochs, signed and oversized offsets, operation status, interrupt masks, request mutations, cached-device replacement, null device, missing operation and null operation table. Checks include request contents, native arguments, SP minus 80, active R4-R11, final saved-register restoration and interrupt masks. The null-table path compares the invalid access rather than fault scratch registers or physical exception delivery.

Negative controls reject the preceding R6-temporary candidate, an incorrect offset and an undersized clear. The active-register proof applies to the recorded normal Clang profile; GCC9 qualification is compilation and exact-selection evidence rather than a claim of matching active registers for this write body.

Clear is normalized by its zeroing contract. Native clearing returns the destination end, whereas standard memset returns the destination; the respective callers use those contracts correctly. Internal clearing widths/order, intermediate request-store/cached-load order, private save/padding aliases, asynchronous observers and physical RTC behavior remain outside this proof. This is a provider-boundary improvement, not complete instruction or frame identity.

All 576 R1 source units compile and compose without new failures or duplicate strong symbols. All 575 other objects and the other four clock function bodies and relocations are unchanged. Imports remain 164 application / 34 bootloader. The normal Clang write body is 46 bytes rather than 48, but no profile qualifies it against stock.

Five generic and four GCC9 profiles compile. They retain the previously admitted exact backend wrappers and, under the generic profile, the callback-binding request. The source plan is unchanged. The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,999 source-built bytes (including assembly and data), 642,161 fallback bytes and 248 resource bytes. Source completeness remains false.

Evidence: [clock-write-frame-review.json](clock-write-frame-review.json). Local probes and negative controls are under ignored `build/goal-r1-clock-write-frame/`; normal report `build/sources-goal-r1-clock-write-frame/report.json`, hybrid report `build/hybrid-goal-r1-clock-write-frame/build-report.json`.
