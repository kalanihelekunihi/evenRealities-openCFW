# Timer cancellation and radio GPIO ordering

Source: `g2/components/foundation/wsf_timer/wsf_timer_stop.c`, `wsf_timer_stop.h`, and `wsf_timer_compat.h`. Selected Cordio WsfTimerStop, wsfTimerRemove and WsfQueueRemove bodies retain their pinned public text and Apache notices; stock-specific sparse layout and reconstructed task-lock adapters are documented in SOURCE_PROVENANCE.json. Existing WSF critical source is unchanged and linked directly; unused scheduler sections are discarded, with no executable stubs.

Stock WsfTimerStop0x52a4d2 holds outer WSF exclusion while private removal0x52a3fc searches the singly linked queue200741b0. A found node is unlinked via0x538cc8 and its started byte at13 is cleared. Allocation, opaque metadata and the removed node's next pointer remain intact. An absent node, even with a nonzero started flag, remains unchanged. Timer storage is borrowed; this path does not free or drain callbacks. Direct private removal lacks outer exclusion around the flag clear and is not a substitute for the public stop.

WSF uses byte nesting depth20075045: entry masks interrupts only at depthzero, exit unmasks when the decremented byte reacheszero. It does not save unrelated incoming PRIMASK. Normal balanced depthzero stop leaves PRIMASKzero even when initiallyone. Byte wrap scenarios are diagnostic invalid nesting, not safe operating contracts.

The contiguous caller slice4b49d0..4b49e6 stops timer20073e64 before disabling GPIO IRQ117, clearing gate136, and applying idle pins93/138. It ends before caller global clearing and transport release52df12. Original non-atomic phases and ignored statuses are retained; no whole-shutdown safety claim.

Saved current comparison: PASS2624 cases,500 distinct original instruction bytes;130 new disjoint bytes in cumulative5174 ledger. Regressions PASS16108 GPIO and6648 control cases. Aggregate43 modules,224 methods,218 pass,6 method skips+1 setupskip,zero failures/errors. Independent review and13-case native rerun are in review/. These results are synchronous synthetic RAM/MMIO comparisons, not hardware scheduling or production compilation proof. Optimized tick remains BLOCKED; zero fully source-complete payloads and no source-built byte-identical bundle.

Remaining providers: asynchronous expiry/dequeue/callback handoff; pending IRQ/NVIC state; transport pad routing, HAL disable/power/uninitialize, command-queue and buffer release. This batch proves neither drain nor allocation lifetime after shutdown.
