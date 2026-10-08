# New validated touch dependencies

| Analysis directory | Source/interfaces | Evidence |
|---|---|---|
|touch-mode-closure-2026-10-08|mode_offline/mode.c, cpu.c, init.c, mode.h|200 mode, 80 wait, 9 field-slice cases|
|touch-scan-mode-composition-2026-10-08|saturated_scan_offline plus actual mode/CPU helpers|720 full cases, mode-entry stub removed|
|touch-pin-control-closure-2026-10-08|pin_control_offline/pins.c, pins.h|216 pin and 72 wrapper cases, ordered bus/PRIMASK|
|touch-regular-mode-composition-2026-10-08|mode_offline/regular.c plus GPIO and pinned public PDL|1080 full cases, no call stubs|
|touch-cap-initialization-closure-2026-10-08|mode_offline/capture.c and init.c plus public PDL capture|722 full cases, no call stubs|
|touch-msclp-attribution-2026-10-08|Pinned unmodified Infineon PDL source|208 exact compiled bytes; Configure has 180 behavioral cases|
|touch-frame-generation-closure-2026-10-08|frame_generation_offline/generator.c, generator.h|192 mask, 180 divider, 1728 CDAC and 1296 closed-frame cases; earlier 864 CDAC-cut cases retained|

Earlier touch/report/storage source remains sealed and unchanged. Existing cumulative index: `../touch-proximity-report-composition-2026-10-08/INDEX.md`.

`build_offline.py` rebuilds these comparators using explicit ARM compiler and PDL-root arguments. PDL pin is35f171...; source comparator CapSense6.10 is247a9a... . Submodule proposals/download hashes are in the attribution directory. No Git/index changes are made.

**Not exhausted:** GenerateAllSensorConfig0x56a4 (calls0x5548/5188), generated base/mode frames0x52bc/5378 and auto-dither0x68ec remain actionable. Their official LP generator source is downloaded. The exact producer's generated cycfg_capsense.h is absent; it limits exact attribution, not continued instruction-grounded semantic recovery. Analog response/factory trims/physical timing require external hardware evidence or a validated peripheral model.
