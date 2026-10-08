# Current touch reconstruction navigation

All locations are additive offline source/analysis, not a production source-complete payload.

| Source family | Analysis directory | Validation boundary |
|---|---|---|
|EEPROM adapters/history/read/write/init|touch-{history,read,init}-closure-2026-10-08 plus earlier dispatch/provider batches|SROM/flash modeled; physical durability unverified|
|Saved-record bootstrap|touch-bootstrap-closure-2026-10-08|Default recovery/readback with synthetic storage|
|Calibration/report/status queries|touch-calibration-closure-2026-10-08|Later gesture/composition batches close its formerly borrowed gesture dependency|
|Gesture speed|touch-gesture-speed-closure-2026-10-08|5042 original/native cases; callback-count arithmetic|
|Gesture state machine|touch-gesture-machine-closure-2026-10-08|4373 cases;874/874 instructionbytes observed; no physical-time proof|
|Slider CPU producer|touch-slider-producer-closure-2026-10-08|915 comparisons; stock undefined non-X bytes excluded|
|Proximity raw filters/debounce|touch-proximity-producer-closure-2026-10-08|1758 comparisons; synthetic acquired counts|
|Both producers→gesture/report/storage|touch-proximity-report-composition-2026-10-08|13 sequences/327 snapshots; SROM/counts/maxRaw synthetic|
|Max-raw wrapper/correction|touch-max-raw-closure-2026-10-08|1440 arithmetic cases/60 wrappercases; wrapper scan explicitly stubbed|
|Scan watchdog/poller|touch-scan-watchdog-closure-2026-10-08|144 calculation/100 poll cases; synthetic IRQcompletion|
|Frame loader/trigger|touch-scan-frame-closure-2026-10-08|60 bus-order comparisons; register backing synthetic|
|Selected saturated-scan composition|touch-saturated-scan-closure-2026-10-08|96 fullbody cases; ONLY mode-switch adapter stubbed, peripherals synthetic|

Remaining static lead: hardware mode switch6ac0 and initialization requestflag setup. No whole-image exhaustion claim. AnalogFIFOresponse and physical timing require external hardware evidence or a validated peripheral model.
