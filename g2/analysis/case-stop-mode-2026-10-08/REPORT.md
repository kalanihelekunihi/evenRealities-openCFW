# Charging-case STOP-mode correction

Locked image function `0x080050e8..0x0800511e` (54 bytes) implements **STOP entry**, despite its existing `HAL_PWR_EnterSLEEPMode` catalogue name. The shared catalogue is preserved; this evidence records the correction locally. Original instruction listing and wrapper/decoded/body hashes accompany the independent reconstruction `stop_mode.c` and interface `stop_mode.h`.

Pseudocode: clear PWR CR1 low3 bits; select LPMS0 for regulator zero, LPMS1 for any nonzero raw argument; set SCB SCR SLEEPDEEP bit2; if entry is exactly1 execute WFI, otherwise SEV/WFE/WFE; after return clear SLEEPDEEP. PWR base is0x40007000 and SCR0xe000ed10. Actual full-width entry0x101 follows WFE; this is raw callee behavior, not endorsement of an invalid public API argument.

Pinned public STM32G0 HALv1.4.7 candidate `a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9`, retained in ../dependency-followup-2026-10-08, has the same STOP0/STOP1 and deep-sleep sequencing. Its SLEEP routine clears SLEEPDEEP instead. This establishes a behavioral family comparison, **not exact producer version or compiled-byte attribution**.

The application at0x08007214 disables wake mask0x2b, enables its selected wake configuration, calls this body with `(0,1)` (STOP0/WFI), then calls `board_peripheral_init` at0x0800b600. That latter body calls mode configuration with0x200, system-clock configuration, and clock-path configuration; either failed configuration reaches fail-stop. This is a static restore call path, not proof that wake hardware fires or clocks restart successfully. The helper does not independently restore clocks or configure wake pins.

Fresh reproducible Clang21/Cortex-M0+ standalone build SHA `510e2b705a507b6a30fc1b1392a5344cc19e83c514850cf8061fa9ba7a917816` passes **216 original-instruction/source comparisons** across raw regulator/entry values, register initial values and PRIMASK0/1. Ordered MMIO writes, resulting CR1/SCR, SP and PRIMASK compare. Two mutants (wrong deep bit/wrong LPMS selection) are rejected. WFI/WFE are explicit controlled-wake cuts; SEV executes. No elapsed time, pin edge, current draw, exception delivery or actual clock restore is claimed.

This is a standalone offline reconstruction, not installed firmware or a full case power manager. Newly recovered facts help simulator/app work distinguish STOP from shallow sleep and avoid dropping the application's post-wake clock setup. Next independently actionable lead is mode-wait0x08005048 and its bounded clock-state polling; its existing decompilation does not prove timing units or physical ready-state changes.

All110 sealed audit inputs remain unchanged. No accepted checkpoint, shared campaign, catalogue, firmware or Git index was changed.
