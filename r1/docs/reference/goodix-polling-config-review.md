# Goodix stock polling configuration

The R1 Goodix demo now selects `__POLLING_INT_PROCESS_MODE__` (1) instead of the vendor default normal-interrupt mode (0). The existing native kernel configuration overlay carries this setting alongside the previously checked software-reset policy. No vendor file or source-plan selection changes.

Two independent observations support the polling setting. The locked compressed RW initialization produces value 1 at `0x20007af1`, the mode byte referenced by `Gh3x2xDemoInit`. A Python decoder and execution of the stock decompressor at `0x286f4` agree on the complete 6,492-byte initialized region. Also, stock interrupt processing at `0x2db8c` reaches `GH3X2X_GetIrqStatus` without the upstream normal-interrupt callback gate.

A bounded execution comparison covers 240 stock/C pairs across five runtime mode bytes, three nonzero initialized flags, two non-engineering work modes, four interrupt masks and two callback flags. Every corrected C path reaches IRQ-status sampling first, matching stock. The previous C configuration diverges in 48 cases, checking `GH3X2X_GetSoftEvent` first. C never executes stock instructions. Stock logging is disabled; the C log sink is modeled as returning zero. The comparison stops at the first hardware query and does not prove the full ISR, physical timing, concurrency or every initialization path.

All 575 units compile; application/bootloader unresolved sets remain exactly 173/34. All 573 other objects are byte unchanged. In the two affected generated units:

- The only configuration macro difference is interrupt-processing mode. The default mode data byte changes from zero to one, matching stock initialization; the compile-time external-interrupt callback flag disappears. Other shared exported data contents are unchanged.
- Kernel instruction/semantic differences are confined to `Gh3x2xDemoInit`, `Gh3x2xDemoInterruptProcess` and `Gh3x2xIntPinTriggerModePro`. Fifteen additional relocation-label differences resolve to identical local strings; their instructions are unchanged. The trigger helper is not independently mapped to a native entry and receives no stock coverage credit.
- The demo-user external-interrupt callback function disappears. Its 21 retained functions are unchanged. The unconditional `hal_gh3x2x_int_init` template and its unresolved `gh3026_int_pin_init` dependency remain; this review does not invent a board binding for them.

Five official qualification candidates compile and select no regions. The corrected kernel is still outside the exact source plan. The canonical hybrid equals the locked application, with 3,905 source-built bytes, 642,255 fallback bytes and 248 resource bytes. Full C source completeness remains false and G2 gates remain unchanged.

Current normal report: `build/sources-goal-r1-goodix-polling/report.json`. [Machine-readable evidence](goodix-polling-config-review.json) binds sources, initialized-RAM verification, native/C prefix probes, negative comparison, object/macro audits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-goodix-polling/`.
