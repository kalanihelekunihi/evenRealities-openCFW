# Full software proximity/slider to gesture and report composition

13 sequence comparisons /327 snapshots match ORIGINAL instructions against independently compiled source: raw proximity filters, baseline/difference/proximity debounce; slider raw/baseline/difference/activity/centroid/position filtering; gesture/speed; calibration/report; EEPROM handling. verify.py reuses preserved fixtures and overlays additive proximity source at0x114000, slider0x112000, gesture support0x110000, calibration/storage0x100000. Those are guest fixtures, not production load addresses. Dependencies, original evidence and interfaces remain in sealed prior batches.

Factory proximity160/finger1000/hysteresis10/on-debounce3/noise40/negative40/baselineIIR1/256 are used. Histories initially contain1900, acquired counts and maxRaw3000 are synthetic. Original/native calls execute explicitly in the same order; no scheduling or physical-time claim. SROM is modeled. Stock slider uninitialized non-X local fields remain excluded; full defined sensor/context/history/counters plus report/storage/gesture are compared. No function entry-return stubs are used for the selected composition.

## Observed behavior and app implications

- Input2400 after idle1900 activates proximity on the seventh processing step in this particular trace: filter settling precedes the three-call debounce. Thus debounce alone is not raw-input response latency. Release follows filtered threshold crossing; no millisecond conversion is supported.
- Inactive slider retains oldX200; release event02 and delayed single-tap04 still occur, but idle stale X causes no new movement. Active/count qualification is essential when consuming coordinates.
- With savedbaseline0, no gesture and no proximity transition, reportTX remains its old contents and calibration flag remains pending. On activation, first emitted report contains savedbaseline0, while RAM/storage save livebaseline1900. Subsequent report contains1900. Apps must not assume reported saved baseline already reflects that report's calibration write.
- With held slider, holdflag10 appears after1000 delivered callbacks, independent of ongoing proximity status. Counter wrap retains modulo32 behavior.
- Command7 parameter0 is rejected and leaves threshold unchanged;1 updates RAM parameter and deferred reset produces hold at one callback increment;65535 postpones hold beyond these sequences. ACK precedes deferred reset/storage. Calls are explicitly sequenced, not concurrent IRQ proof.
- Injected overflow-only status4 survives the producer and can trigger application proximity code2 despite proximity bit1 remaining clear. This is software semantics under synthetic input; hardware overflow occurrence is unverified.

Results.json records every frame, source ELF identity and comparison limits. Command/deferred reset cases, wrapped callback counts, negative-baseline reset, three saved-baseline ordering cases, hold/proximity overlap and inactive/stale reports are covered. No shared state, production firmware, index, commit, accepted checkpoint or device changed.
