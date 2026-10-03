# Independent review 2709 — handler2 deferred roundtrip

**Result: PASS_SCOPED.** The candidate source, ITCM image, candidate artifact hashes, and handler body hash match their receipts. The isolated replay passed all 64 fixtures without intercepting the firmware functions in the chain.

The decoded handler at `0x428240–0x428378` matches the stated profile-field updates, original secondary-field application, timer-start call, and flag publication. The fixture then explicitly enters the external service routine and exercises flag-2 restoration and stop/disable work. The effect ledger, packed initial return, final PRIMASK return, call sequence, delay count, and frame assertions passed. The corrected packet includes the runtime-read mapping used by its replay; earlier failed attempts remain preserved.

The simulated service invocation does not establish its real timing or caller ownership. Emulation also does not establish physical interrupt or peripheral behavior. The temporary pointer published by the active path is not claimed valid after return. This remains private `accepted:false` evidence.
