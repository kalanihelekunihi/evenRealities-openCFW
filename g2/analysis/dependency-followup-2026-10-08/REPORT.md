# Concrete dependency follow-up

This resumes dependency work after the 03:14 UTC scan. New isolated artifacts only; no accepted checkpoint, shared campaign, production provider, gitlink or index changed. No commits or physical device writes. This report is a bounded milestone, **not a claim that every actionable source lead is exhausted**.

## Newly resolved touch source barrier

Official PDL `35f1714623cfea682d5e285af80d50416b4c7bbc`, core-lib `ca57d1e519e08badec6891d1776c7b4f05e09561` and CMSIS `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` supply a preserved minimal source/include closure under `touch-source/`, with source hashes and retained licenses. The declaration-only `system_cat2.h` is a build fixture, not recovered startup. Source and license acquisition are fresh, not inherited from the earlier empty-worktree reports.

The official Arm GNU 13.3.Rel1 macOS ARM64 archive was downloaded to `/tmp/opencfw-arm-gnu-13.3.tar.xz`, SHA256 `fb6921db95d345dc7e5e487dd43b745e3a5b4d5c0c7ca4f707347148760317b4`. It was extracted only to `/tmp/opencfw-arm-gnu`; no system install or PATH edit occurred. This is an observed download hash, not a verified signature. Compiler reports GCC13.3.1, build arm-13.24.

At `-Og`, six pinned public functions reproduce the **entire contiguous stock range [0x9218,0x9316), 254 bytes**, including resolved internal calls:

| Function | Address | Bytes | Prior compiled attribution |
| --- | --- | ---: | --- |
| Cy_SCB_ReadArrayNoCheck | 0x9218 | 56 | Already recorded in matching experiments |
| Cy_SCB_ReadArray | 0x9250 | 30 | Newly reproduced here |
| Cy_SCB_WriteArrayNoCheck | 0x926e | 56 | Newly reproduced here |
| Cy_SCB_WriteArray | 0x92a6 | 48 | Newly reproduced here |
| Cy_SCB_WriteDefaultArrayNoCheck | 0x92d6 | 16 | Newly reproduced here |
| Cy_SCB_WriteDefaultArray | 0x92e6 | 48 | Newly reproduced here |

Increment: **198 newly compiled-source-attributed bytes**, not 254 newly discovered code bytes. These routines already had decompilation/semantic evidence. This does not select a unique producer release among GCC10.3–13.3 or prove the full touch image rebuilds. Clang21 `-Oz` compiled successfully but did not match the first two extents; do not use that as exact-build evidence.

`verify_touch_default.py` freshly executes stock and actual public-source-compiled default-fill bodies/callee, with **136 cases** and no child-call stubs. Count is FIFO elements. The unchecked helper repeats the full uint32 input as 32-bit writes; it does not software-truncate to byte/halfword. Hardware may apply its configured width. The checked helper reads CTRL, reads TX occupancy masked511, computes unsigned capacity-minus-occupancy, clamps requested count and returns the written element count. Both 16/8-element configurations are tested. Impossible occupancy, concurrent consumers, actual transmission and hardware interrupt timing are outside these tests; no safe saturation is inferred from unsigned subtraction.

The two adjacent I2C functions remain unmatched: public `Cy_SCB_I2C_Init`/`SlaveInterrupt` at GCC13.3 `-Og` are 492/300 bytes versus stock438/276. `touch-i2c-screen.json` records twelve optimization/assertion combinations, none matching both stock extents. This is an extent screen, not exhaustive version/configuration proof or evidence the public source is absent. The subsequent bounded layout comparison below advanced the API despite this byte mismatch; changing the FIFO-matched public pin globally would remain unjustified.

### I2C init: recovered small-enum layout and executable compatibility

The public small-enum ABI gives **24-byte config / 84-byte context**, matching tested stock accesses. Config mode is1 byte at0; RX/TX FIFO flags1/2; address3/mask4; address acceptance5; general ACK6; HS7; wake8; digital filter9; low/high phase counts12/16; address delay20. Context state4, master status8, slave status32, event/address/HS callbacks68/72/76 and address delay80. `touch_i2c_layout.c` measures the pinned public types; `touch-i2c-layout.json` records values and `touch_i2c_abi.h` supplies a readable independent explicit adapter layout.

**39 new original/public-source init comparisons** pass using actual instructions, no child stubs. All three modes, selected flag combinations, phase counts1/8/16 and null arguments match complete96-byte guarded context, full peripheral register state, ordered MMIO writes, return and SP. Config read ordering is recorded but not required equal. No bus traffic, slave IRQ behavior, assertion trap cases, concurrent callback/state ownership or physical disabled-state verification. Public body492 bytes differs from stock438; this is bounded API compatibility, not exact compiled attribution.

Two controls reject forced four-byte enums (`-fno-short-enums`, assertion trap) and swapped RX/TX configuration (state mismatch). A first negative fixture merely omitted `-fshort-enums`; that failed to change ABI because this Arm GNU defaults to small enums (readelf Tag_ABI_enum_size). The fixture was corrected and all39 positive cases rerun; `i2c-negative-fixture-repair.json` preserves the distinction. **Small-enum compatibility does not prove an explicit producer flag.**

### Slave interrupt dispatch

**480 new stock/public-source top-level IRQ comparisons** cover all276 stock body instruction bytes. The five helpers are explicit void/no-state-change entry cuts, so this is dispatch and argument ordering evidence only. Helpers are HS9344, receive9748, stop93c4, address95b8 and transmit97fc. The first fixture reversed HS/RX labels; the existing catalogue was already correct. `i2c-irq-fixture-repair.json` preserves that fixture correction; firmware/public code was unchanged.

Recovered order: wake handling first; bus/arbitration error bookkeeping and RX interrupt masking; optional pending-RX kick on STOP; high-speed handling; receive processing unless the FIFO contains the just-matched address; STOP helper and status reload; address helper; transmit helper. Error bits0x101 set slave status0x100 (bus error bit0x100) or0x80 (arbitration), suppress RX interrupts and force the local STOP path. STOP bit0x10 clears then reloads masked slave status before address processing. Address bits0xc0 are handled after completion. RX level1 is skipped when CTRL address-accept0x10000 and address-match0x40 are both set, leaving the address for the address helper. TX masked bits0x41 invoke transmit then clear level1.

This gives CFW instrumentation a defensible order for event counters and host-visible touch I2C symptoms: a bus error can follow the completion path without a separate observed STOP; an address byte must not be consumed as ordinary payload; post-STOP address processing reads updated status. **Helper callbacks, buffer progress/lifetime and asynchronous ownership are not established by these cuts.** The synthetic W1C/masked-register model is explicit; no real interrupt firing/latency is inferred. Unexecuted delay/division/critical link aliases are guarded so reaching one fails rather than pretending to implement it. Source/public top-level300 bytes still differ from stock276.



### Actual slave helpers: stronger follow-up

`--with-real-irq` additionally links the official CM0+ critical-section assembly source from the same PDL pin. **512 stock/public-source cases now execute the actual five helpers and critical bodies, with no helper cuts, numeric executable aliases or original code in the source guest.** They observe1232 distinct original instruction bytes total (including all276 dispatch bytes); this is a per-suite observation count, not a new global coverage delta or new exact source attribution.

The fixture explicitly consumes three RX FIFO values and advances TX occupancy per write. Both initial PRIMASK0/1 are covered. Complete84-byte context,64-byte guarded RX/TX buffers, ordered helper-entry arguments and MMIO writes, final MMIO digest, SP and PRIMASK compare. Two mutants changing RX progress and omitting TX pointer advance are rejected. The final reproducible source build was freshly re-executed after these checks.

Concrete tested progress: with7 RX elements remaining, one FIFO read stores0x0c, advances RX pointer from20003000 to20003001, remaining count7→6 and index0→1. With7 TX elements and a TX event, bytes0..6 are written, TX pointer advances20004000→20004007, remaining count7→0 and index0→7. STOP with a pending byte consumes it before marking completion. Address acceptance with a simultaneous address-match skips ordinary payload processing and enters the address helper. These are the specific coherent synthetic states in the receipt, not a universal transaction/lifetime guarantee.

Public buffer configuration APIs retain caller-provided pointers; this batch does not introduce ownership/freeing. App/CFW callers must keep storage valid and coordinate buffer reconfiguration with the I2C interrupt. **Callbacks remain null in this stronger suite.** Callback reentrancy/state mutation, actual application event handlers, IRQ concurrency and physical clock/board wiring remain outside it. Initial generic-Thumb execution rejected a M-profile critical instruction; the correct `UC_MODE_MCLASS` profile resolved that fixture issue. A broad cy_syslib.c compile required missing delay declarations; critical implementations were correctly obtained from the existing official assembly instead of inventing delay globals. `i2c-real-fixture-notes.json` records these boundaries.

## Charging-case wake interface

Fresh official STM32 HAL power C/header/LICENSE acquisition at candidate pin `a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9` provides a behavioral comparator. `case_wake.c/.h` are independent locked-image reconstructions of enable `0x080050a8` (24 bytes) and disable `0x08005094` (14 bytes), **not copied vendor bodies**. Original case wrapper SHA36ca0c… and decoded image SHA773b6d… are authenticated by the verifier.

Enable does `CR4=(CR4 & ~(arg & 0x3f)) | (arg >> 8)` before `CR3 |= arg & 0x3f`; disable does `CR3 &= ~(arg & 0x3f)`, at PWR base0x40007000. The public header documents shift8 and high/low wake pin constants. Callers must use valid device/board constants and serialize register ownership. Invalid raw arguments can set additional polarity bits; this raw behavior is not an endorsed public API input.

**104 original/independent-source instruction comparisons** freshly match ordered read/write widths/values, final registers, SP and seeded callee-saved registers. Two semantic mutants (drop pin6, wrong polarity shift) are rejected. Actual MMIO is synthetic RAM; pin edges, standby/reset entry, interrupts and power consumption are not tested. No raw void return/flags equivalence or stock HAL-version/byte-identical compiler claim. Source ELF is only an offline module, not installed in production firmware.

## GX I2S relocation lead

The existing pinned `gx_i2s_set_five_wire_mode` object section is830 bytes with11 relocation entries. `codec_mask_probe.py` newly screens the whole authenticated codec payload after discarding each relocation word, then conservatively expanding each masked region by4 and8 surrounding bytes. **Zero hits** remain, including the most permissive610-unmasked-byte pattern. Synthetic positive, relocation-mutated positive and unmasked-byte negative controls pass. This excludes the unchanged unmasked section pattern only: linker relaxation, instruction selection/order changes or another implementation remain possible. No exact relocation-resolved attribution, recovered implementation or new firmware bytes are claimed. No vendor object bytes exported.

## ROM and build configuration boundary

Fresh official download of the already acquired Ambiq helper C at exact pin `5efc0228528a8adce5eae0d226fac85d2551eb3b` matches SHA `b10862af2cb41270165cff0f0d85d75fb4b0729e393813024ea561b25c5c4978`. Existing MRAM-PROVENANCE already correctly documented the five-argument nv_program_main2 entry0x0200ff21 and cleanup writes40014008=C3,40014024=0,40014008=0. This is reauthentication, not new recovered behavior. SDK delay entry0200ff51 is **not** proof that resident stock entry40 has the same implementation. Authentic resident ROM source/bytes are absent; no ROM body can be reconstructed from a helper-table declaration. ROM is outside OTA and does not itself prevent accounting for OTA call instructions.

The installed IAR10.10.2 runtime differs from the unconfirmed stock9.60.2 candidate; actual producing version, library configuration, linker file/order and initializer packing remain unresolved. New GCC availability removes the touch compiler absence; it does not solve Apollo IAR or charging-case armclang production reproduction. The consolidated case toolchains document contains an older GCC paragraph contradicted by its current table and `tools/matching/experiments.md` (Arm Compiler6/armlink); this report uses the newer recorded experiment and does not silently inherit the stale paragraph.

## Source-by-source remaining assessment

| Lead | Evidence and actual boundary | Further action status |
| --- | --- | --- |
| Infineon PDL/core/CMSIS | Six FIFO source bodies now exact; I2C extents differ; board/IRQ ownership absent | I2C init layout now validated in39 cases; dispatch480 child-cut cases plus512 actual-helper/null-callback cases now pass; **actionable** application callback/concurrent ownership comparison remains; no source/compiler acquisition blocker now |
| STM32 HAL/CMSIS-G0 | Two wake bodies reconstructed/tested; public1.4.7 is comparator only | **Actionable** selected case peripheral/HAL configuration comparison; producing armclang/config needed for exact full build |
| Ambiq HAL5.1.0 | Existing accepted242 and prior HAL closure; helper source freshly authenticated | Public register/API evidence remains reusable; private revision, board/cache/IRQ state and ROM bodies limit exact/physical claims |
| FreeRTOS/CMSIS RTOS | Public10.5.1 source and native delay/list tests already available | Scheduler/TCB/config and dynamic ownership still require bounded stock comparison; hardware scheduling claims need traces. Source inference is not globally exhausted |
| Cordio | Pinned public comparator, recovered ATT copy boundary; downstream layouts/timers differ | Port/layout/config comparison remains possible; controller firmware and actual asynchronous scheduling are distinct boundaries |
| EM9305 | Recorded v4.2 mirrored matches versus licensed local4.6; selected4.6 bodies differ | Matching authoritative4.2 source/ABI and MetaWare build are missing. SDK agreement restricts distribution; no confidential source/header layouts exported. Existing mismatch does not prove all public HCI knowledge exhausted |
| NationalChip I2S/DSP | New overmasked screen has no hit; implementation source absent for selected object | Exact unchanged-section lead exhausted by this screen; changed implementations/revisions remain unproven. NPU commands/weights are not MCU source; execution semantics/vendor implementation remain gaps |
| LVGL/Ambiq backend | Recovered snapshots/pins already validated; core is hybrid development lineage | Allocator/cache/panel lifecycle and exact fork remain; source consumer tracing can still advance |
| Nema | Public headers separate from proprietary IAR implementation | Exact implementation source/archive/config absent; public GCC archive is not stock-byte equivalent |
| littlefs/FlashDB/FreeType | Public source baselines available; bounded storage adapters already recovered | Remaining whole-image adapter/ownership/config comparison is possible; external NOR font contents unavailable |
| liblc3/resources | Recovered reference snapshot and earlier validation available | App/audio producer/consumer integration can still be traced; unresolved asset consumer is not blocked merely by missing NOR fonts |
| Product-specific glue | Locked instructions/corpus available | Further offline decompilation remains possible; public dependencies do not substitute for firmware-specific logic |

This assessment does **not** justify the global stopping condition “no remaining actionable knowledge inferable from dependency sources.” It distinguishes selected exhausted/missing-source leads from still-actionable integration and revision comparisons. The practical next dependency batch is touch application callback and concurrent buffer-ownership handling (init/context/actual SDK helpers now advanced), then a selected case HAL peripheral path. Broad repeated inventory scans are unnecessary.

## Reproduce and navigate

Use the OpenCFW venv Python (system Python lacks pyelftools). `build_touch.py --gcc <Arm GNU13.3 bin/arm-none-eabi-gcc> --output <scratch>` builds from the preserved source closure and asserts all254 original bytes. Add `--with-i2c` to build the public small-enum init comparator, then run `verify_touch_i2c_init.py <scratch>/i2c-init-short.elf`. Add `--with-irq` to build the child-cut dispatcher ELF and run `verify_touch_i2c_irq.py <scratch>/i2c-irq.elf`. Add `--with-real-irq` and run `verify_touch_i2c_real.py <scratch>/i2c-irq-real.elf` to execute actual helpers/critical assembly. `verify_real_negative.py --gcc <tool>` checks two progress mutants. The earlier I2C negative test currently points to the temporary GCC13.3 path; reacquire or update that explicit tool path if needed. `touch-reproduction-receipt.json`, `touch-gcc-match.json`, `touch-default-results.json` and `source-provenance.json` preserve source, input and ELF identities. The compiler/archive currently live in temporary paths and can be reacquired; no permanent toolchain install was made.

For case, compile `case_wake.c` with Clang ARM Cortex-M0+ `-Oz -ffreestanding -fno-builtin`, link `-Ttext=0x100000 -e case_wake_enable`, then invoke `verify_case_wake.py <elf>` and `verify_case_negative.py`. `codec_mask_probe.py` reproduces the independent relocation screen.

Official sources: [Infineon PDL pin](https://github.com/Infineon/mtb-pdl-cat2/tree/35f1714623cfea682d5e285af80d50416b4c7bbc), [core-lib pin](https://github.com/Infineon/core-lib/tree/ca57d1e519e08badec6891d1776c7b4f05e09561), [STM32 HAL pin](https://github.com/STMicroelectronics/stm32g0xx-hal-driver/tree/a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9), [Ambiq helper pin](https://raw.githubusercontent.com/AmbiqMicro/ambiqhal_ambiq/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal/mcu/am_hal_bootrom_helper.c), [Arm GNU13.3 release documentation](https://support.arm.com/documentation/109845/13-3-Rel1/).
