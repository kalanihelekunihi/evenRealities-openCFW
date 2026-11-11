# RTC 64-bit read-request frame

`r1_clock_backend_slot12` in `r1/src/application/board/native_clock_port.c` now uses a sixty-four-byte union view and directly loads its final eight bytes as the return value. The request is cleared with standard `memset`, whose returned pointer is passed to dispatch. This removes the separate memcpy result temporary and avoids retaining a request pointer in R4. No assembly is added.

Stock entry `0x51494` clears a sixty-four-byte request, dispatches slot `0x10`, ignores operation status and loads R0/R1 from request offset 56. Its frame totals seventy-two bytes: saved LR plus sixty-eight local/alignment bytes. Recorded normal Clang now also uses seventy-two bytes: sixty-four local plus eight saved bytes. The request stays at caller SP minus 72 and incoming R4-R11 remain unchanged at clear, dispatch and registered-handler entry. The previous C body used eighty stack bytes and kept the request in R4.

REA read the complete forty-byte envelope: thirty-four instruction bytes, two padding bytes and four literal bytes. Independent Thumb decoding establishes this function-local contract. A missing provenance-index entry is added as a manual supplement. This review does not newly establish its association with the native backend table; the existing C candidate name is retained.

The normal Clang candidate passes **320 paired cases / 640 executions**, with the actual pinned musl memset and existing C registry dispatch. Only the registered RTC operation is modeled. Cases include eight full-width values, high-bit and all-one words, zero/low-word-only/high-word-only/full responses, operation statuses, full request mutation, cached-device replacement, null device, missing operation, null operation table and interrupt masks. Checks compare the full R0/R1 result, request state, SP minus 72, active R4-R11, final saved-register restoration and masks. Missing operations and unmodified responses return zeroed result words rather than exposing the operation status.

Negative controls reject truncating the result to thirty-two bits, reading the wrong word pair, clearing too few bytes and retaining the old frame/register layout. The union interpretation follows the ARM target's little-endian unsigned sixty-four-bit representation; the fixture establishes the emitted profile's behavior.

The provider-register proof applies to recorded normal Clang, not GCC9 execution. Clearing is normalized by its zeroing contract; internal store widths/order and raw clear-return registers differ. Private save/padding slots, arbitrary aliases, asynchronous observers, null-table fault scratch registers and physical exception delivery are excluded. No physical RTC or electrical behavior is proven.

All 576 R1 units compile and compose without new failures or duplicate strong symbols. All 575 other objects and the other four clock function bodies and relocations are unchanged. Imports remain 164 application / 34 bootloader. The Clang read body shrinks from 52 to 44 bytes. Five generic and four GCC9 profiles compile, but no read-region bytes qualify; existing exact RTC request/wrapper selections remain valid.

The source plan is unchanged. The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,999 source-built bytes (including assembly and data), 642,161 fallback bytes and 248 resource bytes. Full source completeness remains false.

Evidence: [clock-read64-frame-review.json](clock-read64-frame-review.json). Local probes and negative controls are under ignored `build/goal-r1-clock-read64-frame/`; normal report `build/sources-goal-r1-clock-read64-frame/report.json`, hybrid report `build/hybrid-goal-r1-clock-read64-frame/build-report.json`.

The subsequent [default-backend binding review](clock-default-binding-review.md) establishes the native getter/table/slot-12 veneer chain to this request function. The function-local proof above remains unchanged.
