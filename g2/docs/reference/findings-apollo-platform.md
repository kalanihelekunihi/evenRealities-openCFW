# G2 Apollo platform findings (main + bootloader)

Distilled on 2026-10-21 from the Apollo platform experiment directories under `g2/analysis/` (Ambiq HAL, MSPI/IOM/GPIO, FreeRTOS/WSF, Cordio, logging, FlashDB/FAL, TLSF, IAR runtime/startup, bootloader completion), which were removed during consolidation.
Only durable facts are kept: roles, stock addresses, layouts, register behaviour, lineage evidence, stock quirks and open blockers. Process narrative, test counts and intermediate hashes were dropped.
Recover any cited original with `git show pre-consolidation:<path>` (for example `git show pre-consolidation:g2/analysis/ambiq-gpio-config-2026-10-05/REPORT.md`).
Read this alongside [libraries.md](libraries.md), [toolchains.md](toolchains.md) and [memory-map.md](memory-map.md). This file adds detail and does not repeat what they say.

## 0. Conventions and identities

- **Main addresses.** Main addresses are runtime VAs in the Apollo main image, which loads at `0x00438000`. To get the OTA file offset, compute `VA − 0x438000 + 0x20`; this skips the 32-byte OTA header. `pre-consolidation:g2/analysis/iom-fdnb-stock-lineage-20261009-implementation/REPORT.md`
- **Bootloader addresses.** "BL" addresses refer to the Even bootloader raw image, which loads at `0x00410000`. That image is 148,599 B with SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/upstream-worker/REPORT.md`
- **Image identities.** These are cited throughout the experiments:

| Object | Size | SHA-256 |
|---|---:|---|
| Main OTA payload (with 32-B header) | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Main stripped image (base `0x438000`) | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Locked bundle | 4,301,227 | `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa` |
| Whole-payload analysis ELF (`.text` maps all main bytes at `0x437fe0`) | — | `36c9b79de3b961d36ad343a1402a112298603111cbe1d5875e1b471694159d1a` |

  Sources: `pre-consolidation:g2/analysis/kernel-tick-candidate-20261010/REPORT.md`, `pre-consolidation:g2/analysis/firmware-byte-map-2026-10-05/README.md`, `pre-consolidation:g2/analysis/rea-wide-mapping-exhaustion-20261010-daybreak-low/REPORT.md`.
- **Main vector and extent.** The main vector holds SP `0x2007FB00` and reset `0x005E4233`. The raw main image spans `0x00438000–0x00794324`; the wrapper header is at `0x00437FE0`. `pre-consolidation:g2/analysis/internal-sdk-discovery-2026-10-09/EMULATOR-HARDWARE-CONTRACTS.md`
- **Upstream reference pins.** These pins recur below:
  - Ambiq HAL public replay `5efc0228528a8adce5eae0d226fac85d2551eb3b`, file revision `release_sdk5p1p0-366b80e084`.
  - Cordio public r20.05c `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`.
  - FreeRTOS V10.5.1 `def7d2df2b0506d3d249334974f51e427c17a41c`.
  - FlashDB 2.1.1 `714d6159e7e6afb267a3953756abca445c350e61`.
  - The user-supplied AmbiqSuite 5.2.0 zip: SHA-256 `d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`, 907,382,158 B, 30,485 members, `release_sdk5p2p0_66487dd10`, dated 2026-07-24.

  Sources: `pre-consolidation:g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/REPORT.md`.

---

## 1. IAR startup, scatter loading and runtime

### 1.1 Main scatter table `0x0075D3C8..0x0075D410`

The table has five destination contracts, and all of them use **absolute** addresses. Neither handler's r9/static-base-relative (RWPI) flag is set. A byte-identical rebuild must reproduce these rows, their order and their handler choice. `pre-consolidation:g2/analysis/iar-scatter-destination-discriminator-20261010-daybreak/REPORT.md`

| Row | Handler | Input (packed len / bytes) | Destination | Output |
|---|---|---|---|---|
| zero-init | `__iar_zero_init3` `0x005FA01E` | len `0x70AF0` | `0x20004558` | zero fill |
| zero-init | same | len `0x240FD4` | `0x2013BE70` | zero fill |
| `0x75D3E0` | decompressor `0x0043A11F` (Thumb) | `0x2C` → 22 B at `0x79430E` | `0x00000040` (ITCM) | 24 B |
| `0x75D3F0` | same | `0x54E0` → 10,864 B at `0x79189E` | `0x20000000` | 17,752 B (`0x4558`) |
| `0x75D400` | same | `0x434E` → 8,615 B at `0x78F6F7` | `0x20080000` | — |

- The three compressed inputs form one gapless tail at the end of the image, in reverse row order: `[0x78F6F7,0x79189E)`, `[0x79189E,0x79430E)`, `[0x79430E,0x794324)`. The last range ends at the image end. `pre-consolidation:g2/analysis/iar-scatter-destination-discriminator-20261010-daybreak/REPORT.md`
- **Flag bits.** In a zero-init descriptor, bit 0 of the destination word selects `r9 + word − 1`. In a decompressor row, bit 0 of the packed length selects static-base-relative addressing. `pre-consolidation:g2/analysis/iar-scatter-destination-discriminator-20261010-daybreak/REPORT.md`
- **`__iar_zero_init3` quirk.** It subtracts 4 and writes one word before it tests the loop condition. Lengths 1–3 therefore underflow, so valid lengths are 0 or ≥ 4. `pre-consolidation:g2/analysis/iar-runtime-c-candidates-20261010-sol/REPORT.md`
- **The ITCM `0x40` delay loop is not ROM.** Decoding the 22-byte packed stream (pre-decrement literal loop, 13 literals plus a 3-byte back-reference, then 3 literals plus a 5-byte back-reference) yields 24 bytes. The first six are `01 38 fd d1 70 47` (`subs r0,#1; bne 0x40; bx lr`). This was decoded statically. Unicorn could not execute the decoder loop. It supersedes the "resident ROM 0x40" claim in the radio IOM power reports. `pre-consolidation:g2/analysis/ambiq-critical-2026-10-05/REPORT.md`
- **SRAM init stream verified.** The `0x20000000` stream (record `0x75D3F4`) was decoded independently in Python and by executing the original decoder `0x43A11E`. The two results agree. `pre-consolidation:g2/analysis/bq27427-descriptor-binding-2026-10-09/REPORT.md`

### 1.2 IAR runtime leaves and toolchain evidence

- **Assert ABI.** IAR 10.10.2 `arm/inc/c/assert.h` calls `__aeabi_assert(expression,file,line)` when `__ICCARM__` is defined. The stock three-argument assert provider (TLSF uses `0x4D09B4`) is therefore consistent with the ordinary IAR header and needs no custom override. The GNU `__assert_func` path takes four arguments. `pre-consolidation:g2/analysis/application-iar-input-search-20261010-implementation/REPORT.md`
- **Stock assert route.** The stock assertion goes through the logger and a `BKPT 0xAB` route. This differs from the print-and-abort template in the IAR vendor `assert.c`. `pre-consolidation:g2/analysis/tlsf-main-runtime-boundary-20261010-implementation/REPORT.md`
- **Local IAR 10.10.2 runtime objects.** The archives are `rt7M_tl.a` and `dl7M_tln.a`.
  - `assert.o` `.comment` reads "IAR 10.10.2.628/LNX, Cortex-M3, normal DLIB, -Oh, -ropi". These are runtime-object facts, not application flags.
  - `ABImemcpy.o` provides `memcpy`/`memcpy4`/`memcpy8`.
  - GNU ld cannot link IAR objects: it rejects `R_ARM_THM_JUMP6` as truncated.
  - 10.10.2 cannot confirm the 9.60.2 candidate.

  `pre-consolidation:g2/analysis/tlsf-main-runtime-boundary-20261010-implementation/REPORT.md`
- **IAR 10.10.2 container.** The base archive (SHA `b4fe2e43…`, Build Tools 10.10.2.27058) was installed in a container. Compiling fails with `LMSC2143` (license/bearer token required). No object was produced. `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/TOOLING-INSTALL-RESULT.md`
- **Ten reconstructed IAR runtime leaves.** Ten small IAR runtime bodies (388 B total) were rebuilt in C: strcat, isxdigit, scanner unget, an output context, zero-init and others. The recovered contract:
  - Scanner state is context +0, consumed +12, width +16.
  - The output context is +8, with count at +44.
  - `_UngetN` decrements `consumed` even at EOF.
  - No compiled body matched stock bytes.

  `pre-consolidation:g2/analysis/iar-runtime-c-candidates-20261010-sol/REPORT.md`
- **Copy routines.**
  - The `memcpy` span is `0x439BE4..0x439C8A`: 166 B, made of 104 instruction bytes and 62 gap bytes.
  - The aligned interior entry is `0x439C04`, used as the copy provider.
  - `memmove` is at `0x439710..0x4397A6`.

  `pre-consolidation:g2/analysis/tlsf-main-source-comparison-20261010-implementation/REPORT.md`, `pre-consolidation:g2/analysis/apollo-lz4-source-discriminator-20261009T211300Z/pseudocode.md`
- **No application project inputs.** No authenticated application IAR project or ICF (`s200.ewp`, `s200.icf`, `s200_ap510b_iar_git`) exists locally or in SDK 5.2. Neither does an assert override. `pre-consolidation:g2/analysis/application-iar-input-search-20261010-implementation/REPORT.md`
- **SDK 5.2 GNU recipe and linker script.**
  - Executable MRAM starts at `0x00410000`. ITCM has VMA 0 with an MRAM LMA. Data starts at `0x20000000`.
  - Stack and heap markers are at `0x2007D000`/`0x2007C000`. The NOLOAD shared region is at `0x20080000`.
  - The recipe sets `FABI=hard`. Objects built with the soft VFP-args ABI refuse to link.
  - IAR section names are `.intvec/.textrw/SHARED_RW/RESOURCE_TABLE`. GNU uses `.isr_vector/.itcm_text/.shared/.resource_table`.
  - The stock IAR scatter loader is at `0x005E42B4`.

  `pre-consolidation:g2/analysis/sdk-runtime-link-20261010-implementation/REPORT.md`

### 1.3 Interrupt-masking disciplines (do not interchange)

| Provider | Stock | Behaviour | Src |
|---|---|---|---|
| Ambiq `am_hal_interrupt_master_disable` | `0x473940` (8 B `eff3108072b67047`: `MRS r0,PRIMASK; CPSID i; BX LR`) | Saves and restores PRIMASK. The public GCC body compiles to the identical 8 bytes. | `pre-consolidation:g2/analysis/ambiq-critical-2026-10-05/REPORT.md` |
| FreeRTOS `ulSetInterruptMask` / clear | `0x5FA0A4` (22 B) / `0x5FA0BA` (14 B) | Saves BASEPRI, writes `0x30`, then DSB/ISB. Restores the saved value. This is **not** a diagnostic routine; older reports said it was. | `pre-consolidation:g2/analysis/timer-queue-wsf-2026-10-05/REPORT.md` |
| FreeRTOS task critical enter / exit | `0x4420D0` (24 B) / `0x4420E8` (44 B), literal `0x442210` | Sets BASEPRI `0x30` and uses a u32 nesting count at `0x2000309C`. The outermost exit **clears** BASEPRI to 0 and does not restore it. | `pre-consolidation:g2/analysis/timer-daemon-wsf-2026-10-05/REPORT.md` |
| WSF `WsfCsEnter` / `WsfCsExit` | `0x52B8A4` / `0x52B8B6` (18 B each) | u8 nesting at `0x20075045`. CPSID runs only at depth 0; CPSIE runs when depth returns to 0. Does **not** restore the prior PRIMASK. | `pre-consolidation:g2/analysis/wsf-radio-handoff-2026-10-05/REPORT.md` |

---

## 2. Ambiq HAL (AmbiqSuite 5.1.0 lineage) in main

### 2.1 GPIO

GPIO base is `0x40010000`. `PINCFG[224]` is at `+4·pin`, and `PADKEY` is at `+0x400` (key `0x73`). Each register family below is seven words:

| Family | RD | WT | WTS | WTC | EN | ENS | ENC |
|---|---|---|---|---|---|---|---|
| Offset | `0x404` | `0x420` | `0x43C` | `0x458` | `0x474` | `0x490` | `0x4AC` |

Source: `pre-consolidation:g2/analysis/ambiq-gpio-board-2026-10-05/pseudocode.md`. An earlier model placed EN/WTS/WTC after WT; that was wrong.

| Function | Stock | Contract | Src |
|---|---|---|---|
| `am_hal_gpio_pinconfig_get` | `0x480EEE` (30 B) | Pin ≥ 224 returns 5. A NULL output returns 6. The pin check takes precedence. | `pre-consolidation:g2/analysis/ambiq-gpio-config-2026-10-05/REPORT.md` |
| `am_hal_gpio_pinconfig` | `0x480F0C` (126 B) | Two 7-word bitmaps mark extended-drive pads and normal pads that support extra drive. The table has holes: pin 106 is **not** in the extended table. Normal pads: drive bits 10–11 values 2/3 need the capability; bit 12 is slew. Extended pads accept pull 0/1/6 only. Writes run save PRIMASK → `CPSID` → `PADKEY=0x73` → `PINCFG=raw` → `PADKEY=0` (cleared, not restored) → restore. Rejects return 5 or 7 with no MMIO. | same |
| `am_hal_gpio_state_write` | `0x480FD6` (218 B) | The operation is truncated to a byte (UXTB). Ops 0..5 are clear, set, toggle, output-disable, output-enable, enable-toggle. Unknown ops return 0 with no MMIO. There is **no pin range check**: bank = `(pin>>5)&7`, so bank 7 aliases the next register family and pin 256 wraps to 0. Only the toggles take PRIMASK. Always returns 0. | `pre-consolidation:g2/analysis/ambiq-gpio-board-2026-10-05/REPORT.md` |
| `am_hal_gpio_interrupt_control` | `0x4810B0` | NULL or op > 3 returns 6. Pin > 223 returns 5. Op 0/1 changes one bit; op 2/3 applies a 7-bank mask, a 28-byte input reread for each channel. The channel is **not validated**: an invalid channel hits ch0 for single-bit ops and both channels for mask ops. Updates EN with PRIMASK held. Pin-index helper is 22 B. | `pre-consolidation:g2/analysis/radio-gpio-control-2026-10-05/REPORT.md` |
| `am_hal_gpio_interrupt_irq_status_get` | `0x481574` (126 B) | Reads raw status, or status AND EN, under PRIMASK. | `pre-consolidation:g2/analysis/ambiq-gpio-irq-2026-10-05/REPORT.md` |
| `am_hal_gpio_interrupt_irq_clear` | `0x4815F2` (58 B) | One write to CLR with no wait. An invalid IRQ returns 6. | same |
| `am_hal_gpio_interrupt_register` | `0x48162C` (154 B) | Channel 0, 1 or both. Publishes the callback **then** the argument, with no lock and no pin check. | same |
| `am_hal_gpio_interrupt_service` | `0x4816C6` (116 B) | Dispatches set bits in ascending order and reads table slots live, so a callback can change a later slot. A missing callback returns 7 and processing continues. Six bytes after the guard are unreachable. | same |

- **GPIO IRQ map.**
  - IRQs 56..62 and 125..131 select seven banks per channel.
  - EN/STAT/CLR start at `0x40010530/534/538`, with bank stride `0x10` and channel stride `0x70`. IRQ59 maps to `0x40010560/564/568`.
  - The callback and argument tables are 14×32 words at `0x20068228` and `0x20068928`.

  `pre-consolidation:g2/analysis/ambiq-gpio-irq-2026-10-05/REPORT.md`
- **`GPIO0_607F_IRQHandler` `0x4B80BE`.**
  - It takes a seven-word all-bank snapshot that it never uses (helper `0x4812F6`).
  - It then gets the **raw** IRQ59 status, clears it, and runs service. Return codes are ignored.
  - A pending bit therefore dispatches even when EN is 0.

  `pre-consolidation:g2/analysis/radio-gpio-consumer-2026-10-05/REPORT.md`
- **Board consumers.**
  - **Display power helper `0x592C78`** (named `jbd4010_configure_gpio_pins`, inferred). It configures pin 143 if revision < 3, pin 128 if revision < 4, and pin 142 always, each with raw config `0x183` (from `0x78EE40`). `pre-consolidation:g2/analysis/ambiq-gpio-config-2026-10-05/REPORT.md`
  - **Flash setup `0x46FB0C`.** It saves pin 103's config with the getter (call at `0x46FD10`) before MSPI operations. `pre-consolidation:g2/analysis/ambiq-gpio-config-2026-10-05/REPORT.md`

### 2.2 MSPI

- **Bases and handle.**
  - MSPI0/1/2 are at `0x40060000/0x40061000/0x40062000` (stride `0x1000`).
  - Handle magic is `0xBEBEBE`; bit 24 means initialized and bit 25 enabled. An invalid handle returns 2 before any MMIO.

  `pre-consolidation:g2/analysis/ambiq-mspi-cycle-2026-10-05/upstream/REPORT.md`
- **Interrupt helpers.**
  - Enable and disable read-modify-write `INTEN` (+0x200) with no lock.
  - Status reads `INTSTAT` (+0x204), optionally ANDed with INTEN.
  - Clear writes `INTCLR` (+0x208) and then **must** read INTSTAT back.
  - The NOR and display ISRs use raw status: clear, then service.
  - The async NOR write path clears and enables mask `0x1A80` (DERR/CQUPD/CQERR/SCRERR).

  `pre-consolidation:g2/analysis/ambiq-mspi-cycle-2026-10-05/REPORT.md`
- **Interrupt-clear copies.**
  - The main copy is at `[0x4C23DE,0x4C240E)`.
  - In the bootloader:
    - interrupt enable/disable/status_get: `[0x426450,0x42647C)`, `[0x426484,0x4264B0)`, `[0x4264BA,0x4264F6)`
    - clear: `[0x426506,0x426536)`
  - The original decompiler missed the bootloader clear's read-back.

  `pre-consolidation:g2/analysis/ambiq-mspi-cycle-2026-10-05/upstream/REPORT.md`, `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/SDK-SETUP-AND-SOURCE-PROGRESS.md`
- **Stock sparse MSPI state.** Fields are TCB address slot +0x18, CQ count +0x20, HP count +0x840 and XIP delay +0x8CC. This layout differs from the public SDK. The global module state array is at `0x200523D8` with stride `0x8D0`; the CQ slot is at +0x828. `pre-consolidation:g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/ambiq-cmdq-disable-2026-10-05/REPORT.md`
- **`am_hal_mspi_disable` (118 B).**
  - Invalid handle returns 2; already disabled returns 0.
  - Nonzero CQ or HP counts return 3.
  - If the TCB slot is set, it calls CQ-disable (error propagated), then CQ-term, then clears enable.
  - DEV0XIP bit 0 selects the delay call.

  `pre-consolidation:g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md`
- **`am_hal_mspi_deinitialize` (56 B).** It ignores disable errors, clears init and the module index, and returns 0 even when busy (the enable bit and pending counts stay). Success is **not** a drain guarantee. `pre-consolidation:g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md`
- **Consumers.**
  - NOR and display reconfigure `0x470D7C` and `0x59C876` gate on disable.
  - JBD4010 power-off `0x593200` calls disable at `0x59326A`.
  - Init-error cleanup `0x46FB0C` calls deinitialize at `0x46FC20`, `0x46FC96` and `0x46FCF6`.

  `pre-consolidation:g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md`
- **CMDQ.**
  - `am_hal_cmdq_disable` `0x538E8C` (66 B): validates; is a no-op if already disabled; otherwise clears CQEN and the enable bit. It does not wait or free.
  - `am_hal_cmdq_term` `0x53909A` (98 B): refreshes indices. When not forced, it rejects cur ≠ end. It then clears init, CQEN and the pause mask. Force skips only the busy check. It does not drain or free.
  - `update_indices` `0x538D18` (64 B): uses the hardware index low byte plus an epoch, subtracts 256 on wrap, refreshes the head, and restores PRIMASK.
  - MSPI wrappers: `mspi_cq_disable` `0x4BFD62` (12 B, caller-local slot +0x828); `mspi_cq_term` `0x4BFC86` (58 B, global module slot, forced term, status ignored, slot cleared, returns 0).

  `pre-consolidation:g2/analysis/ambiq-cmdq-disable-2026-10-05/REPORT.md`

### 2.3 IOM (stock behaviour predates SDK 5.2)

- **Base and island.** Register base is `0x40050000 + module·0x1000` (module 0..7, from handle +4). The handle is valid when `(prefix & 0x01FFFFFF) == 0x01123456`; bit 24 means initialized and bit 25 enabled. The code island is `[0x55BCE8,0x55D280)`. `pre-consolidation:g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/REPORT.md`

| Function | Stock | Notes | Src |
|---|---|---|---|
| `validate_transaction` | `0x55C1E0` (166 B) | `(h, txn, bBlocking)`. Only when not blocking does it check pause byte txn+36 (`&0xE0`) and status word txn+40 (`&0x00E0E0E0`). Both known callers pass blocking = 1. | `pre-consolidation:g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/REPORT.md` |
| Ordinary blocking transfer | `0x55CC1C..0x55CF2E` (786 B) | Saves and disables INTEN, polls the FIFO, then restores INTEN at `0x55CE2C`. Earlier work mislabelled it nonblocking. | same |
| Blocking SPI full-duplex | `0x55CF40..0x55D246` (774 B) | Direction == 2. FULLDUP is set in MSPICFG (+0x280), CMD is at +0x120, FIFO polling. Restores INTEN and clears FULLDUP. | `pre-consolidation:g2/analysis/iom-fdnb-stock-lineage-20261009-implementation/REPORT.md` |
| Interrupt service | `0x55C558..0x55C7E0` (648 B) | Tests byte handle+`0x83C` (`bHP`) first. There is **no** FDNB-active dispatch (SDK 5.2 and public `ef488e3b` add one). Interrupt accumulator is at handle+24. | same |
| Configure (I2C) | `0x55CA94..0x55CC10` (380 B) | Writes MI2CCFG at +0x2C0. Unsupported rate returns 6, unsupported mode 5, module ≥ 8 rejected. | `pre-consolidation:g2/analysis/iom-strdis-stock-binding-20261009-implementation/REPORT.md` |

- **I2C rate table.** Stock keeps STRDIS (bit 24) = 0, the old behaviour. SDK 5.2 defaults it to 1.

| Rate | MI2CCFG | CLKCFG |
|---|---|---|
| 100 kHz | `0x3F070` | `0x773B2301` |
| 400 kHz | `0x3F270` | `0x1D0E2301` |
| 1 MHz (≈860 kHz) | `0x23040` | `0x0B052301` |

  `pre-consolidation:g2/analysis/iom-strdis-stock-binding-20261009-implementation/REPORT.md`
- **Transaction struct (stock, old/public layout, 48 B).** Fields are byte count +16, direction byte +20, TX pointer +24, RX pointer +28, continue byte +32, pause +36 and status +40. SDK 5.2 inserts `eFdnbMode` before pause; with 4-byte enums that moves pause/status to +40/+44, so stock is not that layout. `pre-consolidation:g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/REPORT.md`
- **App transaction producer `0x52DF50..0x52E058`.** It runs a 2-byte full-duplex transfer (TX at sp+4, RX at sp) on the radio transport's HAL handle, which `0x55CF40` consumes. `pre-consolidation:g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/REPORT.md`
- **IOM source lineage.**
  - `5efc0228` has no FDNB.
  - Public `ef488e3b1fb1d612d61862595edd203ee9f6ca37` (dated 2026-05-12) has a TX-DMA/RX-IRQ FDNB C implementation, but its header is unchanged (SHA `86135b68…`).
  - SDK 5.2.0 adds selectable direction and `eFdnbMode`.

  `pre-consolidation:g2/analysis/spi-fdnb-sdk-provenance-2026-10-09-source-track/REPORT.md`
- **SDK 5.2 FDNB contract (reference only; not in stock).**
  - `eFdnbMode = 0` is RX DMA/TX IRQ.
  - A start returning SUCCESS means scheduled, not complete.
  - Finish clears state and restores INTEN/DMATRIGEN before calling the callback.

  `pre-consolidation:g2/analysis/spi-fdnb-sdk-provenance-2026-10-09-source-track/REPORT.md`

### 2.4 Power domains, polling and delay

- **Domain lookup `0x47EF18`.** NULL output or domain ≥ 34 returns 6. Otherwise it copies a 16-byte record `{enable_reg, enable_mask, status_reg, status_mask}` from table `0x6BECB0..0x6BEED0` (literal `0x47F944`) with memcpy `0x439C04`. `pre-consolidation:g2/analysis/power-domain-descriptor-2026-10-06/pseudocode.md`
- **IOM domain mapping.** IOM modules 0..7 map to domains 3..10. Enable masks are bits 1..8 of `0x40021004`. Status at `0x40021008` is **shared by group**: IOM0–3 use mask `0x1E` and IOM4–7 use `0x1E0`. The poll waits until the masked value ≠ the whole mask. `pre-consolidation:g2/analysis/power-domain-descriptor-2026-10-06/REPORT.md`
- **Physical provider `0x47F7AE`.**
  - It calls the lookup and pre-wrapper `0x48032C`.
  - With PRIMASK held, it clears the enable mask.
  - It consults `0x47F6F2`, polls, then calls post-wrapper `0x480342`.
  - Domain 29 has its own path.
  - A second provider is `0x4C4530(4, domain)`.

  `pre-consolidation:g2/analysis/radio-iom-power-prepare-2026-10-05/external-boundary.md`
- **Poll helper `0x480826`.** A nonzero 5th argument (byte) waits for equality; zero waits for inequality. Budget N allows at most N `delay(1)` calls. The general path uses budget 5. `pre-consolidation:g2/analysis/radio-iom-power-prepare-2026-10-05/external-boundary.md`
- **Power callbacks.**
  - The table at `0x20073270` (0x3C B) is zeroed by startup `0x480434`.
  - Selection reads CHIPID `0x4002000C` and revision word `0x200001E8`.
  - One branch (`0x48064A..0x480650`) installs pre `0x5A07E6` and post `0x5A07F0`. The post callback may call `0x5A001C`.

  `pre-consolidation:g2/analysis/radio-iom-power-prepare-2026-10-05/external-boundary.md`
- **Delay `0x4807A0..0x4807F0` (80 B).**
  - Literals: 250.0f, 96.0f, and the perf register `0x40021000`. Bits [4:3] == 2 selects HP.
  - It converts u32 to f32, uses 5 fractional fixed-point bits, does HP multiply/divide, truncates, and adjusts by 15 (LP) or 24 (HP).
  - If count > adjustment it branches to the ITCM `0x40` loop; otherwise it returns.
  - It **differs from SDK 5.2** (integer `83us+(us+1)/3`, adjustment 25). Examples: HP, 1 µs gives 59 in stock vs 58 in SDK. LP, 16,777,217 µs gives 536,870,897 vs 536,870,929.

  `pre-consolidation:g2/analysis/delay-sdk52-independent-receipt-review-20261009-implementation/REPORT.md`

### 2.5 RTC (`am_hal_rtc_time_set`; functionally identical in `5efc0228` and SDK 5.2)

- **Bodies.** The setter is at `[0x4D3ADC,0x4D3B9A)` (190 B; the same hash was seen relocated at `0x4E4918` in another release). The validator is at `[0x4D3A58,0x4D3ACC)` and dec→BCD at `[0x4D3A38,0x4D3A58)`. Registers: control `0x40004800` (WRTC bit 0), CTRLOW `0x40004820`, CTRUP `0x40004824`. `pre-consolidation:g2/analysis/rtc-setter-boundaries-20261009-implementation/REPORT.md`
- **Input.** Ten u32 words:

| Offset | Field | Notes |
|---|---|---|
| +0 | read-error | ignored |
| +4 | weekday | validated 0..6 |
| +8 | century | low bit only, CTRUP bit 28, not validated |
| +12 | year | |
| +16 | month | |
| +20 | day | |
| +24 | hour | |
| +28 | minute | |
| +32 | second | |
| +36 | hundredths | |

  `pre-consolidation:g2/analysis/rtc-setter-boundaries-20261009-implementation/OWNER-CONTRACT.md`
- **Packing.**
  - CTRLOW: hour `<<24 &0x3F`, minute `<<16 &0x7F`, second `<<8 &0x7F`, hundredths `&0xFF`.
  - CTRUP: weekday `<<24 &7`, year `<<16 &0xFF`, month `<<8 &0x1F`, day `&0x3F`.

  same
- **Quirks.**
  - Year 100 is accepted and BCD-encodes to `0xA0`.
  - There is no Gregorian check, so 31 February passes.
  - Write order is ctrl `|=1`, CTRLOW, CTRUP, ctrl `&=~1`. Invalid input returns 1 with no MMIO.

  same

### 2.6 Cache maintenance (CMSIS SCB style; MIT reconstruction, not attributed)

- **Bodies.** Invalidate / clean+invalidate is at `0x475014..0x47510E` (250 B). Clean is at `0x47510E..0x475194` (134 B). The range argument is `{u32 addr; s32 len}`. `pre-consolidation:g2/analysis/cache-maintenance-2026-10-06/pseudocode.md`
- **Behaviour.**
  - If CCR (`0xE000ED14`) bit 16 is clear: DSB, ISB, return 0.
  - A NULL range means whole cache: CSSELR `0xE000ED84`=0, then CCSIDR `0xE000ED80`, set mask `0x3FE0`, way `<<30`.
  - A range uses 32-byte steps. The unaligned raw address is written and `len += addr&31`.
  - A non-positive length still loads both words, then returns.

  same
- **Operation registers.**

| Operation | Whole | Range |
|---|---|---|
| Invalidate (flag low byte 0) | `0xE000EF60` | `0xE000EF5C` |
| Clean+invalidate (flag low byte ≠ 0) | `0xE000EF74` | `0xE000EF70` |
| Clean | `0xE000EF6C` | `0xE000EF68` |

  same
- **Consumers.**
  - **Display write `0x59CCDC`.** It reads buffer +0x14 and length +0x0C and calls clean at `0x59CD10`. It builds the transfer with `0x59CAFC`, then calls blocking MSPI `0x4C2098` at `0x59CD26`.
  - **Audio inactive DMA buffer `0x57A7E0`.** It starts from template `0x78D474` `{0,3200}`, queries the buffer with `0x590B6C`, then invalidates (flag 0) at `0x57A800`.

  same

---

## 3. FreeRTOS kernel (V10.5.1 + CMSIS-RTOS2) in main

### 3.1 Globals

| Address | Object |
|---|---|
| `0x20074A20` | `pxCurrentTCB` |
| `0x20074A24` / `0x20074A28` | `pxDelayedTaskList` / `pxOverflowDelayedTaskList` |
| `0x20074A30` | `uxCurrentNumberOfTasks` |
| `0x20074A34` | `xTickCount` (literal `0x4557AC`) |
| `0x20074A38` | `uxTopReadyPriority` |
| `0x20074A3C` | `xSchedulerRunning` |
| `0x20074A40` | `xPendedTicks` |
| `0x20074A44` | `xYieldPending` |
| `0x20074A48` | `xNumOfOverflows` |
| `0x20074A50` | `xNextTaskUnblockTime` |
| `0x20074A58` | `uxSchedulerSuspended` |
| `0x20073D24` | `xPendingReadyList` |
| `0x2006A49C` | `pxReadyTasksLists[]` |
| `0x20074AB0` | timer command queue handle (literal `0x47EB6C`) |

Sources: `pre-consolidation:g2/analysis/rtos-tick-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/rtos-resume-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/kernel-tick-candidate-20261010/REPORT.md`.

### 3.2 Functions

| Function | Stock | Notes |
|---|---|---|
| `vTaskSuspendAll` / `xTaskResumeAll` | `0x454D7C` (12) / `0x454DCC` (306) | 11 direct callers each |
| `xTaskIncrementTick` | `0x45504C` (338) | SysTick vector slot 15 (`0x43803C`) → wrapper `0x442114`, which masks, ticks and pends PendSV if the tick returns true |
| `xTaskRemoveFromEventList` | `0x455370` (246) | Called at `0x4419F4` (ISR send) and `0x441C10` (receive) |
| `prvResetNextTaskUnblockTime` / `uxTaskGetNumberOfTasks` | `0x455876` (38) / `0x454F10` (6) | |
| `xTaskGetTickCount` / `…FromISR` | `0x454EFE..06` / `0x454F06..10` | Both return the same word |
| `xTaskGetSchedulerState` | `0x4558A4..C4` | 1 = not started, 2 = running, 0 = suspended |
| CMSIS `IS_IRQ` / `osKernelGetTickCount` | `0x44900E..3C` / `0x4490CC..E2` | IRQ if IPSR ≠ 0, or state ≠ 1 and (PRIMASK or BASEPRI) ≠ 0 |
| `portYIELD` | `0x4420BC` (18) | ICSR = `0x10000000`, then DSB/ISB |
| `xQueueGenericSendFromISR` / `prvCopyDataToQueue` | `0x441952` (240) / `0x441ED8` (134) | |
| `xQueueReceive` / `prvCopyDataFromQueue` | `0x441B0A` (314) / `0x441F5E` (42) | |
| `xTimerPendFunctionCallFromISR` | `0x47EB4A` | |
| `xEventGroupSetBits` / `vEventGroupSetBitsCallback` / `xEventGroupSetBitsFromISR` | `0x47ED76` (168) / `0x47EE1E` / `0x47EE4A` | |
| Timer task loop / command processor | `0x47E878` / `0x47E97A` (278) | The processor was missing from the old Ghidra census. |

Sources: `pre-consolidation:g2/analysis/rtos-resume-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/rtos-tick-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/rtos-ready-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/kernel-tick-candidate-20261010/REPORT.md`, `pre-consolidation:g2/analysis/timer-queue-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/event-group-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/timer-daemon-wsf-2026-10-05/REPORT.md`.

### 3.3 Layouts and semantics

- **Queue_t.**

| Offset | Field |
|---|---|
| +0 | head |
| +4 | write |
| +8 | tail |
| +12 | read |
| +16 | `xTasksWaitingToSend` |
| +36 | `xTasksWaitingToReceive` |
| +56 | `uxMessagesWaiting` |
| +60 | `uxLength` |
| +64 | `uxItemSize` |
| +68 | `cRxLock` |
| +69 | `cTxLock` |

  The configured size is 80 B. A list is 20 B. TCB fields used: state item +4, event item +24, priority +44. `pre-consolidation:g2/analysis/timer-queue-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/rtos-ready-wsf-2026-10-05/REPORT.md`
- **Timer daemon dispatch.** A deferred ISR command is a 16-byte `{-2, callback 0x47EE1F, EventGroupHandle_t (borrowed), bits}`. The daemon calls **any negative** command ID as `callback(stack+8, stack+12)`; it does not check for −2. Positive IDs start at `0x47E9B8`. The queue slot is freed before the callback runs, so the event-group pointer must stay valid until the callback completes. `pre-consolidation:g2/analysis/timer-daemon-wsf-2026-10-05/REPORT.md`
- **Event group.** Cell `0x20074EF0` holds an **EventGroupHandle_t**, not a task-notification target. SetBits ORs the low 24 bits. A woken waiter receives the pre-clear bits | `0x02000000`. The WSF wait call is `xEventGroupWaitBits(h,1,clear=1,all=0,portMAX_DELAY)`. `pre-consolidation:g2/analysis/event-group-wsf-2026-10-05/REPORT.md`
- **Ready-list insertion.** It inserts before the current index. During `xTaskResumeAll`, an equal-or-higher priority sets yield-pending. While suspended, removed tasks go to pending-ready. `pre-consolidation:g2/analysis/rtos-ready-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/rtos-resume-wsf-2026-10-05/REPORT.md`

---

## 4. Cordio WSF (Ambiq port, stock layout)

- **WSF OS control block `0x20073230` (64 B).** This layout is **not** public WSF (16 handlers, 16-bit events).

| Offset | Field |
|---|---|
| +0 | 10 handler pointers |
| +0x28 | 10 byte event masks |
| +0x32 | padding |
| +0x34 / +0x38 | message queue |
| +0x3C | task flags |
| +0x3D | handler count |

  `pre-consolidation:g2/analysis/wsf-radio-handoff-2026-10-05/REPORT.md`

| Function | Stock | Behaviour |
|---|---|---|
| OS wake select | `0x52B8D8` (70) | Reads `0x20074EF0` and does nothing if it is 0. In ISR context it calls SetBitsFromISR(h,1,&woken) and pends PendSV only if status && woken. In task context it calls SetBits(h,1), then PendSV plus DSB/ISB. |
| `WsfSetEvent` | `0x52B91E` (64) | Uses `handlerId & 15` with **no validation**: IDs 10/11 hit padding, 12..15 overwrite the queue head, and 23 aliases 7. The mask is truncated to 8 bits and task flags get `|= 4`. Events coalesce. |
| `WsfTaskSetReady` / ready-to-sleep | `0x52B95E` (30) / `0x52B99E` (20) | |
| `wsfOsDispatcher` | `0x52B9D0` (232) | Messages are handled first and freed afterwards. Timer messages are not freed. Events run in ascending ID and are cleared before the call. An event whose handler is NULL stays pending. |
| `WsfQueueDeq` / `WsfMsgDeq` / `WsfMsgFree` | `0x538C4A` (36) / `0x4BF9EC` (20) / `0x4BF9B0` (10) | `WsfMsgFree` subtracts the hidden header. |
| `WsfBufFree` | `0x5304D4..0x530512` (62) | Pool table pointer cell `0x20074EEC`, pool count byte `0x20075044`, freed marker `0xFAABD00D`, 12-B descriptors. It picks the highest pool whose start ≤ ptr, with **no upper-bound check**. |
| `WsfTimerStop` / `wsfTimerRemove` / `WsfQueueRemove` | `0x52A4D2` / `0x52A3FC` / `0x538CC8` | Timer queue head is `0x200741B0`; the started byte is at +13. Stop unlinks and clears the flag but does not free. |
| `WsfTrace` wrapper | `0x52A63C..0x52A672` (54) | Formats into a 1024-B stack buffer with `0x473036`, prints with `0x4733EE`, and calls `WsfAssert` `0x569A44` (line 137, file literal `0x6DF094`) if len ≥ 1024. Newline literal is `0x52A674`. |

Sources: `pre-consolidation:g2/analysis/wsf-radio-handoff-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/timer-queue-wsf-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/wsf-queue-candidate-20261010/REPORT.md`, `pre-consolidation:g2/analysis/wsf-buffer-candidate-20261010/REPORT.md`, `pre-consolidation:g2/analysis/radio-timer-stop-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/wsf-trace-candidate-20261010/REPORT.md`.

---

## 5. Cordio BLE host: lineage and layouts

**Lineage.** Stock behaves like the **AmbiqSuite SDK 5.2 Cordio sources**, not public r20.05c. The exact producing revision is unknown, and the modified source has no public upstream. Apache SDK copies and hashes:

| File | SHA-256 prefix |
|---|---|
| `attc_proc.c` | `90cf6edc…` |
| SDK `l2c_main.c` | `16de4356…` |
| public r20.05c `l2c_main.c` | `b76edc13…` |
| SDK `sec_main.c` | `46ddb191…` |
| public `sec_main.c` | `60e8cfd6…` |

Sources: `pre-consolidation:g2/analysis/cordio-att-guard-binding-20261009-implementation/REPORT.md`, `pre-consolidation:g2/analysis/cordio-signaling-length-ninecase-20261009-implementation/REPORT.md`, `pre-consolidation:g2/analysis/sec-hardware-error-cleanup-20261010-implementation/REPORT.md`.

| Discriminator | Stock (= SDK 5.2) | r20.05c | Src |
|---|---|---|---|
| `l2cRxSignalingPkt` `[0x53076E,0x5308E6)` (376 B) | `UXTH len`; `len < 4` returns **before** `DmConnIdByHandle` `0x4B6E96` | no guard | `pre-consolidation:g2/analysis/cordio-signaling-ninecase-review-20261009-source-track/REVIEW.md` |
| `attcProcRsp` `[0x4B5448,0x4B557A)` (306 B) | method ≥ 18 exits; NULL processor skipped (table `0x700964`, method 10 NULL, method 9 = `0x4B53DC`); min-PDU table `0x785270` = `05 03 02 01 02 01 01 01 02 01 03 05 01`; `WsfTimerStop(CCB+24)` runs **before** the length check | no guards | `pre-consolidation:g2/analysis/cordio-att-guard-binding-20261009-implementation/REPORT.md` |
| ATT `onDeck` indexing | `onDeck[connId-1]`: stock arithmetic `G+384+12·connId` equals `G+396+12·(connId−1)` | `onDeck[connId]` | `pre-consolidation:g2/analysis/cordio-att-ondeck-threecase-20261009-source-track/REPORT.md` |
| `secHciCback` `[0x536234,0x536324)` (240 B), HW-error event 20 | Drains the pubKey (+40 `0x20072CE0`), DH-key (+48 `0x20072CE8`) and AES (+32 `0x20072CD8`) queues **in that order** and frees each with no callbacks. `secCb` is at `0x20072CB8`. | ignores event | `pre-consolidation:g2/analysis/sec-hardware-error-cleanup-20261010-implementation/REPORT.md` |
| `smp_main.c` | Has the stale-AES queue cleanup | absent | `pre-consolidation:g2/analysis/cordio-sdk520-parser-lead-2026-10-09-source-track/REPORT.md` |

- **ATT client.**
  - `attcCb` is at `0x2006F904` and `attCb` at `0x200610AC`.
  - The CCB is 44 B: main pointer +0; outstanding message +4 (event +6, status +7, pPkt +8, handle +12); timer +24; slot +40; connId +41.
  - There are 3 connections × 3 bearers, with connection stride 132. The queue sits at G+396 (3×12 B); `pSign` is at +432 and `autoCnf` at +436.
  - The initializer is `[0x531B1C,0x531B90)`. Packet free is `0x531AC0` and request setup `0x531160`.

  `pre-consolidation:g2/analysis/cordio-att-ondeck-review-20261009-implementation/REPORT.md`
- **L2CAP ACL path.**
  - `l2cHciAclCback` is `0x5308E6..0x530A9C`. It masks the handle at +0 to 12 bits and reads the HCI length at +2; if that length is < 4 the payload length is 0.
  - It requires HCI len == L2CAP len + 4 (32-bit compare, so payload ≤ 65531) and reads the CID at +6.
  - CID 5 dispatches through control block +8 with `(handle, payload_len, original packet ptr)`. It then **always** calls `WsfMsgFree` `0x4BF9B0` at the join point `0x530A94`.
  - The L2C control block is `0x200737D8` (literal `0x530B90`): +0 ATT, +4 SMP, +8 signaling (`0x53076F`), +24 master signaling, +28 slave signaling, +32 other. The ACL callback is `0x5308E7`.
  - `DmConnRole` is `0x4B73C4`.

  `pre-consolidation:g2/analysis/cordio-sdk520-parser-lead-2026-10-09-source-track/CALLER-AND-FIXTURE-CONTRACT.md`
- **SMP.**
  - **`SmpHandler`** is `0x537D0C..0x537E9E` (402 B; 24 BLs to 11 providers). The r1 message has event/status at +2/+3 and a plaintext word at +8. The byte at +2 is compared with `0x20`, `0x1C` and `0x0B`. It handles CMAC cleanup and current/stale AES selection. `pre-consolidation:g2/analysis/smp-dispatch-candidate-20261010/REPORT.md`, `pre-consolidation:g2/analysis/ghidra-mcp-depth-20261010-daybreak/REPORT.md`
  - **`smpCcbByConnId`** is `0x5375FC..0x537742` (326 B). The CCB array is at `0x20070AEC` with **76-B stride**. The ID is truncated to a byte with no upper bound. A zero ID triggers a 5-stage product logging cascade. `pre-consolidation:g2/analysis/smp-ccb-candidate-20261010/REPORT.md`
  - **`SmpDbService`** is `0x542960..0x5429F2` (146 B). It uses a 10-record table at `0x200708EC` and config pointer cell `0x200004B8`. Helpers: in-use `0x541E50`, timer test `0x541E34`, timer start `0x52A4C4`. It divides with `sdiv`, so divisor 0 yields 0. `pre-consolidation:g2/analysis/smp-db-candidate-20261010/REPORT.md`
  - **`smpSmExecute`** is `0x56EE62..0x56F144` (738 B).
    - It checks global +248, CCB pointer +72 and its first byte.
    - Name helpers are `0x56D454` and `0x56D31E`.
    - The tail (`0x56F0EC`) reads CCB +61/+62. Role == 1 selects the table group at base +228/+232. It walks the state table, then a 4-triple fallback, writes the next state and dispatches an indirect action. The base is `0x20070AEC` (literal `0x56F154`).
    - The log formats are `"SMP Exe: evt=%s st=%s"` `0x77BF14` and `"smpSmExecute event=%d state=%d"` `0x765710`.

    `pre-consolidation:g2/analysis/smp-sm-dispatch-tail-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-smp-format-20261010/REPORT.md`
  - **Logging helpers.** Gate `0x4C9C50` reads byte `0x2007502F`. The flags getter `0x43D0CE` reads byte `0x20004543` (bit 1 used). Comparator `0x44B610..0x44B63A` (42 B) is a memcmp-like routine. `pre-consolidation:g2/analysis/diagnostic-flags-candidate-20261010/REPORT.md`, `pre-consolidation:g2/analysis/smp-provider-candidate-20261010/REPORT.md`
- **HCI reset path.**
  - `HciCoreHandler` `0x530CB2..0x530D30` calls the event processor `0x56B390..0x56B7BC`. If the reset-active byte (ctx+21) is set, it then runs `hciCoreResetSequence` `0x569B56..0x569D26` regardless of the processor's result.
  - The command-complete processor is `0x56B182`, and flow control is `0x52AEF8`.
  - `HciLeReadSupStatesCmd` `0x52B37C` builds 0x201C via `0x52AE38` and sends it with `0x52AE5E`.
  - **The 0x201C reply is copied without checking the status byte (offset 5):** 8 bytes are copied from offset 6 to `0x200714D8` inside the HCI CB `0x20071478`. No stock reader of that bitmap was found.

  `pre-consolidation:g2/analysis/emulator-upstream-fresh-2026-10-09-1810-source-track/HCI-201C-STOCK-BINDING.md`, `pre-consolidation:g2/analysis/emulator-upstream-fresh-2026-10-09-1810-source-track/HCI-201C-DATAFLOW-RESULT.md`

---

## 6. Radio (EM9305) host-side board and transport

- **IRQ setup.**
  - `HciDrvRadioBoot` `0x4B48A6` registers ch0 pin 117 with handler `0x4B4A98` and argument NULL. This is bank 3 bit 21, using slots `0x200683FC`/`0x20068AFC`.
  - It enables GPIO117 through `0x52DD58`.
  - It sets IRQ59 priority 4 (IPR byte `0x40`) and NVIC ISER1 bit 27.

  `pre-consolidation:g2/analysis/radio-gpio-consumer-2026-10-05/REPORT.md`
- **ISR callback `0x4B4A98`.** It increments the counter at `0x20074640`, reads the handler-ID byte at `0x20074FCB` (= 7), and calls `WsfSetEvent(7, 1)`. It does **not** do an HCI transfer in the ISR. `pre-consolidation:g2/analysis/radio-gpio-consumer-2026-10-05/REPORT.md`
- **Pin 117 wrappers.** Enable `0x52DD58` and disable `0x52DD6A` return the literal 117, not a status. Disabling does not clear STAT, unregister the callback, touch the NVIC or drain WSF. `pre-consolidation:g2/analysis/radio-gpio-control-2026-10-05/REPORT.md`
- **Shutdown slice.** In `HciDrvRadioShutdown` the slice `0x4B49D0..0x4B49E6` runs, in order:
  1. `WsfTimerStop(0x20073E64)`
  2. disable pin 117 IRQ
  3. clear pin 136 (helper: low byte 0 → WTC4 `0x40010468`, otherwise WTS4 `0x4001044C`, bit 8)
  4. the idle-pins helper `0x52DD7C` (24 B, void): clears pin 93 (WTC2 `0x40010460`, mask `0x20000000`), then sets pin 138 config to raw 3 (word `0x78EE48`); statuses ignored, not atomic
  5. after the slice: caller-global clear, then transport release `0x52DF12`

  `pre-consolidation:g2/analysis/radio-timer-stop-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/ambiq-gpio-board-2026-10-05/REPORT.md`
- **Transport release `0x52DF12`.**
  - The wrapper is `{instance u32 @0, HAL handle @4, init byte @8, power byte @9}`. Instance ≥ 9 returns 1.
  - Steps:
    1. pads `0x4C2E30(inst,0)`
    2. disable-like `0x55C430`
    3. if byte 9 is set, power-like `0x55C7E8(h,2,1)`; clear byte 9
    4. uninit-like `0x55C286`; clear byte 8
    5. return 0
  - All statuses are ignored and the handle is not cleared.

  `pre-consolidation:g2/analysis/radio-transport-pads-2026-10-05/pseudocode.md`
- **Pad dispatcher `0x4C2E30` (570 B).** It accepts instance < 8 and builds key = `(u8)cmd | inst<<2`. Key 4k drives four pads; key 4k+1 drives the first and third. Every pad config reloads word `0x78EE48` (= 3) and ignores the status. `pre-consolidation:g2/analysis/radio-transport-pads-2026-10-05/pseudocode.md`

| Instance | Command 0 pads | Command 1 pads |
|---|---|---|
| 0 | 5, 7, 6, 50 | 5, 6 |
| 1 | 8, 10, 9, 51 | 8, 9 |
| 2 | 25, 27, 26, 11 | 25, 26 |
| 3 | 31, 33, 32, 13 | 31, 32 |
| 4 | 34, 36, 35, 16 | 34, 35 |
| 5 | 47, 49, 48, 17 | 47, 48 |
| 6 | 61, 63, 62, 117 | 61, 62 |
| 7 | 22, 24, 23, 19 | 22, 23 |

  Source: `pre-consolidation:g2/analysis/radio-transport-pads-2026-10-05/pseudocode.md`.
- **IOM-like helpers (names inferred).**
  - Local CQ term `0x55C11A` (32 B): clears slot +0x828 even if CQ validation fails, and returns 0.
  - Disable `0x55C430` (104 B): pending word +0x24 ≠ 0 returns 3. Otherwise it clears reg `0x11C` bit 0, then bit 4 (separately), runs forced CQ term, and clears enable.
  - Uninitialize `0x55C286` (54 B): clears init even if disable reported busy, so enable can stay set.

  `pre-consolidation:g2/analysis/radio-iom-release-2026-10-05/pseudocode.md`
- **Power control `0x55C7E8` (op 2, retain 1).**
  - It requires `(reg 0x248 & 6) == 4` and pending == 0.
  - It snapshots registers into the handle: `0x104→+0x86C`, `0x210→+0x870`, `0x118→+0x874`, `0x11C→+0x878`, `0x228→+0x87C`, `0x22C→+0x880`, `0x234→+0x884`, `0x23C→+0x888`, `0x240→+0x88C`, `0x244→+0x890`, `0x280→+0x894`, `0x2C0→+0x898`, `0x200→+0x89C`.
  - If reg `0x228` (= CQCFG; aliases the register that CMDQ-disable writes) bit 0 is set, it pauses CQ via `0x55C168`.
  - It sets flag +0x868 = 1, then clears `0x11C` bits 0 and 4.
  - It then calls `0x47F7AE((u8)(module+3))` and discards the result, then `0x4C4530(4, …)` and returns that.
  - Stock CQ descriptor rows are at `0x6C0F40`.

  `pre-consolidation:g2/analysis/radio-iom-power-prepare-2026-10-05/pseudocode.md`, `pre-consolidation:g2/analysis/radio-iom-power-prepare-2026-10-05/REPORT.md`

---

## 7. Logging stack

### 7.1 EasyLogger `elog_output` at `0x43D574..0x43D976` (1,026 B)

The analysis directories called this body the "extended logger". Its ABI and state agree with EasyLogger 2.2.99, whose configuration is in [libraries.md](libraries.md): five 33-byte tag-level slots, per-level format masks and a 1,024-byte buffer. The memory map also labels `0x20070BE8` as the elog object and `0x2007456C` as the assert hook.

- **ABI.** r0 level, r1 tag/module, r2 file, r3 function; on the stack: line, format, then varargs. After the prologue the live va pointer is at SP+80. `pre-consolidation:g2/analysis/extended-log-whole-smp-20261010/REPORT.md`
- **Interrupt and fatal paths.**
  - IPSR ≠ 0 returns immediately, so nothing is logged from an ISR.
  - Level ≥ 6 checks cell `0x2007456C`. If it is nonzero, it calls `cb(0x76B634, 0x78A988, 572)`. If it is zero, it logs recursively and then enters the non-returning loop `0x44B0AE`.
  - A NULL module in policy `0x43D4B0` takes the same route with line 481.
  - The installed callback target is unknown.

  `pre-consolidation:g2/analysis/extended-log-float-runtime-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-policy-20261010/REPORT.md`
- **State at `0x20070BE8`** (literal `0x43DA70`).

| Offset | Meaning |
|---|---|
| +1 | module filter |
| +32 | output-token filter string |
| +216 + 4·level | per-level prefix mask (date/time/tick/file/line/function) |
| +240 | module-policy enable |
| +245 | colour/suffix enable |

  Level and colour string tables are at `0x20000974`/`0x2000098C`. Module policy has 5 rows of stride 33: level +49, name (30 B) +50, active +81. The default level is 5. `pre-consolidation:g2/analysis/extended-log-whole-smp-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-module-policy-20261010/REPORT.md`
- **Helpers.**

| Helper | Stock | Notes |
|---|---|---|
| guard enter / exit | `0x43D416` / `0x43D438` | Call lock `0x44AA98` / unlock `0x44AAA0` |
| policy helpers | `0x43D97C`, `0x43D9F0`, `0x43DA0A` | |
| post-format suffix | `0x43D8DC..0x43D970` | |
| shared buffer | `0x2006BD30` | |
| append | `0x44B668..0x44B70A` | Copies while offset < 1024. Writes **no** terminator. NULL asserts. |
| output | `0x44AA80..0x44AA98` | `submit(buf,len,0,(u8)level)`, then `signal(*0x20074570, 1)` |
| token search (strstr) | `0x44B63A..0x44B666` | Uses strchr `0x481818` |
| strlen | `0x44A43C` | |
| memset-like | `0x43C0E4..0x43C14A` | |
| timestamp | `0x44B728` | `snprintf(buf,5,"%ld" @0x43DA6C, tick)` |
| time providers | `0x44AAA8`, `0x44AB14`, `0x44AB1C` | |

  Sources: `pre-consolidation:g2/analysis/extended-log-frontier-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-append-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-output-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-token-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-memory-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-time-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-postformat-20261010/REPORT.md`.
- **Formatter `0x44B76C`** (vsnprintf-like, over DLIB `printf_core` `0x481836`).
  - `%p` is lowercase hex with **no** `0x` prefix.
  - It handles flags `0`/`-`/`#`, widths, `%.*s`, `l`/`z`, `%c`, and `%llu`/`%lld` as two words.
  - `%f` uses `vmul.f64` at `0x4D435C`. Float arguments are promoted to doubles at stack +8/+16/+24 (caller `0x49D580`).

  `pre-consolidation:g2/analysis/extended-log-common-format-20261010/REPORT.md`
- **Caller census.** There are 6,239 direct BLs to `0x43D574`. Of these, 6,227 resolve to flash format literals (5,032 distinct formats). The 12 runtime-format sites are inside wrapper `0x56D478`: four use r8 (its r0 format parameter, 30 callers) and eight use a stack hex-dump buffer at sp+8. Eighteen sites use `%f`. `pre-consolidation:g2/analysis/extended-log-caller-inventory-20261010/REPORT.md`, `pre-consolidation:g2/analysis/extended-log-float-runtime-20261010/REPORT.md`

### 7.2 Other loggers and printers

- **Short event logger `0x43CE9E..0x43CF02` (100 B).** It is also `audio_log_simple`; older notes mislabel it "compress".
  - It reads a policy byte via `0x44A9AE` and rejects IPSR ≠ 0.
  - It checks the lock word `0x20074388`.
  - The token is the high 10 bits of r0 OR the low 22 bits of r1.
  - It takes the lock with timeout 500, calls short formatter `0x43CB84(r2 fmt, &varargs)`, and unlocks.
  - It always returns 0.

  `pre-consolidation:g2/analysis/main-flashdb-short-log-20261010/REPORT.md`
- **Diagnostic print `0x4733EE..0x47341A`** (FlashDB `FDB_PRINT` and WsfTrace).
  - It returns 0 if the sink pointer cell `0x200742F0` is NULL.
  - Otherwise it calls `0x473036(buffer 0x2006B930, fmt, va)`, reloads the sink, and calls `sink(buffer)`.
  - `0x473036` is an AmbiqSuite R3.2.0-adapted `am_util_stdio` vsprintf. It takes **no capacity** argument. Its newline-translation cell is `0x20074F7F`.

  `pre-consolidation:g2/analysis/main-flashdb-short-log-20261010/REPORT.md`, `pre-consolidation:g2/analysis/main-print-lower-frontier-20261010/REPORT.md`

---

## 8. FlashDB 2.1.1 and FAL in main

- **Configuration proofs.** These come from original bytes plus pinned headers:
  - **Short enums.** The KVDB object is 2,220 B (`0x8AC`) with 64/64 caches; default enums would make it 2,744. The KV object is 88 B (value_len +12, addr.value +84); default enums would give 92/+16/+88.
  - **`FDB_WRITE_GRAN = 1`.** The KV header magic is at +4; granularity 8/32/64/128 would put it at 8/20/40/80.
  - **`FDB_KV_NAME_MAX = 64`.** `create_kv_blob` `0x544D60` rejects `strlen ≥ 65`; values 61–65 were tested.

  `pre-consolidation:g2/analysis/flashdb-blob-build-interface-20261010-implementation/REPORT.md`, `pre-consolidation:g2/analysis/flashdb-provider-config-20261010-implementation/REPORT.md`, `pre-consolidation:g2/analysis/flashdb-provider-execution-20261010-implementation/REPORT.md`
- **DB object fields.**

| Offset | Field |
|---|---|
| +8 | name/path pointer |
| +12 | sector size |
| +16 | max size |
| +24 | `init_ok` |
| +25 | file-mode flag |
| +28 / +32 | lock / unlock |
| +168 | KV cache, 64 × 8 B |
| +680 | sector cache, 64 × 24 B (address at +4) |

  `pre-consolidation:g2/analysis/main-flashdb-short-log-20261010/REPORT.md`
- **App wrapper `SVC_FlashDBBlobRead` `[0x54116E,0x5411F2)` (132 B).**
  - It selects db = `0x2005DFFC + (idx&0xFF)·0x8AC`, narrows len to u16, builds a 20-B `fdb_blob` (buf +0, size +4, saved.len +16), and calls `fdb_kv_get_blob` `0x54454A`.
  - It calls `osKernelGetTickCount` twice and ignores the result.
  - If `saved.len == 0`: flag bit 1 logs through `elog_output` (level 1, line 241, `"get the %s value fail, len = %d\n"`). Flag bit 0 or 2 logs through the short logger with token `0x04800000`.
  - It has 9 callers: `0x4D9578`, `0x4D965E`, `0x4D981C`, `0x4D9956`, `0x4D99E8`, `0x5105FC`, `0x5106AE`, `0x510852`, `0x510948`.
  - Literal pool:

| Literal | Value | Meaning |
|---|---|---|
| `0x5412C8` | `0x2005DFFC` | DB array |
| `0x541268` | `0x78E54C` | `db.api` |
| `0x541264` | `0x6E4CC8` | build path |
| `0x5412D0` | `0x783190` | function name |
| `0x5412CC` | `0x75996C` | format |
| `0x5412D4` | `0x743150` | prefixed format variant |

  `pre-consolidation:g2/analysis/main-flashdb-import-frontier-20261010/REPORT.md`, `pre-consolidation:g2/analysis/rea-wide-mapping-exhaustion-20261010-daybreak-low/REPORT.md`
- **Function map** (all pinned 2.1.1 bodies):

| Function | Stock | Function | Stock |
|---|---|---|---|
| `update_sector_cache` (picks the **last** empty slot) | `0x543C48..0x543CC0` | `get_sector_from_cache` | `0x543CC0..0x543CEC` |
| `update_kv_cache` | `0x543D1C..0x543E28` | `get_kv_from_cache` | `0x543E28..0x543EE8` |
| `find_next_kv_addr` | `0x543EE8..0x543F8C` | `get_next_kv_addr` | `0x543F8C..0x544000` |
| `read_kv` | `0x544000..0x54418E` | `read_sector_info` | `0x54418E..0x544374` |
| `get_next_sector_addr` | `0x544374..0x5443B0` | `kv_iterator` | `0x5443B0..0x54443A` |
| `find_kv_cb` / `find_kv_no_cache` | `0x54443A` / `0x54447A` | `find_kv` | `0x54449A..0x5444F4` |
| `get_kv` (ignores the read result) | `0x5444F4..0x54454A` | `fdb_kv_get_blob` | `0x54454A..0x5445B2` |
| `write_kv_hdr` | `0x5445B2` | `create_kv_blob` | `0x544D60` |
| `fdb_calc_crc32` (0xEDB88320, table) | `0x585840..0x585870` | `_fdb_set_status` / `_fdb_get_status` / `_fdb_write_status` | `0x585870` / `0x5858A8` / `0x5858D8` |
| `_fdb_continue_ff_addr` (ignores read errors) | `0x5859A0..0x585A12` | `_fdb_flash_read` / `_fdb_flash_write` (FAL ignores sync) | `0x585A12` / `0x585A52` |
| `_fdb_db_path` (flag db+25, ptr db+8) | `0x585C94..0x585CA4` | | |

  `pre-consolidation:g2/analysis/main-flashdb-short-log-20261010/REPORT.md`
- **`write_kv_hdr`.**
  - It calls status `0x5858D8(…,6,1,false)`.
  - **Only if the low byte of the result is 0** (UXTB at `0x5445D2`) does it call flash-write `0x585A52(addr+4, hdr+4, 20, false)`.
  - Its results are narrowed to u8.

  `pre-consolidation:g2/analysis/flashdb-provider-execution-20261010-implementation/CORRECTION.md`
- **FAL.** Shapes match RT-Thread FAL `aa0211218634a613d3638425a830854bd07a0b76`, but that pin is not verified as the stock source.
  - Cache fill is `0x597C6C`. `fal_partition_init`'s static branch is `0x597CAE`: table base `0x6D5358`, count 2 at `0x200745E0`, table pointer at `0x200745DC`.
  - `flash_device_find_by_part` `0x597D10` computes `(part−base)>>6`, so rows are 64 B. The device cache is at `0x20074140`.
  - `fal_partition_read` `0x597D34` and `_write` `0x597D72` use partition offset +0x34 and length +0x38, and device ops +0x28/+0x2C. The uint32 bounds check can wrap.
  - `fal_flash_device_find` `0x597E54` uses strncmp(…, 24). The table at `0x78F0A4` holds 1 device, `0x722B30` (count at `0x78F0A8`).

  `pre-consolidation:g2/analysis/main-flashdb-short-log-20261010/REPORT.md`

---

## 9. Other libraries in main

- **TLSF v3.1 (`deff9ab5`).**
  - Entry points:

| Function | Stock |
|---|---|
| `tlsf_create` | `0x4D06EC` (42 B) |
| `tlsf_malloc` | `0x4D0722` (34 B) |
| `tlsf_free` | `0x4D0808` (74 B) |
| `tlsf_realloc` | `0x4D0868` (226 B) |
| assert | `0x4D09B4` |
| internal | `0x4CFF6C`, `0x4CFF9A`, `0x4CFFC2`, `0x4D0524` (init, takes r0 only) |

  - The control block is `0xC74` B: 24 FL × 32 SL, SL bitmaps at +0x14, free lists at +0x74, row stride `0x80`.
  - **The stock uses the portable generic bit-scan fallback** (public TLSF has no IAR branch): generic fls `[0x4CFD18,0x4CFD56)`; ffs `[0x4CFD56,0x4CFD66)`, which computes `x&-x` then subtracts 1; fls wrapper `[0x4CFD66,0x4CFD70)`.
  - Behaviour equals pinned v3.1 over a 64 KiB arena, but the public compiled bodies differ in bytes.

  `pre-consolidation:g2/analysis/tlsf-main-source-comparison-20261010-implementation/REPORT.md`, `pre-consolidation:g2/analysis/tlsf-main-runtime-boundary-20261010-implementation/REPORT.md`, `pre-consolidation:g2/analysis/rea-wide-mapping-exhaustion-20261010-daybreak-low/REPORT.md`
- **LZ4.**
  - Entry points: `read_variable_length` `0x54EE90..0x54EF06`, `LZ4_decompress_generic` `0x54EF08..0x54F338`, `LZ4_decompress_safe` `0x54F338..0x54F356`, local helpers `0x54EE18..0x54EE8C`.
  - Behaviour is identical to both v1.9.4 and v1.10.0 on the discriminator set, so no version is selected.
  - Offset 0 is accepted, as in upstream; the spec calls such a block corrupt.
  - A zero compressed size returns −1. Token `00` returns 0.
  - **Outer caller `0x4E0C0C..0x4E0C34`** returns 0 for any NULL or zero argument and returns 0 for any result < 1, so it hides decoder errors. The emulator's `0x56192E` call site belongs to a different firmware version.

  `pre-consolidation:g2/analysis/apollo-lz4-source-discriminator-20261009T211300Z/pseudocode.md`
- **TinyFrame CRC.** The update at `[0x491730,0x49174E)` (30 B) computes `crc = T[(crc^b)&0xFF] ^ (crc>>8)`. The table literal at `0x491EF0` points to a 512-B table, which is reflected polynomial `0xA001` (CRC-16/ARC). The window `[0x4916C8,0x491752)` also holds lock, unlock, init and final helpers. `pre-consolidation:g2/analysis/tinyframe-checksum-build-gap-20261010-implementation/REPORT.md`
- **NemaGFX.**
  - Stock `nema_cl_bind_sectored_circular` `0x5143D4..0x5144BA` is 230 B (SHA `1b72806a…`).
  - The SDK 5.2 IAR 9.70.1.475 `nema_cmdlist.o` symbol is 222 B. Stock has an extra `ldr r2,[r0,#24]; bic r2,#0x20; str` at `0x514476`, which clears cmdlist flag bit 5. That object is therefore not the stock producer.
  - Lineage is unresolved. A NEMAP 1.4.15 note moved the circular-flag set from unbind to bind, but that does not prove this is the same change.
  - Related: `nema_set_error` `0x4B127C`; `nema_context` cell `0x20074EFC` (literal `0x514B78`).
  - The SDK header says 1.4.12 while its changelog reaches 1.4.17.

  `pre-consolidation:g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/FINAL-STATIC-RESULT.md`, `pre-consolidation:g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/LINEAGE-RESULT.md`
- **CMSIS-DSP is probably not linked.** Twenty functions from the SDK 5.2 IAR M55 DSP archive (`iar_cortexM55f_math.a`, IAR 9.60.4.438) were searched for, plus four large tables (`armBitRevTable`, `sinTable_f32`, `twiddleCoef_4096`, `twiddleCoef_rfft_4096`). There were zero exact hits in main. `pre-consolidation:g2/analysis/cmsis-m55-iar-inclusion-2026-10-09-source-track/REPORT.md`

---

## 10. Peripheral drivers in main

- **TDK ICM-45608 host driver.**
  - `semantic_set_orientation_matrix` `0x4A460C..0x4A46B0` turns 9 floats into a Q14 cache at `0x20000E00`, raw floats at `0x20000E38`, and Q30 values at `0x20000E14` (columns 0/1 negated). Its caller is `HUB_IMUCalibParaInit` `0x4A6BCE`, via `0x4A6C02`.
  - Mounting writer `0x507710..0x507726` writes SRAM `0x1AC`, 18 B, directly from the Q14 buffer. The public driver uses an int8 conversion here; stock does not.
  - SRAM write `0x508E92` → `0x508FA6`: validates with `0x508ED2`, sends 3 B (address hi/lo plus the first byte) to reg `0x7C`, then the remaining bytes one at a time to `0x7E`. Delay callback is device+12 with argument 4. Direct reg write is `0x508EB6`.
  - Device context is `0x20073020`: read `0x4A35B0`, write `0x4A35EA`, delay `0x491102`. Bus 4, I2C address `0x69`. Bus functions are `0x50436E`/`0x5044B4`.
  - GAF entry `0x506ECA` (caller `0x4A4054`) reads ODR registers `0x1B`/`0x1C`. It writes a 125-B patch (`0x6D53D8`, SHA `80eb396b…`) to SRAM `0xC80`, then a 4-B key (`f1 70 0c c0`) to SRAM `0xB4`.
  - **There is no conditional unequal-ODR write to SRAM `0x50`.** That rules out TDK 1.1.8 as-is. The exact older revision has not been chosen.

  `pre-consolidation:g2/analysis/tdk-transport-independent-review-2026-10-09/REPORT.md`, `pre-consolidation:g2/analysis/tdk-stock-binding-search-2026-10-09/REPORT.md`
- **BQ27427 fuel gauge.**
  - The descriptor table is in decoded SRAM `0x200006EC..0x20000724`: seven 8-B entries `{subclass, block, offset, type, …, value}`. Subclasses: 82/82/82/64/82/81/105.
  - Configure `0x53BB8C..0x53BCDA` (root literal `0x53C1CC`) writes **0x28 over the whole byte** at subclass 105, block 0, offset 5. Zephyr's CC Gain workaround only clears bit 7.
  - Generic update is `0x53B6F0` (valid flag at buffer+34, dirty at +35).
  - Commit `0x53BA32` writes class, block and 32 B, then the checksum (`0x53B522`) to reg 60.

  `pre-consolidation:g2/analysis/bq27427-descriptor-binding-2026-10-09/REPORT.md`
- **MX25U25643G NOR.**
  - The JEDEC ID is `C2 25 39`; stock packs it as `0x002539C2` (little-endian).
  - Commands used: 9F, 03, 02, 20, B7 (EN4B) and 6C (QREAD4B: 1-1-4, 8 dummy cycles, requires QE, not in QPI).
  - The vendor LLD 1.1b is **Macronix-proprietary, internal use only**.

  `pre-consolidation:g2/analysis/macronix-official-sample-discovery-2026-10-09/REPORT.md`
- **OPT3007.** `ti_opt3007_assignRegistermap` `0x5135E0..0x513734` holds 19 register triples. The Linux `opt3001.c` (`ffc25326`, GPL-2.0) matches the protocol: ID registers `0x7E`/`0x7F`, byte-swapped 16-bit reads, 4-bit exponent and 12-bit mantissa. `pre-consolidation:g2/analysis/internal-sdk-discovery-2026-10-09/REPORT.md`
- **Display L8 assets.** All six are colour format 6, flags 0, stride = width.
  - Path: constructor `0x5BF332` → `0x5BF2F8` → image setter `0x498680`.
  - Decoder registration `0x4C794C`: header callback `0x4C79D1`, open callback `0x4C7B25`. The pixel pointer is at descriptor +0x10.
  - Draw-buffer init is `0x48B762` → `0x48AEF8`; it rejects buffers with too little storage.

| Descriptor | Size (px) |
|---|---|
| `0x768374` | 34×24 |
| `0x7682CC` | 68×28 |
| `0x7682E8` | 163×52 |
| `0x768320` | 44×32 |
| `0x768358` | 187×64 |
| `0x76833C` | 86×50 |

  `pre-consolidation:g2/analysis/firmware-byte-map-2026-10-05/README.md`

---

## 11. Even bootloader (BL, base `0x410000`)

**Startup.**
- `0x432910` writes `VTOR=0x410000`. The stack-limit literal is `0x2007D000`.
- `0x43299C` walks the scatter/init records at `0x4330D8..0x433120`. Each slot-relative callback returns the next record; this is **not** a constructor array.
- The OTA payload does not contain ROM MRAM-program `0x0200FF21`, the ROM entries `0x41`/`0x49`, or the SBL at `[0x400000,0x410000)`.
- A 22-byte compressed ITCM helper expands to 24 B. The bootloader may therefore populate its own ITCM `0x40` region, as main does; check that before treating `0x41` as ROM.

Sources: `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/RECOVERY-AND-CHECKLIST.md`, `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/remaining-providers-current.md`.

| Area | Stock BL address → role | Src |
|---|---|---|
| Kernel/CMSIS | Context guard `0x41602A` (IPSR ≠ 0 rejects; mode `0x418B56` == 1 allows; otherwise PRIMASK/BASEPRI ≠ 0 rejects). State `0x416088` (mode 0 → 3, mode 2 → 2, else word `0x200270D4` == 1). Init `0x416058` and start `0x4160B0` (state 0 → 1 → 2; calls no-op `0x416028`, then scheduler start `0x418148`). Tick `0x4160E8` reads `0x20027148`. Thread new `0x4160FE`. Terminate `0x416200`. Flags set/wait `0x41623A`/`0x4162C4`. Task delay `0x416378`. | `pre-consolidation:g2/analysis/bootloader-source-candidate-20261010/REPORT.md` |
| Queues | Submit `0x41649A`: guard → −6, NULL → −4, lower result 1 → 0, else → −3. Envelope `0x41937C..0x4193DE` is a 12-B `{class,payload,event}` record on queue `0x20027180`; class < 6 uses blocking put `0x419EC0`, ≥ 6 uses the ISR put. Create/put/get `0x416816`/`0x4168A2`/`0x416920`. Static ctor `0x419C9C`. Init `0x419D68`. Reset `0x419BE8`. Dynamic `0x419D08` (80 B from heap `0x419730`). Destroy `0x41A470` and free `0x419830`. Queue fields: count +0x38, max +0x3C, item +0x40, static flag +0x46, type +0x4C. Heap arena is 81,920 B. | same; `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/semaphore-REPORT.md` |
| Mutex/semaphore | Mutex create `0x416610` (record `0x433D28`; elog mutex static 80 B at `0x20026CB0`). Acquire/release `0x4166AA`/`0x416710`. Semaphore create `0x416762` (maximum 1 → type 3, > 1 → type 2; handle stored at `0x20027104`). | same |
| Scheduler/port | Suspend `0x4181D8` (depth `0x2002716C`). Reschedule `0x41B3D0` (PendSV). BASEPRI mask `0x41B2F8`; **clang -O2 output is byte-identical** to its 22 B. Critical save `0x41B8EC`. Task return `0x41B390`. Malloc-failed hook `0x41B5F6`. Stack-overflow hook `0x41B600` (name at TCB+0x34). Idle cleanup `0x418A98`. | `pre-consolidation:g2/analysis/bootloader-source-candidate-20261010/REPORT.md` |
| Core setup | CPACR `0x41AC44` (sets `0x00F00000`). FPCCR lazy mode `0x41AC5A`. I-cache enable `0x41E1E8` (guard `0xE001E300`, CCR bit 17, ICIALLU `0xE000EF50`). D-cache `0x41E266`. Cache maintain `0x41E348..0x41E442`. | same |
| Delay | `0x41D1C0` (80 B, float math, then the ROM cycle routine). Wrappers `0x41F9D8`/`0x41F9E6`. | same |
| Logging | EasyLogger output `0x4176CE` uses the canonical `(level,tag,file,func,line,fmt,…)` order. Setters `0x4173CA`/`0x417438`/`0x417510`/`0x4174A6`. Plain printf `0x415FAE..0x415FDA` (callback slot `0x200270CC`, buffer `0x20024CD0`; restores incoming R3 into R1). elog snprintf/vsnprintf `0x41B218`/`0x41B25C`. The littlefs callbacks use `0x415FAE`, but mount errors (`0x4210C8`/`0x4211B0`/`0x421210`) use `0x4176CE`; the two ABIs differ. | same |
| NOR/MSPI | Status PIO `0x4205F4..0x42069E` (instr, addr, flag, dst, len; the ready poll at `0x42074E` sends instr 5, len 1). Command transfer `0x42069E..0x42074E` (error format at `0x431468`). Erase `0x420A08`. Program `0x420B0C`. Mode-switch call sites `0x420C80`/`0x420D92`. littlefs read/prog/erase `0x4212D8`/`0x421310`/`0x421348`. Clock request `0x4222F0` (class 4). HAL power control `0x426808`. memset `0x426C10`. | same |
| NOR read quirks | One 24-B RX PIO command (`0x6C`, turnaround 1, timeout 1,000,000). It checks only the start address. Any nonzero status maps to `LFS_ERR_IO`. | `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/CONTINUING-SOURCE.md` |
| Platform/IOM | Configure `0x41F846` (four 28-B rows). Init table `0x41F9F8` (four records). Device-mode publish `0x41FADC`. Allocator init `0x41FD70` ("tlsf init.", line 19). Main init `0x41B862`. Context claim/enable/IRQ/transaction/configure `0x42C4C6`/`0x42C538`/`0x42C63A`/`0x42C988`/`0x42CC34`. NVIC enable `0x430470` (IRQ 10). Retry `0x43048E`. Descriptor publisher `0x42C45A` (32-B entries at ctx+0x854). Service `0x42C6F8`. Bring-up `0x430000..0x4301D6`. | same; `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/semaphore-REPORT.md` |
| DFU | Send `0x42DCA2` (10-word message). Terminal `0x42E1DA` (DFU flag bit 23). OTA-fail log `"Bootloader ota fail, system reset!!!"` at `0x42DE12`. Thread deinit `0x42DDDA`/`0x42E3CA`. Platform terminal `0x4329C4`. | `pre-consolidation:g2/analysis/bootloader-source-candidate-20261010/REPORT.md` |
| Power (PCM) | Startup power root `0x41C4B4` (unresolved). Dispatch `0x41CE52`. Power-state wrapper `0x41CD1A` (slot `0x20026E3C`). Boost service `0x41CDB8` (slot `0x20026E64`). Power-register read/update `0x41D90E`/`0x41D92C`. TON gate `0x41C838`. PCM2.2 spot timer `0x41CC48`/`0x41CCD6`. Event-A selectors 0 `0x427E84` and 2 `0x428240`. Timer service `0x42A04A` (state 2 → `0x428378`, 7 → `0x428A94`). Selector 8 `0x428BB0`. Transitions 14/15/16/17/18: `0x42944A`/`0x429524`/`0x42962C`/`0x429718`/`0x42984E`. Selector/walker `0x42A2B4`/`0x42A43A` (matrix `0x433498`). TON adjust `0x42A1BC`. Trims `0x42A4BC`. SPOT trims `0x42AE24`/`0x42AE6C` (these test the **low byte** of R0). PCM2.1 temperature `0x42BF54` is the same algorithm as PCM2.2 `0x42AC54` (S0 = −40.0f, MSPI selector 29, poll `(2500,0x400083E0,1,0)`). | same |
| BL009 callbacks | SRAM table: slot 8 at `0x20026E40` (`0x42D848` is `return 0`); slot 0x34 at `0x20026E6C` (ORs bits 0–1 of `0x400211A0`, sets ready byte `0x200271B8`); slot 0x38 at `0x20026E70` (reverses that). Timing callbacks gate on `0x200271A8` and write the low 10 bits of `0x40020080` (threshold 8/subtract 7, special 7/6). Config writes the low 6 bits of `0x40020088` and bits 15–16 of `0x400201B0`. The SPOT installer stores 29 callback addresses. | same |
| UART | Ctor `0x422AD4`. Power `0x422BA8`. Activate `0x422DC6`. Baud `0x422E28`. Config `0x42308E`. Status/mask `0x4236CE`/`0x423700`. Ring `0x4275EA`. Static pool of four contexts at `0x20024400..0x20024870`; rows published at `0x2002451C`/`0x20024638`/`0x20024754`. Row 3 borrows TX buffer `0x20080800` (1 KiB). | `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/REPORT.md` |
| ADC | Profile `0x42F020`, apply `0x42EA68`. Region `0x42E8D0..0x42F14E` (14 functions). Timer enable `0x40038040`. TEMP channel 8 skips correction. Correction keeps 12 bits. Power enter/leave errors are ignored. | same |
| Misc | ITM/debug release `0x423D20`/`0x423DD0`. Config/temp/logger sink `0x41C86C`/`0x41CA2C`/`0x41583C`. The clock mux `0x41AF84..0x41AFBC` restores pin register 15 when EXTREF is enabled without PLL. | same |

- **Device info.**
  - Mode-1 helper `0x41D294` (→ `0x41D792`) returns a 64-B `am_hal_mcuctrl_device_t`. Words 0–5 are part, ID0/ID1, revision, vendor, SKU. Word 6 = 1. **Word 7 (NVM size) is left untouched.** Words 8–11 are ITCM/DTCM/SSRAM/MRAM sizes in bytes. Words 12–15 are the JEDEC fields.
  - SKU low-bit memory tuples (KiB): (128,256,1024), (128,256,2048), (256,512,2048), (256,512,3072). SKU bits [3:2] select MRAM 1024/2048/3072/4096 KiB.
  - The symbol `opencfw_boot_device_clock_factors` is misnamed; its table holds memory sizes.
  - Range validation caches word 11 at `0x200270C8` and rejects addresses below 4000. It checks only `size < MRAM`, **not** address+size.
  - The INFO/OTP read service is `0x4213E6`.
  - Selector 0 returns a 16-B feature record of byte fields (proves byte-sized enums). Its trim word is read from INFO1 +0x244.

  `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/DEVICE-INFO-LAYOUT.md`
- **Library lineage.**
  - littlefs 2.10.1: `lfs_config` `0x431070`, public API `0x415128..0x41531C`.
  - TLSF v3.1: control `0xC74`, 24×32, arena `0x70800`.
  - EasyLogger 2.2.99 (`elog.c`/`elog_utils.c`) with a synchronous channel-1 sink.
  - MSPI HAL 5.1.0.
  - The FreeRTOS revision is **not** inherited from main.

  `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/upstream-worker/REPORT.md`

---

## 12. Other payload notes from these experiments

- **EM9305 v4.2 vs v4.6.** The public mirror `C0R3YY2/em9305_original` @ `e4412bc98d4e76d441d1226ca3696e53cfae5f54` contains the `emcore/bin/v4.2/standard` ihex and sym files. Forty named v4.2 bodies match stock exactly. Eighteen of them distinguish v4.2 from v4.6:

`IRQ_Cleaning`, `NVMEntry_CopyJLITable`, `NVM_AfterOperation`, `NVM_BeforeOperation`, `PML_Dbm2PmlRfPower`, `ProtTimer_StoreConfig`, `RF_BleChannel2RfChannel`, `RF_GetOutputPower`, `RF_Ln`, `RF_RfChannel2BleChannel`, `RF_SetMacTiming`, `RF_TestModeStart`, `SleepTimer_SetWakeupTime`, `VoltMon_UpdateFlags`, `gIRQ_PRIORITY`, `llPrbs9Payload`, `receiverTestCheckParameters`, `scan15_4CheckParameters` (whose size differs in v4.6).

  The files are kept under ignored `third-party/local-vendor/sources/em9305-v4.2-public-mirror/`. `pre-consolidation:g2/analysis/daybreak-source-frontier-20261010/REPORT.md`
- **GX8002 codec toolchain.** NationalChip's documentation names C-SKY Tools V3.10.15 Minilibc abiv2 B20190929 (GCC 6.3.0). The archive is `csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz` (105,910,950 B, SHA `df33d1e1…`). The official share link has expired, and the tarball contains no LICENSE file. `lvp_aiot d4aa0094` requires CK804ef hard-float. `pre-consolidation:g2/analysis/emulator-upstream-dsp-provenance-2026-10-09-source-track/REPORT.md`
- **GX8002 callback root.**
  - Stored slot `0x10026D38` points to `0x20026D3C`, a 32-B sample-app descriptor: init `0x10208E4C`, event `0x10208F04`, loop `0x102091BC`, suspend `0x10208DEC`, resume `0x10208DCC`.
  - The loader copies 14,716 B to IRAM `0x10023400–0x10026D7C`, and BSS clearing starts at `0x20026D80`.
  - Whether IRAM is aliased into DRAM is unproven.

  `pre-consolidation:g2/analysis/callback-root-boundary-integration-2026-10-09/REPORT.md`

---

## 13. SDK 5.2 inventory, licensing and SDK bugs

- **Archive compilers.** The SDK has 55 archives:

| Archive | Compiler |
|---|---|
| Apollo510/510L/330P HAL+BSP | IAR 9.70.2.500 |
| CMSIS M55 DSP | IAR 9.60.4.438 |
| Nema IAR extension | IAR 9.40.2.374 |
| `lib_nema_apollo510_nemagfx.a` (SHA `8c620449…`) | IAR 9.70.1.475 |
| CryptoCell / mbedTLS 2.16.2 | GCC/Keil |

  No IAR DLIB/runtime archive is included. `pre-consolidation:g2/analysis/sdk-520-public-source-map-2026-10-09-source-track/REPORT.md`
- **Licensing.**
  - The AM-BSD-EULA is BSD-3-style but defers to third-party terms.
  - The ThinkSi grant covers headers and documentation only.
  - The Ambiq PDF terms restrict reverse engineering and unbundled redistribution.
  - **Nema binaries are therefore not redistributable** and cannot be public submodules.

  `pre-consolidation:g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/LICENSE-AND-COMPARATOR-RESULT.md`
- **Access.** The SDK portal (`contentportal.ambiq.com`) requires login. `pre-consolidation:g2/analysis/middleware-iar-nema-gap-2026-10-09-source-track/OFFICIAL-ACCESS-FOLLOWUP.md`
- **`am_util_stdio_snprintf`/`vsnprintf` (SDK 5.2) is non-standard and unsafe.**
  - It copies accepted bytes **without a NUL**.
  - If capacity is too small it returns 0 and leaves the destination untouched.
  - It formats into the global `g_prfbuf` (1024 B, or 2048 B with 4096 alignment under `AM_PART_APOLLO5_API`) **before** checking n. Oversized input therefore overflows the internal buffer even when n = 0 or 1.

  `pre-consolidation:g2/analysis/sdk-formatter-buffer-20261010-implementation/REPORT.md`

---

## 14. Emulation and tool lessons

- **Unicorn 2.1.4 skips an instruction under memory hooks.** With a valid memory-access hook installed over accessed RAM, Unicorn can skip the first instruction after a false `ITcc`. This was reproduced in FreeRTOS O2 list insertion and FlashDB O1 `get_kv`. O0 builds and runs without hooks behave correctly. It is an engine bug; do not patch firmware or source around it. `pre-consolidation:g2/analysis/unicorn-it-divergence-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/flashdb-o1-read-diagnosis-20261010-implementation/REPORT.md`
- **Unicorn instruction gaps.**
  - The Unicorn M4 model rejects M55 `CSEL`/`CSET` and `MRS IPSR`.
  - M4, M7 and M33 cannot run `vmul.f64`. Use an M33-with-VFP model for FP64 bodies.
  - QEMU 11.1.2 MPS3-AN547 runs M55 FP64 but cannot map `0x438000`.
  - Unicorn on macOS crashes when creating an ARM engine; the Linux container works.
  - LZ4 `memmove` fails in continuous mode and works when single-stepped.

  `pre-consolidation:g2/analysis/extended-log-float-runtime-20261010/REPORT.md`, `pre-consolidation:g2/analysis/apollo-lz4-source-discriminator-20261009T211300Z/REPORT.md`, `pre-consolidation:g2/analysis/bootloader-source-candidate-20261010/REPORT.md`
- **Ablation (`97e051b4`).** It needs reviewed function starts and the Thumb state. Its direct-call inventory is complete only for functions ≤ 4,096 B, because of a hard per-function scan cap. Its whole-image graph assigns gap or data calls to the preceding function and drops call sites. `pre-consolidation:g2/analysis/ablation-whole-main-frontier-20261010-daybreak-low/REPORT.md`
- **Ghidra-MCP 7.0.0 (`9cc29c0f`).** On a single-body ELF the stored function body is degenerate, so CFG, xref and call-graph queries return empty. `get_function_pcode(granularity=high)` still recovers the full high P-code. `pre-consolidation:g2/analysis/ghidra-mcp-depth-20261010-daybreak/REPORT.md`
- **REA (Ghidra 12.1.4, ephemeral).** Use the whole-payload analysis ELF; it yields 7,341 procedures and 17,010 strings. Its types are low-confidence; for example it shows `undefined8` for `0x54454A`, which really returns in r0. `pre-consolidation:g2/analysis/rea-wide-mapping-exhaustion-20261010-daybreak-low/REPORT.md`

---

## 15. Stock quirks worth preserving (summary)

1. GPIO state-write has no pin bound and aliases bank 7 and pin 256. Interrupt-control does not validate the channel. `pre-consolidation:g2/analysis/ambiq-gpio-board-2026-10-05/pseudocode.md`, `pre-consolidation:g2/analysis/radio-gpio-control-2026-10-05/REPORT.md`
2. MSPI deinit, IOM uninit and CMDQ forced-term all report success without draining or freeing. `pre-consolidation:g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/radio-iom-release-2026-10-05/pseudocode.md`
3. WSF `handlerId&15` aliasing, WSF critical-exit unmasking, and FreeRTOS outer exit forcing BASEPRI to 0. `pre-consolidation:g2/analysis/wsf-radio-handoff-2026-10-05/REPORT.md`, `pre-consolidation:g2/analysis/timer-daemon-wsf-2026-10-05/REPORT.md`
4. `WsfBufFree` has no upper bound when selecting a pool. `pre-consolidation:g2/analysis/wsf-buffer-candidate-20261010/REPORT.md`
5. HCI 0x201C states are copied without a status check. `pre-consolidation:g2/analysis/emulator-upstream-fresh-2026-10-09-1810-source-track/HCI-201C-DATAFLOW-RESULT.md`
6. The LZ4 outer caller hides errors, and the decoder accepts offset 0. `pre-consolidation:g2/analysis/apollo-lz4-source-discriminator-20261009T211300Z/pseudocode.md`
7. The RTC accepts year 100 (BCD `0xA0`) and impossible dates. `pre-consolidation:g2/analysis/rtc-setter-boundaries-20261009-implementation/OWNER-CONTRACT.md`
8. BQ27427 writes the whole byte `0x28` for CC Gain. `pre-consolidation:g2/analysis/bq27427-descriptor-binding-2026-10-09/REPORT.md`
9. IAR `__iar_zero_init3` underflows for lengths 1–3. `pre-consolidation:g2/analysis/iar-runtime-c-candidates-20261010-sol/REPORT.md`
10. The BL MRAM range check ignores address+size, and BL NOR read checks only the start address. `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/DEVICE-INFO-LAYOUT.md`, `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/CONTINUING-SOURCE.md`
11. `elog_output` silently drops ISR-context logs, and level ≥ 6 without a hook never returns. `pre-consolidation:g2/analysis/extended-log-policy-20261010/REPORT.md`
12. Stock audio power differs from pinned upstream in two places: CRYPTO uses index `0x17`, and SPOT failure is ignored. Stock UART also clears the active DMA-busy state, which pinned source does not. `pre-consolidation:g2/analysis/c-implementation-rounds-20261010/REPORT.md`

## 16. Open blockers and unknowns (as last stated)

- **IAR producer and build inputs.** The exact IAR producer (release, DLIB variant, options, ICF, link order) is unknown. IAR 10.10.2 cannot compile without a license token, and the stock candidate is still 9.60.2. `pre-consolidation:g2/analysis/tlsf-main-runtime-boundary-20261010-implementation/REPORT.md`, `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/TOOLING-INSTALL-RESULT.md`
- **EasyLogger output paths.**
  - The fatal callback target is unknown.
  - The 18 `%f` call sites cannot run: no available model executes FP64 at the stock address.
  - The 12 runtime-format producers are unresolved.

  `pre-consolidation:g2/analysis/extended-log-frontier-20261010/REPORT.md`
- **Product data with no source.**
  - FAL partition and device tables.
  - FlashDB DB rows.
  - Print buffer and sink initialisers.
  - Touch CapSense generated config (939 reset bytes).
  - EM9305 ARC QP/C port.
  - GX8002 `.config`.

  `pre-consolidation:g2/analysis/g2-product-source-final-discovery-20261010/REPORT.md`
- **Hardware behaviour not established.** None of these were shown: physical drain or quiescence for MSPI, IOM or CMDQ teardown; real delay timing; IRQ delivery; or power-domain status semantics. `pre-consolidation:g2/analysis/radio-iom-power-prepare-2026-10-05/external-boundary.md`
- **Bootloader.** These remain open:
  - the startup power root `0x41C4B4`
  - 18 callback targets
  - the ROM entries `0x0200FF21`, `0x41` and `0x49`
  - the SBL `[0x400000,0x410000)`, for which no backup exists

  Reading the SBL safely needs a non-reset, read-only debug attach. `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/integrated-status/remaining-providers-current.md`, `pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/READ-ONLY-ACQUISITION.md`
- **Lineage gaps.**
  - The Nema flag-clear block.
  - The TDK driver revision.
  - The exact private Cordio and HAL revisions; stock mixes SDK-5.2 Cordio behaviour with pre-5.2 IOM behaviour.

  `pre-consolidation:g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/LINEAGE-RESULT.md`, `pre-consolidation:g2/analysis/tdk-transport-independent-review-2026-10-09/REPORT.md`, `pre-consolidation:g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/REPORT.md`
