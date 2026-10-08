# Touch reconstruction navigation

| Delivered family | Location | Validation boundary |
|---|---|---|
|Earlier mode, pins, capture, initialization, per-sensor frames|../touch-mode-closure-2026-10-08/INDEX.md|7,539 reported cases across selected suites; see each stub/physical limit|
|All-slot orchestration|../touch-all-slot-closure-2026-10-08/REPORT.md|144 preserved original/source cases; five active/four LP slots; no call stubs|
|Base/mode/pin-function frames|../touch-base-frame-closure-2026-10-08/REPORT.md|2,304 fresh original/source cases; full frame/context; no call stubs|
|Auto-dither and mode7 composition|REPORT.md|240 fresh cases; full software helpers and public PDL; synthetic MMIO/SFLASH|
|Public source attribution|../touch-msclp-attribution-2026-10-08/REPORT.md|208 exact compiled bytes; Configure differs24 bytes and is behavioral only|

New sources: g2/components/touch/all_slot_offline, base_frame_offline, auto_dither_offline. build_offline.py builds new base/dither comparators; verify.py here and in base-frame directory execute originals. Current rebuild receipts point to scratch/tmp artifacts, whose preservation is not required for source reproduction. Prior source/report/test files remain unchanged.

Next software lead: stock preparation0x71c8 and clock-selection0x6384 with helpers0x623c/0x6294/0x6352; fixed-point conversion0x5d70. The stock preparation continues through configurable callback, mode transitions,0x7064 and widget measurement, so the offline base->auto-dither helper is not closure of that larger function. No external input blocks this next bounded software analysis. Factory analog response, actual trim and physical timing remain external boundaries.
