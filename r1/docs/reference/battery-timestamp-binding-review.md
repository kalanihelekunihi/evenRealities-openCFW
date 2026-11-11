# R1 low-battery timestamp binding

The unresolved `time_backend_timestamp_thunk` dependency now aliases the existing `r1_time_backend_timestamp` body in `r1/src/application/board/structured_time.c`. The alias uses the same C type and address; it adds no second implementation, data or inline assembly. The normal source manifest is unchanged.

REA confirms the low-battery call at `0x3d90a` reaches stock `0x8ada4`, whose two pointer loads select the registered backend getter and whose `MOVS R0,0` supplies null context before a tail transfer. This is the behavior already implemented by the C timestamp function. It deliberately does not substitute the registration's snapshot context or add null guards absent from stock.

Validation:

- 256 paired native/C thunk cases compare callback-entry register state and caller SP, ordered registration/backend reads, actual result and final registers/masks, callback mutations, and matched null/unmapped backend or null-getter faults. Fault comparisons use Unicorn access faults; physical Cortex-M exception delivery is not proven.
- 1,850 paired cases execute the actual low-battery C policy/frame adapter through the real C timestamp alias to a modeled registered getter. They preserve the original native-record oracle, threshold/count-wrap cases, mutations, return values and register/mask checks. The current union-owned battery storage is bound at its recovered address. Logging, battery voltage, backend getter, KV and thread/event providers remain modeled.
- Wrong-context and added-null-guard variants are rejected.
- All 576 R1 units compile and both relocatable compositions succeed without failures or duplicate strong symbols. Application imports fall from 165 to 164; bootloader imports remain 34. All 575 other objects and the three existing structured-time function bodies/relocations are unchanged. `make sources-check` and `git diff --check` pass.

The battery C body retains its existing private stack and assembly save-frame bridge. Its callback depth can differ from stock; the alias adds no frame and the separate thunk fixture checks native caller-depth behavior. No physical RTC or battery sampling is exercised.

Four Clang and four GCC9 qualification candidates compile and select no regions. The exact source plan remains unchanged. The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,961 source-built bytes, 642,199 fallback bytes and 248 resource bytes. Full source-only linking, hardware operation and source completeness remain unproven; no G2 gate advances.

[Machine-readable evidence](battery-timestamp-binding-review.json) records REA observations, source/dependency hashes, alias identity, strict thunk and battery-chain fixtures, rejected variants, audits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-battery-timestamp-binding/`.
