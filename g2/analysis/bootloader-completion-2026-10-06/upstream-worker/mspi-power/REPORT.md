# MSPI power-control source closure

## Result

Added `g2/components/bootloader/nor_mspi_power/power_control.c` and `.h` as a readable, target-specific reconstruction of locked routine `0x426808`. The implementation uses the locked bootloader state layout and control-flow, while making each hardware or sibling-subsystem call an explicit function in `opencfw_mspi_power_ops_t`. `power_control_adapter.c/.h` adds the stock three-argument `opencfw_bl_power_control(handle, operation, retain_state)` ABI so existing call sites can use the source provider directly. Its adapter binds `clock_request` to the recovered native dispatcher and uses volatile MMIO operations for register access and interrupt disable.

The provider preserves: handle tag mask/value `0x01ffffff`/`0x01bebebe`; byte truncation of operation, retain, and user-ID values; full-width module indexing; operation 0's retain-valid and clock-class-7 errors; operations 1 and 2 power-down behavior; busy-field checks; register save/restore order and index mapping; CQCFG's bit-0 enable handling and CQFLAGS set-clear restore; interrupt mask `0x1fff`; XIP bit-0 delay gate; callback order; and propagated clock request/release errors. The save-valid byte is at byte offset `0x860`, which is word slot `0x218` in the handle.

## Source provenance and comparison

The local source candidate is `upstream-worker/ambiqhal-apollo510/ambiqhal/mcu/apollo510/hal/mcu/am_hal_mspi.c`, from the exact gitlink commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, release marker `release_sdk5p1p0-366b80e084`, source SHA-256 `5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`. Its per-file record identifies Ambiq Micro copyright and an in-file BSD-3-Clause notice. The root gitlink remains uninitialized and unchanged; the source acquisition already recorded under `upstream-worker/ambiqhal-apollo510/` supplies the source used here.

That SDK's `am_hal_mspi_power_control()` at line 4440 is related but has a different public handle/API layout. It independently confirms the power sequence and saved register family, including the retained CQ state, MSPI interrupt disable, XIP off delay, and clock/peripheral gating. It is not claimed as a byte-identical body. The reconstruction follows the locked decompilation `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/decomp/00426808.c` for target-specific offsets, magic, byte fields, and return behavior.

## Synthetic verification

`test_power_control.c` runs the source against synthetic register storage and callback recorders; it does not access hardware. It covers invalid handles, unsupported operations, both busy guards, power-down save and XIP delay, callback mask/order inputs, clock-request failure, retain-state rejection, retained restore including CQCFG/CQFLAGS mapping, CQ enable/disable, and clock-release failure. The host test passes all 23 assertions:

```sh
cc -std=c11 -Wall -Wextra -Werror -O0 -g \
  g2/components/bootloader/nor_mspi_power/power_control.c \
  g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-power/test_power_control.c \
  -o /tmp/mspi_power_test
/tmp/mspi_power_test
```

The provider compiles as a freestanding Cortex-M55 ARM EABI5 object with Clang (`-std=c11 -Wall -Wextra -Werror -ffreestanding -fno-builtin`). Output SHA-256: `f6182019894dc655821838ef6e958cef35c8758d7af8264ea31c0e0dfd0824bb`.

`verify_power_control.py` executes the locked image's original `0x426808` instructions and the separately compiled source plus native three-argument adapter ELF under Unicorn with matching synthetic external callback stubs. All 19 cases pass, comparing return values, the complete 0x8d0-byte handle, callback event order/arguments, and the 0x300-byte MSPI register window. Covered paths include null/bad handles, invalid and truncated operations, both busy tests, save-valid and class-7 gates, clock request/release failures, ordinary wake and retained restore (with and without CQ enable), power-down save (with and without active CQ), XIP delay, and high module/user values. The run executes 1,008 distinct original instruction bytes. Its source ELF SHA-256 and per-source hashes are recorded in `out/power-control-differential.json`.

## Integration dependencies and limits

The adapter binds `mode_enter` to `0x41bf84`, `mode_leave` to `0x41c17a`, clock request to native `clock_request`, release-all to `0x4223d8`, CQ disable/enable to `0x423fad`/`0x423f8e`, clock-generator control to the local source provider for `0x4249a0`, and delay to `0x41d1c0`. Mode enter/leave, release-all, CQ disable/enable and delay remain external integration dependencies. Clock request and release resolve to the recovered native clock-manager dispatchers. Interrupt disable and indexed MSPI register reads/writes use volatile operations at `0x40060000 + module * 0x1000 + offset`. No timer frequency or physical timing behavior is inferred here.

`arm-none-eabi-nm -u power_control_adapter.o` lists the adapter's separate-object dependencies: `clock_request`, `opencfw_bl_clock_release_all`, `opencfw_bl_mspi_clockgen_control`, `opencfw_bl_mspi_cq_enable`, `opencfw_bl_mspi_mode_enter`, `opencfw_bl_mspi_mode_leave`, `opencfw_hal_delay_us`, `opencfw_hal_mspi_cq_disable`, and the local `opencfw_hal_mspi_power_control`. The new `mspi_clockgen_control.c` in this directory resolves the clock-generator symbol; mode enter/leave, release-all and CQ functions remain named sibling dependencies, as does the external delay service. In the isolated power differential, private boundaries are bound to synthetic interception addresses instead of no-op production implementations.

The power-control comparison intercepts its sibling providers at stock call addresses and supplies matching deterministic callback behavior to the source adapter. It compares their order and inputs; this isolated 19-case profile does not compare clock-generator internals. Separately, the device-configuration profile below executes and validates a source-owned clock-generator helper. The Cortex-M4-ISA source ELF used by Unicorn is a test build, not the target's IAR/Cortex-M55 final build. No firmware source integration, shared build-system edit, hardware access, or full executable equivalence was performed.

## Device configuration and clock-generator helper

Added `g2/components/bootloader/nor_mspi_power/device_configure.c/.h` for stock entry `0x424be4`, the two private helpers `0x424120` and `0x424a18`, and `mspi_clockgen_control.c` for called helper `0x4249a0`. The implementation consumes the stock 24-byte record and the recovered private handle offsets. It does not pass the 24-byte caller buffer to the public SDK's incompatible 52-byte `am_hal_mspi_dev_config_t`.

The clock-generator provider uses the locked helper's register literal `0x40004110`, byte-truncates its four register arguments, performs the recovered PRIMASK save/disable/restore sequence, applies the per-module five-bit register fields, and invokes `opencfw_hal_delay_us(10)` only on the enabled path. `clock_request` and `clock_release` resolve to the recovered native clock-manager dispatchers. The remaining external dependency for this tested device-config path is delay service `0x41d1c0`; that source/provider must be supplied by the integration target.

The public HAL source at the exact Apollo510 HAL5.1.0 gitlink (`5efc0228528a8adce5eae0d226fac85d2551eb3b`, file SHA-256 `5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`) is a register/protocol cross-check only. The stock/source implementation follows the locked bootloader evidence; no public HAL body is claimed as an exact translation of the private firmware routine.

`make -C g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-power test` compiles both providers for ARM and compares stock against source under Unicorn. The current run passes 2,823 cases: all 256 frequency bytes across modules 0–3 in SDR/DDR, every device-mode byte, plus invalid-handle/configuration and clock-transition error paths. It compares return values, the full 0x8d0-byte handle, the 0x300-byte MSPI register window, global clock-generator register, and delay/clock callback events. The stock run executes the original main routine and helpers `0x424120`, `0x4249a0`, `0x424a18`, and `critical_save 0x41b8ec`; the run covers 3,142 distinct original instruction bytes, not 3,142 instructions. MMIO and delay are synthetic; this establishes semantic equivalence for the listed cases, not physical timing, full-image linkage, or byte identity. Full per-case output is `out/device-configure-differential.json`.
