# Independent review: WSF radio handoff

Scope: the stock-adapted WSF event/critical/wake/dispatcher implementation, linked GPIO/radio callback, pinned public source metadata and bounded stock/source verifier. No implementation or shared evidence was edited.

## Result

No blocking code or evidence-integrity issue found. `g2/build/foundation/wsf-radio-simulator/comparison-final.json` passes 180 stock/source cases, including event-mask coalescing, repeat/repost ordering, IDs at and beyond the supported range, critical nesting, wake outcomes, message/timer dispatch order, sleep boundary arguments, and the radio GPIO handoff. The current ELF and all five paths in the verifier’s source manifest match. The four focused `test_wsf_radio` methods pass.

Critical nesting and dispatcher control flow agree with the authenticated stock instructions. `WsfCsEnter` disables IRQs only when the stock nesting byte is zero; `WsfCsExit` decrements it and enables IRQs only when it returns to zero. It does not restore a prior PRIMASK. The stock dispatcher drains task flags in message, timer, handler order, clears handler event bytes under the critical section before callbacks, revisits flags posted while dispatching, calls `WsfMsgFree` after message callbacks, and does not free timer messages. The C’s `while (FLAGS)` and one-byte event storage match that machine behavior.

The provenance correctly separates Apache-licensed public Cordio r20.05c source from the proprietary AmbiqSuite 2.5.1 stock port family. The implementation is labeled an adaptation/reconstruction, not unchanged upstream source. The four pinned public source files and license blob hash-check against the recorded commit. Stock function bytes are checked against the locked image and symbol census.

## Boundaries and sharp preconditions

The synthetic providers replace context classification, RTOS task/ISR notification, timer update/expiry, message dequeue/free, wait and application handlers. The verifier checks their call arguments and ordering, including PendSV request conditions, but does not establish real RTOS queue effects, allocation ownership, scheduler initialization, sleeping, or event delivery. GPIO W1C remains synthetic. The component is not full BLE/RTOS initialization or a firmware image.

WSF IDs 10–15 are not rejected: stock-effective low-four-bit indexing writes into bytes past the ten initialized event slots, including queue-control bytes. The header makes IDs 0–9 a precondition and documents aliases. Callers must also ensure message/timer providers yield valid registered IDs; message/timer handler calls are unchecked. Event masks truncate to eight bits, repeated events coalesce by OR, and zero masks still mark handler work ready and request a wake. Critical nesting must be balanced and stay within the documented 0–254 entry-depth bound; depth overflow/underflow is not made safe. The final-depth exit enables interrupts regardless of the caller’s prior PRIMASK, as stock does.

These constraints are documented reconstruction boundaries, not mismatches in the exercised stock behavior. Invalid IDs or unbalanced critical sections should not be treated as safe general-purpose API inputs.

## Final evidence-accounting follow-up

The final cumulative snapshot reconciles: 234 touch bytes plus 2,130 Apollo bytes equals 2,364 unique traced bytes. The WSF comparison contributes 470 new Apollo bytes. Its five execution-overlay intervals sum to 470; I checked each against the final comparison’s per-PC instruction bytes and SHA-256, then against the initial interval map. Every byte in the overlay was previously unresolved. The comparison remains PASS180 with 1,110 bytes observed including prior shared bodies; that total is not the 470-byte new delta.

The inventory has 28 source files (11 implementation C, 12 headers, five simulator/seam C), all current-hash matched and none ignored. All seven callable-profile ELF hashes and all listed evidence-input hashes match current files. The fresh aggregate is internally consistent at 35 modules, 196 tests, 190 passes, zero failures/errors and seven skips; validation records 40 passing fresh foundation tests. The static WsfOsInit fill-tail evidence is separate from emulator coverage: its guarded native execution diagnostic is INCONCLUSIVE and explicitly excluded. The corrected static call-chain supports conditional handler ID 7 only after the normal initialization/registration sequence; it is not a runtime boot claim.

No stale artifact or accounting contradiction remains in the cumulative report. Updating this review changes its hash; the final build-provenance manifest must be rebound to this updated review file.
