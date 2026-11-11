# Direct C watchdog checker

Current implementation: [C timestamp and void operation ABI](watchdog-pure-c-review.md). The scratch-register preservation described below is historical.

`r1_native_watchdog_check` now contains the sampling, list traversal and expiry logic directly in C. The ten-byte naked bridge and private `watchdog_check_body` are removed from `r1/src/application/board/native_watchdog_manager.c`. The architectural `msr basepri` instruction remains. Two empty compiler constraints capture incoming R3 and restore the sampled word on normal return; they emit no instructions. This is compiler-specific C, not portable ISO C.

Stock entry `0x5da4c` pushes R3/R4/R5/LR. Its sample provider receives the saved R3 word at caller SP minus 16, and a partial provider write preserves the remaining incoming bytes. The direct C frame contains that initialized volatile word and a volatile list pointer. Recorded Clang uses eight local and eight saved bytes; GCC9 uses the same total extent. Both call modeled providers at native depth 16 and pass the timestamp word at SP minus 16. Private saved-register slots differ. A straightforward scalar C local produced a 24-byte frame and was rejected.

After sampling, the C checker traverses the list, reads the low flag byte, skips bit-1 records, reads timestamp then interval and performs the unsigned wrapping timeout comparison. Expiry reloads and sets flag bit 0, writes BASEPRI 64, publishes the fault record and attempts the stock four-byte zero write at `0xffffffff`. That existing stock fault sequence is preserved; emulation stops at the attempted write and does not prove exception handling or physical reset.

REA read the complete 104-byte stock envelope: 94 instruction bytes, two padding bytes and eight literal bytes. Raw Thumb decoding independently establishes the entry, return and literal addresses. The provenance index now includes this previously missing entry as a manual supplement, without treating compilation or behavioral agreement as exact qualification.

Both recorded Clang and scoped GCC9 pass **6,912 paired cases / 13,824 executions each**. Cases vary enabled state, zero-to-three nodes, flags, timestamps, intervals, wrapping samples, zero/one/two/four-byte writes and incoming R3. Checks compare provider sequence and depth, sample pointer, returned R3, controlled node state, final callee-saved registers and interrupt masks. Expiry checks include ordered flag writes, BASEPRI at fault publication, fault-record storage, and attempted invalid-write address/size/value. Lock/list/sample providers are modeled in these cases.

Each compiler also passes **1,024 paired cases / 2,048 executions** using actual stock and C list head/next helpers and linked-list metadata. Lock and sample providers remain modeled. Negative controls reject a zero timestamp seed, signed timeout arithmetic, the wrong BASEPRI value, the old bridge's deeper provider calls, and the straightforward 24-byte C frame.

Active provider callee-saved values, private stack/save slots, flags and void-return caller-clobbered registers other than R3 are excluded. The sampling fixture writes at most the four-byte timestamp word. No physical-device operation is claimed.

All 576 R1 source units compile and compose without new failures or duplicate strong symbols. All 575 other objects and both other watchdog-manager functions are unchanged. Imports remain 164 application / 34 bootloader. Four generic and four scoped GCC9 profiles compile, but no exact regions are selected. The normal manifest and source plan remain unchanged. Scoped GCC qualification retains the existing Nordic-header unused-parameter warning exception.

The canonical hybrid application still matches locked SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: 3,961 source-built bytes (including assembly and data), 642,199 fallback bytes and 248 resource bytes. Source completeness remains false.

Evidence: [watchdog-check-c-review.json](watchdog-check-c-review.json). Local probes and negative controls are under ignored `build/goal-r1-watchdog-check-c/`; the normal report is `build/sources-goal-r1-watchdog-check-c/report.json`, and the hybrid report is `build/hybrid-goal-r1-watchdog-check-c/build-report.json`. The earlier [saved-word frame review](watchdog-c-check-frame-review.md) describes the superseded bridge and retains its historical counterexamples.
