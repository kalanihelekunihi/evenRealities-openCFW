# Wave 21 markers

Same rules as earlier waves. Backups of every edited file are in `.waves/w21-bak/*.w21pre`.

## Done

1. **g2c_vectors.c: 10 IRQ handlers.** The GUESS is removed. Each slot was checked against the stock disasm (`/tmp/apm.bin`, base 0x438000) and `apollo-main/ghidra/open-2026-09-29/decomp/<addr>.c`.
   - Eight slots already had matching bodies in g2/src under unsuffixed names. They are now bound to those bodies directly: HardFault_Handler (CmBacktrace), SVC_Handler, PendSV_Handler and SysTick_Handler (FreeRTOS ARM_CM55 port), hal_i2c_irq_handler, uled_mspi_term, gx8002_i2s_isr and PDM0_IRQHandler.
   - Two bodies are new, transcribed from stock: `am_gpio0_607f_isr_4b80be` (IRQ59) and `am_irq82_isr_4d58a6` (calls am_hal_spotmgr_boost_timer_interrupt_service_48039a).
   - The linked vector table was read back, and all 10 slots point at those functions.
2. **am_hal_clkmgr_g2.c: clock-manager RAM map.** Every upstream `g_*ClkMgr*` / stabilizing / pending object is mapped to its stock RAM address from the literal pools of the stock clkmgr functions (0x4c3750..0x4c45e2). The hand copy in hal/clock already uses exactly those addresses.
   - **Bug found and fixed:** `am_hal_clkmgr_clock_release_all`, called by am_hal_mspi, was the upstream version. It walked upstream's own bitmap, which is never set, so it never released anything. It is now reimplemented from stock 0x4c45a4 and walks the stock bitmap.
   - GUESS narrowed (still 1): the private_clkgen_* helpers, clock_config and board_info_* keep upstream static state. Stock has no private_clkgen_* functions.
3. **g2c_ghidra_shim.h: removed.** Nothing in g2/src or the build tooling included it. It was moved to `.waves/w21-bak/`, and the compose still builds 2869/2869.
4. **em9305 gp-relative loads.** All 43 `[gp,..]` operands, including the 16 loads, are at 0x334122..0x334ca4, in rodata.
   - That region starts with the HCI vendor-command table at 0x3340bc, which code reads as data (0x30ec48 `mov_s r0,0x3340bc`). Objdump mis-decodes it as code.
   - No instruction writes gp.
   - The highest direct RAM refs below 0x80ff54 are one-word hook slots 0x80fdfc..0x80fe1c, each loaded with `ld [rX,0]` and no stride.
   - So this image's code never touches 0x80fe20..0x80fe28. The UNVERIFIED is narrowed to possible ROM use.
5. **Scanner.** `.waves/inventory.py` gets a new CORPUS rule: a "Ghidra" word is a citation when its own line or the next line names a concrete corpus file (`ghidra/open-YYYY-MM-DD` or `decomp/<8hex>.c`). It changes no count outside wave-21 lines.

## Genuinely unresolvable (updated)

| marker | where | why |
|---|---|---|
| GUESS | hal/clkmgr-g2c/am_hal_clkmgr_g2.c | The upstream private_clkgen_hf*adj_* helpers, called by upstream am_hal_clkgen.c, have no stock counterpart because stock clkmgr ends at board_info_set 0x4c45e2. Their state can't be matched to stock. Removing it would mean replacing upstream clkgen.c with a stock-derived one. |
| GUESS | ble/g2c-leaves (+0xc3) | Vendor field with no upstream counterpart. |
| stub | notify_app_icon.c | No stock strings or protocol docs name the tables. |
| weak x3 | iar_stdout.c | Intentional weak overrides. |
| inferred | cb_ring_battery.c | Object membership of the forwarder at 0x500378 can't be proven. |
| inferred | aging_test_page.c | Stringless LVGL callees. |
| inferred | g2_als.h | No DRV_ __func__ strings. |
| inferred | dmic/i2s_request_provider.c | The protocol is reconstructed from 0x57ce78/0x57d024 bodies. |
| GUESS+FLAG | codec-a .ld | csky DSP and the extra libgcc routines are not in image_a. |
| FLAG+UNVERIFIED | em9305 .ld | The stack top comes from r17 (caller/ROM). Possible ROM use of the rodata range pair {0x80fd74,0x80ff54} can't be checked because the ROM is not in the repo. Nothing in this image references that table. |
| inferred | em9305 controller_init.c | unchanged |
| raw / inferred | codec-b | unchanged |
| FLAG | touch | unchanged |
