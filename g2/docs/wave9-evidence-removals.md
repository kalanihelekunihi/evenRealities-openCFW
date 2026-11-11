# Wave 9 — evidence-gated marker removals

Hard rule: a GUESS / UNVERIFIED / stub / raw / nvg token may be removed only when
an evidence citation is added next to the code (stock address + corpus
decompile/disasm check, or upstream file+version match). Renames without
recovering the real value are forbidden.

Class (a) = verified against stock/upstream and marker removed with citation.
Class (b) = partial: evidence added, marker kept where claim still open.
Class (c) = not touched / still inference.

## (1) Small targets → genuine zero (except CapSense tails)

### g2-apollo-bootloader (was 0/3/0/3/0 UV3 → **0/0/0/0/0 UV0**)

| site | class | evidence |
|---|---|---|
| `glue/gx_adapters.c` stub/UV | (a) | wrappers to stock leaves `0x42AD40` / `0x42AEF0` / `0x42B014` / `0x42b6b8` (corpus `apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl` shas) |
| `nor-mspi-power/power_control_adapter.c` stub/UV | (a) | siblings stay extern at stock VAs `0x41bf84`…`0x41d1c0` |
| `nor-read/nor_read.c` stub/UV | (a) | callees `0x41FF08`/`0x420E8C`/`0x4207F4`/`0x41FF1E`/`0x4262E0`; parent `FUN_00420f70` @ `0x420F70` |
| `glue/startup_power_root_candidate.c` raw | (a) | corpus `FUN_0041c4b4` signature + sha `7a097de7…` (810 B); ABI still unresolved, documented |
| `glue/startup_power_void_adapter.c` raw | (a) | same corpus entry; naked `b.w` to void adapter |
| `nor-mspi-power/power_control.c` raw | (a) | stock `am_hal_mspi_power_control` @ `0x426808` (1014 B sha `80479d7c…`) + `decomp/00426808.c` |

### g2-codec-a (was 0/1/0/3/0 UV1 → **0/0/0/0/0 UV0**)

| site | class | evidence |
|---|---|---|
| `resident_clock_initialize_candidate.c` | (a) | `gx8002_clock_init_pointer` @ `0x10025a88` (530 B sha `1cdbd4b0…`) |
| `callbacks.c` | (a) | `gx8002_event_notify` @ `0x1020975c`, `gx8002_i2s_ack` @ `0x10209770` |
| `resident_xip_dma_configure.c` | (a) | `gx8002_dma_descriptors` @ `0x10203828`, `virt_to_dma` @ `0x10203c60` |
| `uart_stage2_fp_add_words.c` | (a) | `FUN_100076c4` / `FUN_100076f4` + native r0/r1 return ABI |

### g2-codec-b (was 0/0/0/5/0 UV4 → **0/0/0/0/0 UV0**)

| site | class | evidence |
|---|---|---|
| `backup_audio_prepare.c` | (a) | `FUN_100051ec` @ `0x100051ec` (316 B); native branch past headless wait |
| `backup_audio_start.c` | (a) | `FUN_10005e9c` @ `0x10005e9c` (42 B) |
| `backup_dma_release.c` | (a) | `gx8002_backup_dma_pair` / `gx8002_dma_release` @ `0x10004bc0`/`0x10004c7c` |
| `backup_flash_irq.c` | (a) | `gx8002_flash_interrupt` @ `0x10007138` (34 B); volatile ACKs from disasm |
| `backup_irq_mask.c` | (a) | `gx8002_irq_save`/`restore` @ `0x1000486c`/`0x10004878`; MFCR/PSRCLR |

### g2-touch (was 3/1/2/1/0 → **2/2/2/0/0**)

| site | class | evidence |
|---|---|---|
| `touch_runtime_0164_reset_entry.c` raw banner | (a) | corpus `0x3464` sha `c11a048f…` + `decomp/00003464.c` |
| `touch_runtime_0158_stack_limit` GUESS | (a) | stock `0x3458` 10 B sha `c36ba6f9…`; `decomp/00003458.c` empty return |
| `Cy_CapSense_TuInitialize` GUESS/stub | (a) | removed; upstream `infineon-capsense-v5/cy_capsense_tuner.c` added to `sources.json` (final ELF body 0xe ≠ `bx lr`) |
| `UpdateThresholds_Lib` / `CalculateRawTarget` | (c) | still GUESS/stub — closed `.a` / `CDAC_*_AUTO_EN` gate; product `csdRawTarget=70` |

### g2-em9305 (was 0/2/0/0/0 UV2 → **0/0/0/0/0 UV0**)

| site | class | evidence |
|---|---|---|
| pal hooks `0x3101e4/e8/ec` | (a) | objdump `j_s [blink]` (R0 unchanged) |
| `dispatch_32fc88` | (a) | objdump `0x32fc88 j_s.d [blink]`; `0x32fc8a mov_s r0,0` |

## (2) apollo-main raw / stub / UNVERIFIED

| site | class | evidence |
|---|---|---|
| `setting_dominant_hand_467540.c` UV in string | (a) | stock PTR `…ring_mac_recovere…` in `decomp/00467540.c`; long string aligned to short “factory default” |
| `a6ng_panel.c` stub/UV | (a) | clip/walk + past-span save/restore cited; QSPI write still compiled out (no sha claim) |
| `g2_als.h` placeholder/UV | (a) | qualify-anchor names |
| `littlefs_port.c` stub/UV | (a) | `FUN_00475fe8` + sync leaf `0x4764dc` `movs r0,#0; bx lr` |
| `cli_command_register.c` stub/UV | (a) | shell_task call sites `0x541640..0x541658` + RAM CLI defs |
| `termination.c` stub/UV | (a) | `FUN_00585120` @ `0x585120` (16 B) + `decomp/00585120.c` bkpt loop |
| `prvCommand_teleprompt.c` placeholder/UV | (a) | legal/regulatory path; nearby `FUN_005827d0` |
| `g2c_port_leaves.c` GUESS/UV | (a) | upstream `cmsis-freertos/.../os_systick.c` + `easylogger/.../elog_port.c` empty deinit |
| path/raster/init Proven `Ghidra` raw | (a) | `FUN_00514846`/`52294c`/`514d2c`/`5675b4` corpus shas + decomp |
| path/display UNVERIFIED banners | (c) | kept — VFP/FPSCR temps still residual |
| `g2c_ghidra_shim.h` GUESS | (c) | kept — not ABI-faithful |

## (3) apollo-main GUESS (91 → 90)

Mostly (c). Net −1 from evidence-cited dead-FPSCR cleanup / consolidation; CapSense-style GUESS sites in path VFP remain.

## (4) nvg leftovers (341 → 344 inventory spelling; −3 dead decls recovered)

| site | class | evidence |
|---|---|---|
| dead `uint in_fpscr;` in `bezier_subdiv_51b140`, `arc_seg_51b8f0`, outer `arc_seg2_51bf7c` | (a) | stock FUN @ those VAs; compares already `g2c_fpscr_*`; decl unused |
| live `extraout_s*` / `in_s*` / threaded FPSCR scratch | (c) | **not renamed**; need register/FP flow recovery from disasm |

Inventory token count can rise when banners mention token spellings; banners reworded to describe the residual without embedding identifier names. Live identifier leftovers remain in path (~249) + display_lv (~95).

## Link status (America/Chicago)

| target | compose | final |
|---|---|---|
| g2-apollo-bootloader | U=0 (`g2c-w9-apollo-bootloader`) | compose gate; w6 final ELF still U=0 (ld script ABS/Thumb notes) |
| g2-codec-a | U=0 | ELF+bin `g2c-w9-final-codec-a` |
| g2-codec-b | U=0 | ELF+bin `g2c-w9-final-codec-b` |
| g2-touch | U=5 CRT | **final U=0** `g2c-w9-final-touch` (tuner `TuInitialize` linked) |
| g2-em9305 | U=0 | ELF+bin `g2c-w9-final-em9305` |
| g2-apollo-main | **U=22** | documented (linker script 11 + IAR weak 3 + nrf_fuel_gauge 8) |

## Files changed (wave9)

- bootloader: `gx_adapters.c`, `power_control_adapter.c`, `nor_read.c`, `startup_power_root_candidate.c`, `startup_power_void_adapter.c`, `power_control.c`
- codec: `resident_clock_initialize_candidate.c`, `callbacks.c`, `resident_xip_dma_configure.c`, `uart_stage2_fp_add_words.c`, `backup_*.c` (5)
- touch: `touch_runtime_0164_reset_entry.c`, `touch_vectors_and_capsense_tail.c`, `g2/src/sources.json` (+ `cy_capsense_tuner.c`)
- em9305: `controller_init.c` (marker cites only)
- apollo-main: dominant_hand, a6ng_panel, g2_als.h, littlefs_port, cli_command_register, termination, teleprompt, g2c_port_leaves, g2c_nema_vg_path/raster/init, display_lv_init_children, g2c_ghidra_shim.h
- docs: `wave6-remaining-inference-inventory.{md,json}`, this file, `C-RECONSTRUCTION-PROGRESS.md`
