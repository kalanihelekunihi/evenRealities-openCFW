# Offline power-management callback ABI

Independent ARM32 list registration, phase dispatcher and DeepSleep wrapper. [Report and386 three-way cases](../../../analysis/touch-pm-callbacks-closure-2026-10-08/REPORT.md). Caller retains ownership of linked descriptors/params/context; supported valid types/modes and coherent lists only. Installed clock tests stop before WFI. Fixed observed SRAM ABI; no production patch or physical wake model.
