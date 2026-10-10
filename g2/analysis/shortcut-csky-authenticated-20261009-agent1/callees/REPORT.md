# Ten direct startup callees and public-provider correlation

Status: partial P2 evidence ready for independent review. All ten assigned roots produced CFG-bounded Ghidra functions and complete raw instruction/P-code/decompiler exports. Their non-overlapping bodies total **982 instruction bytes**; together with the first four startup bodies the scoped total is 1,226 bytes. This is neither complete firmware coverage nor complete transitive behavioral closure.

`run.py` authenticates the locked whole bundle and codec again, verifies each canonical image against the exact payload slice, and uses the corrected private MOVIH+MFCR processor. `bodies.json` records every body span/hash in child, codec and conditional runtime coordinates. `receipts.json` records actual commands and output hashes. No canonical inventory, gate or source implementation changed.

| Entry | End exclusive | Bytes | Source-backed identity and new behavior |
| --- | --- | --- | --- |
| 0x10000a04 | 0x10000a28 | 36 | `spl_boot_info_init`: calls 0x10000e58, samples PMU 0xa0010068 low nibble, records NOR device=2 at 0x20001280 only when nibble=2; takes a second independent MMIO sample and stores sample & 0xffffff00 at 0x20001284. Non-NOR leaves boot-info unchanged. |
| 0x10000f14 | 0x10000f34 | 32 | `spl_board_init`: calls trim-state accessor 0x10000b40; only if result=0 rewrites 0xa0010094 as (old & 0xfffffff0) | 12. Public board source corroborates pad 8/function 12. |
| 0x1000092c | 0x100009c2 | 150 | `spl_clk_init`: zeroes two trim states via helpers; for module IDs 0..25 initializes div and DTO, applies ten 8-byte source-table entries from 0x200011e8, initializes 26 module-source selectors, calls board trim helper, then sets SRAM gate and oscillator/gate bits. Final 26 gate calls enable IDs selected by 0x20462 below ID 18 and disable the remainder. |
| 0x10000134 | 0x10000136 | 2 | `spl_clear_bss`: single `jmp lr`; no memory writes and no BSS clear. Public `spl_start.S` contains the same empty routine. |
| 0x10000f04 | 0x10000f12 | 14 | `serial_init`: overrides caller arguments, calls 0x10000e84 with r0=225<<9=115200, r1=0; restores LR and returns. Matches public no-UART-boot branch using CONFIG_SERIAL_BAUD_RATE=115200; incoming `(1,0)` is not passed through. |
| 0x10000a2c | 0x10000aa8 | 124 | `spl_nor_load_image`: two explicitly recovered routes described below; stores and calls the selected reset pointer, then returns 0 if target returns. |
| 0x10025a88 | 0x10025c9a | 530 | `clk_init`: ROM versus SRAM start paths, oscillator/PLL retry and source tables, constant module/div/DTO call sequence, SRAM resume gate restoration, final oscillator disable and LDO writes. Public board clock implementation matches this structure; provider names have byte-level matches. |
| 0x10024984 | 0x100249a2 | 30 | `gx_pmu_get_start_mode`: public archive supplies exact body except one named call relocation. For wake source 2..5 returns 0xa0010058 & 1 and additionally reads 0xa001005c; otherwise returns 0. The latter MMIO read disappears from raw C and must remain in reviewed semantics. |
| 0x10025cbc | 0x10025cd0 | 20 | `board_init`: queries wake source; for unsigned source >=2 calls 0x100245f0 (`xip_sflash_init` candidate); always calls XIP 0x10203c74 (`gx_analog_config_update_enable`, exact archive match). |
| 0x10026314 | 0x10026340 | 44 | `main`: public `lvp/main.c` matches six named lifecycle calls and the loop. `LvpInitMode(1)` matches public `LVP_MODE_TWS`=1; strong corroboration for CONFIG_LVP_INIT_WORKMODE_TWS. Loop ticks events while mode tick !=0, then runs system shutdown and returns 0. |

Names based only on source call order remain candidates. The archive-equal HAL labels below have stronger byte-level evidence. Body extents exclude adjacent literal pools and breakpoint/alignment words.

## NOR loader routing recovered at the body level

Use 32-bit wrapping arithmetic for all expressions and preserve helper call return/side effects separately. Let `base=read32(0x20001284)` and `mode=read32(0x20033ffc)`. Both routes call helper 0x10000c40 twice and do not check its return status.

If mode equals 0xaabbccdd, first request `(base+0x323b0, &stack_word, 4)`. Second request is `(stack_word+0x323b4, 0x20003000, 0x1408c)`. The second source expression deliberately does not add `base`; it exactly matches public `spl.c` second-firmware source-coordinate formula. Selected target is 0x10003100.

Otherwise first request `(base+0x3000, &stack_word, 4)`, then `(base+0x3000+stack_word+4, 0x10023400, 0x397c)`; selected target is 0x10023500. Length 0x397c equals the canonical stage2 SRAM length 14,716. In either route store the selected target to 0x2002e938, execute `jsr` to it, then return 0 if it returns. Actual flash-base samples, copy success and execution visibility remain external premises. The code contains both concrete targets; the indirect target set in this body is finite and resolved under the intended coordinate model.

## Source and archive shortcuts independently tested

Public `libdriver_release_v1.0.6.a` contains relocatable objects rather than HAL implementation C. `archive_probe.py` extracted pmu_ctrl.o and misc.o into this successor directory and preserved native disassembly/relocations. It proved:

- `gx_pmu_get_start_mode` section: 30 bytes identical to 0x10024984 apart from the four-byte BSR relocation at [2,6); that named relocation identifies 0x10024940 as `gx_pmu_get_wakeup_source`.
- `gx_pmu_get_wakeup_source`: all 66 section bytes exactly equal stock SRAM [0x10024940,0x10024982). Reads 0xa0000034; priority is bit0->GPIO=2, then bit2->AUDIO=3, bit3->I2C=5, bit1->RTC=4; when none are set returns read32(0xa001002c)&1 (COLD=0/WDT=1). This resolves the immediate dependency of the start-mode and board wrappers.
- `gx_analog_config_update_enable`: all 20 section bytes equal canonical BINH-A XIP at child offset 0xc70, runtime 0x10203c74 under the reviewed XIP base 0x10203004. Its 14-byte instruction body writes 0x59 to 0xa0005040, 5044, 5048 and 504c in that order and returns; the remaining six bytes are alignment and its literal pool.

`provider_match.py` proved exact bytes outside explicitly named four-byte relocations for eight more direct clock/LDO providers. These are **section matches**, including literal data, not pseudocode coverage counts:

| Stock address | Archive section name | Section bytes |
| --- | --- | --- |
| 0x10024bcc | gx_clock_set_source | 20 |
| 0x10024be0 | gx_clock_set_module_source | 400 |
| 0x10024df8 | gx_clock_set_div | 330 |
| 0x10024f44 | gx_clock_set_dto | 200 |
| 0x10025060 | gx_clock_set_pll | 32 |
| 0x10025080 | gx_clock_set_module_enable | 256 |
| 0x100246f0 | gx_analog_set_ldo_ana_voltage | 32 |
| 0x10024730 | gx_analog_set_ldo_dig_voltage | 44 |

The eight sections total 1,314 bytes. `provider-matches.json` contains every excluded relocation and both byte hashes. This is concrete dependency provenance and a useful type/name shortcut; a prebuilt provider cannot supply code in the final source-only reconstruction. No archive executable is admitted as a build input.

## Remaining source-backed frontier

The ten wrappers have no failed decoder or unknown body edge in this private export. Their transitive helpers are not thereby complete. In particular, the 44-byte main wrapper calls six shipped BINH-A XIP bodies: 0x102078a4 (`LvpSystemInit`), 0x102085a4 (`LvpInitMode`), 0x10208cd4 (`LvpInitializeAppEvent`), 0x102085f8 (`LvpModeTick`), 0x10208d48 (`LvpAppEventTick`), 0x10207a7c (`LvpSystemDone`). Public sources for these exist; this branch is a new bounded P2 frontier, not blocked private input.

HAL source C is absent from the public SDK inspected, but matching archive object sections preserve instruction/relocation facts. More P2 recovery can use that evidence. Public board variants share substantial initialization code, so these matches do not uniquely identify the Even board. Final PLL/clock/LDO hardware effects, source table contents, flash reader helper, interrupt/exception effects and firmware-specific mode extensions require deeper analysis or hardware/private documentation. No global public-source exhaustion claim is made.

Tool notes: the pinned old GNU objdump does not support `--disassemble=<symbol>`; the failed diagnostic is preserved as `gx_pmu_get_start_mode.txt`. Section-selective `-dr -j .text.<name>` succeeded. All ten private Ghidra decompiles succeeded; raw C remains deficient for unused MMIO reads, volatile ordering and function ABI guesses. The manually stated instruction facts retain those effects. No cybersecurity classifier block occurred.
