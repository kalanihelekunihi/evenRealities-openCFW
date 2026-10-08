# Offline low-power history interface

reset.c independently reconstructs stock tuner initialization0x7e04; decoder.c is a **new offline/app helper**, not a reconstructed stock consumer or firmware patch. Cortex-M0+ Thumb32-bit context assumptions apply only to reset.c. No complete-image or hardware-scheduling claim.

`touch_lp_history_span(common,capacity,&needed)` first checks common u16+22 bit0, then frame/count/first metadata bytes24..26. The locked project has four slot positions. `touch_lp_history_read` reads little-endian frame-major samples only after the full-span check, requiring an enabled-at-capture bitmask indexed by absolute slot. Disabled positions return UNWRITTEN/value0 without reading retained bytes. Output reports scan counterbyte27 and reset/valid flagsbyte28. Error paths retain caller output; needed becomes0 except invalid pointers.

Caller must supply a proven capacity and stable capture of metadata/history/enable state. The426-byte gap before the next object is not a declared allocation. The API cannot fix producer overflow, infer disabled positions from metadata, guarantee atomicity or establish physical baseline validity. Reset leaves samples/counts/counter intact and disables interpretation.

Evidence: ../../../analysis/touch-lp-history-closure-2026-10-08/REPORT.md (766 selected cases; stock comparisons, original observations and new-helper guards separated). Build remains scratch/offline only.
