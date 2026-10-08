# Source and validation rescan

Compared with `g2/analysis/rescan-2026-10-07T024938Z`. Read-only inspection; only this scan directory was created. No builds, emulation, generation, staging or campaign edits.

Bootloader C/header/assembly: **242 → 295**. Foundation: **89 → 89**. Changes: **53 added, 3 modified, 0 removed**.

Git visibility: {'tracked': 384}; ignored inspected source files: **0**.

Added or modified component source:

- `g2/components/bootloader/clock_manager/clock_class_provider6.c` (modified)
- `g2/components/bootloader/clock_manager/clock_class_provider6.h` (modified)
- `g2/components/bootloader/initializer_callbacks/adc_configuration.c` (added)
- `g2/components/bootloader/initializer_callbacks/adc_configuration.h` (added)
- `g2/components/bootloader/initializer_callbacks/adc_profile.c` (added)
- `g2/components/bootloader/initializer_callbacks/adc_profile.h` (added)
- `g2/components/bootloader/initializer_callbacks/adc_samples.c` (added)
- `g2/components/bootloader/initializer_callbacks/adc_samples.h` (added)
- `g2/components/bootloader/initializer_callbacks/clock_generators.c` (added)
- `g2/components/bootloader/initializer_callbacks/clock_generators.h` (added)
- `g2/components/bootloader/initializer_callbacks/clock_pll_math.c` (added)
- `g2/components/bootloader/initializer_callbacks/clock_pll_mod.c` (added)
- `g2/components/bootloader/initializer_callbacks/clock_pll_rounding.c` (added)
- `g2/components/bootloader/initializer_callbacks/elog_output.c` (added)
- `g2/components/bootloader/initializer_callbacks/elog_setters.c` (added)
- `g2/components/bootloader/initializer_callbacks/elog_setters.h` (added)
- `g2/components/bootloader/initializer_callbacks/elog_uart_tx.c` (added)
- `g2/components/bootloader/initializer_callbacks/plain_printf.c` (added)
- `g2/components/bootloader/initializer_callbacks/platform_bringup.c` (modified)
- `g2/components/bootloader/initializer_callbacks/service_records.c` (added)
- `g2/components/bootloader/initializer_callbacks/service_records.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_alternatives.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_clock_config.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_clockmux.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_clockmux.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_clockmux_dependencies.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_clockmux_entry.S` (added)
- `g2/components/bootloader/initializer_callbacks/startup_config_leaves.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_initialize_leaves.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_initialize_leaves.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_memory_config.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_memory_config.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_power_config.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_power_config.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_power_register_read.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_runtime.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_runtime.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_shutdown.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_shutdown.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_spot_events.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_spot_events.h` (added)
- `g2/components/bootloader/initializer_callbacks/startup_spot_handlers.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_spot_timer.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_ton_gate.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_ton_hooks.c` (added)
- `g2/components/bootloader/initializer_callbacks/startup_ton_hooks.h` (added)
- `g2/components/bootloader/initializer_callbacks/uart_context.c` (added)
- `g2/components/bootloader/initializer_callbacks/uart_context.h` (added)
- `g2/components/bootloader/initializer_callbacks/uart_rx.c` (added)
- `g2/components/bootloader/initializer_callbacks/uart_rx.h` (added)
- `g2/components/bootloader/platform_control/power_special_mode.c` (added)
- `g2/components/bootloader/platform_control/power_special_mode.h` (added)
- `g2/components/bootloader/thread_creation/isr_delivery.c` (added)
- `g2/components/bootloader/thread_creation/isr_delivery.h` (added)
- `g2/components/bootloader/thread_creation/mutex_kernel.c` (added)
- `g2/components/bootloader/thread_creation/mutex_kernel.h` (added)

Current shared offline test ELF SHA256: **129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9**. This agrees with the 129a exact-image validation receipt.

- `129a6b2f38f1`: PASS, 7 integration cases; 41 referenced receipt files rehashed, 0 mismatches. Role: Promoted bounded source-linked offline test checkpoint; root startup remains unresolved.
- `370bdfaad92f`: PASS, 7 integration cases; 50 referenced receipt files rehashed, 0 mismatches. Role: Validated bounded offline native startup candidate; unpromoted shared checkpoint remains129a.
- `4b1fb7505187`: FROZEN_PENDING_FINAL_VALIDATION; actual frozen ELF hash matches: True; 201 linked objects / 230 input copies. Final validation summary present: False.

Newer startup work includes native PCM2.2 sequence handlers and source-defined initialization/relocation of the 1371-byte locked DATA record under `inventory-worker/startup-initialize/`. These analysis-local C artifacts are separate from component-source counts above. The 370b checkpoint is validated but unpromoted; the 4b1 successor is frozen pending final validation. Presence of a candidate does not establish completed integration.

The shared image still retains the original-address startup contract and explicit startup/logger integration models. Offline instruction comparisons do not prove peripheral timing, whole-source completeness, a working hardware image or byte-identical rebuilding. Build outputs are intentionally ignored; inspected C/header/assembly is visible to Git. Exact per-file differences and receipt identities are in `snapshot.json`.
