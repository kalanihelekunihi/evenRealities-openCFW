# Independent offline mode and CapSense initialization

Recovered ARM32 interfaces are in mode.h. [Mode evidence](../../../analysis/touch-mode-closure-2026-10-08/REPORT.md), [full initialization](../../../analysis/touch-cap-initialization-closure-2026-10-08/REPORT.md), [regular composition](../../../analysis/touch-regular-mode-composition-2026-10-08/REPORT.md), and [saturated composition](../../../analysis/touch-scan-mode-composition-2026-10-08/REPORT.md).

The core exposes open dependencies explicitly. Regular binding uses independent GPIO and unmodified pinned public PDL; it excludes request 7 until all-slot/auto-dither generation is closed. Saturation binding handles its selected request path without function stubs. Peripherals and delay calibration are synthetic; no hardware or timing validation is implied.
