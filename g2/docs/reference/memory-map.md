# G2 memory maps by processor

This document records boundaries, owners, and notable fixed state for firmware
`s200_v2.2.6.10`. Per-function address rows are left to the pseudocode
corpus.

Citations are `path:line` at commit `832137ec`. Confidence:

- **Proven**: byte or hash evidence.
- **Strong**: independent structural evidence.
- **Inferred**: a consistent single line of evidence.
- **Unverified**: not checked.

Container formats are in [firmware-formats.md](firmware-formats.md).

## 1. System overview

| Processor | Core | Payload | Role |
|---|---|---|---|
| Ambiq Apollo510B (one per temple) | Arm Cortex-M55, FPU (and MVE-capable) | `apollo_bootloader` and `apollo_main` | main application, UI, BLE host, file systems |
| EM Microelectronic EM9305 | ARC EM (ARCv2 EM, "EM7D") | `ble_em9305` | BLE 5.4 controller over HCI |
| NationalChip GX8002 ("grus", board `grus_gx8002b_dev_1v`) | C-SKY CK804EF (ABIv2, hard float) plus gxNPU | `codec` | audio codec/DSP, KWS |
| Infineon PSoC 4000T CY8C4046FNI | Cortex-M0+ | `touch` | CapSense touch, I2C slave to Apollo |
| STM32G0B1-class (G0B0/G0B1/G0C1 not separable) | Cortex-M0+ | `case` | charging case |

Evidence for each processor:

- EM9305: `g2/docs/memory-map.md:1792-1795`.
- GX8002: `g2/docs/research/g2-codec-stage2-sections-recovery.md:22-23`;
  `g2/docs/research/peripheral-oss-library-provenance-audit.md:18,84-89`.
- PSoC 4000T: `g2/docs/research/g2-touch-identity-recovery.md:15-18`.
- STM32G0: `g2/docs/research/g2-box-stm32g0-platform-recovery.md:28-41`.

## 2. Apollo510B

### 2.1 Internal MRAM (per temple)

| Start | End (excl.) | Size | Owner | Conf. | Source |
|---:|---:|---:|---|---|---|
| `0x00400000` | `0x00410000` | 64 KiB | Ambiq secure bootloader (SBL). Not in EVENOTA; must not be overwritten | Proven (manifest policy) | `g2/docs/memory-map.md:27`; `g2/manifests/g2-2.2.6.10.json:250-259` |
| `0x00410000` | `0x00434477` | 148,599 B | Even bootloader image | Proven | `g2/manifests/g2-2.2.6.10.json:190-213`; `g2/docs/memory-map.md:250` |
| `0x00434477` | `0x00438000` | ≈15 KiB | bootloader-partition headroom (unused by stock) | Proven | `g2/docs/memory-map.md:250-308` |
| `0x00437FE0` | `0x00438000` | 32 B | main-image OTA preamble position (header only; never executed) | Strong | `g2/docs/memory-map.md:311-313` |
| `0x00438000` | `0x00794324` | 3,523,364 B | Even main application (raw image) | Proven | `g2/docs/memory-map.md:309`; `g2/tools/open_cfw.py:42` |
| `0x00794324` | `0x007FE000` | ≈433 KiB | free MRAM in stock | Proven (arithmetic) | `g2/docs/memory-map.md:1202-1208` |
| `0x007FE000` | `0x007FE010` | 16 B | bootloader-owned update flag/record; excluded from application images | Proven (manifest policy) | `g2/manifests/g2-2.2.6.10.json:260-266`; `g2/tools/open_cfw.py:43` |
| `0x007FE010` | `0x00800000` | ≈8 KiB | not characterised (end of 4 MiB MRAM) | Unverified | — |

Apollo-main image structure:

- **Vector table** at `0x00438000`:
  - initial SP `0x2007FB00`;
  - reset `0x005E4233`;
  - NMI `0x004397A7`;
  - HardFault `0x005B0115`.

  Confidence: Proven.
  Source: `g2/docs/research/g2-s200-config-main-recovery.md:52`.

- **Startup and runtime initialization.** Confidence: Strong.
  Source: `g2/docs/memory-map.md:1328-1336`.
  - Reset enters startup at `0x005E4294`.
  - The IAR-style scatter loader at `0x005E42B4` walks a table at
    `0x0075D3C8`.
  - One record decompresses a 22-byte stream at `0x0079430E` into ITCM
    starting at `0x00000040`, which holds the Ambiq three-cycle delay loop.
  - Main-image code therefore also executes from ITCM `0x00000000+`.

- **Discovered functions.** Ghidra finds 7,370 function entries, all in the
  first 34 of 64 equal chunks. From `0x00600FAA` onward the image is
  data/resources. Confidence: Strong.
  Source: `g2/docs/memory-map.md:311-317`.

- **Embedded source paths.** The image contains 357 embedded `__FILE__`
  paths rooted at `D:\01_workspace\s200_ap510b_iar_git\`:
  - 123 are third-party paths;
  - 234 are project paths.

  They anchor 1,760 functions. Confidence: Proven.
  Source: `g2/docs/research/apollo-embedded-source-path-census.md:8-26`.

### 2.2 SRAM / TCM

| Region | Evidence | Conf. |
|---|---|---|
| ITCM from `0x00000000` (runtime-copied code at `0x00000040`) | scatter record, `g2/docs/memory-map.md:1328-1333` | Strong |
| DTCM / low SRAM `0x20000000–0x2007FFFF` (main SP `0x2007FB00`; validator bound `0x2007FFFF`) | `g2/tools/open_cfw.py:771-774`; `g2-s200-config-main-recovery.md:52` | Strong |
| SSRAM from `0x20080000` (`SSRAM_BASEADDR`); main uses e.g. `0x200E99B4`, `0x2034DC30`, codec-DFU scratch `0x2035EE18` (8 KiB) | `g2/docs/memory-map.md:1350-1351`; `g2-codec-fwpk-segments-recovery.md:57-60` | Strong |

The SSRAM base is named in
`g2/docs/research/g2-bootloader-mspi-configure-424af0-424bd4-source-candidate.md`.

**Main-application fixed state.** These addresses are useful as pseudocode
naming seeds. All are Proven, meaning they are pinned by analyzers against the
authenticated image.

| Address | Object | Source |
|---:|---|---|
| `0x20074A20` | FreeRTOS `pxCurrentTCB` | `g2/docs/memory-map.md:1215` |
| `0x20074F14` | IAR DLIB `errno` | `g2/docs/research/iar-dlib-runtime-census.md:71-72` |
| `0x2007456C` | EasyLogger assertion-hook pointer | `g2/docs/memory-map.md:382-383` |
| `0x20070BE8` | EasyLogger logger object (`0xF8` B) | `g2/docs/upstream-inventory.md:844-845` |
| `0x2006BD30` | EasyLogger 1,024-byte output buffer | `g2/docs/upstream-inventory.md:840-841` |
| `0x20072AD8` / `0x20074578` / `0x20074570` | elog mutex control block (80 B), mutex handle, async event-flags handle | `g2/docs/upstream-inventory.md:858-860` |
| `0x200749C4` | TinyFrame instance, in a bookended allocation: `0xA5A5A5A5`, then a `0x7158`-byte core at `+4`, then `0x5A5A5A5A` at `+0x715C` | `g2/components/README.md:38-43` |
| `0x2005DFFC` | two FlashDB `fdb_kvdb` objects, stride `0x8AC` | `g2/docs/upstream-inventory.md:795-797` |
| `0x2006F600` | LVGL tick state | `g2/docs/memory-map.md:1367-1371` |
| `0x20066230` / `0x200744D4` | UI-module registry runtime copy (43 rows; flash table `0x006A44B0`) / count | `g2/docs/memory-map.md:1256-1258` |
| `0x20068228` / `0x20068928` | GPIO handler table (14×32 pointers) / callback arguments | `g2/docs/memory-map.md:1258-1260` |
| `0x20075024` | lens-side byte: 1 = left/other, 2 = right. Sampled 5× from GPIO `0x9C` | `g2/components/apollo_main/core_overlay/EVIDENCE.md:37,53-66` |
| `0x2004FA98` / `0x2004FAC8–0x200523C8` | Cordio WSF buffer pool descriptors / pools (8×16, 4×32, 10×64, 20×480) | `g2/docs/memory-map.md:365-372` |
| `0x20075045`, `0x20074EF0`, `0x20073230` | WSF critical-section nesting byte, event group, WSF task | `g2/docs/memory-map.md:355-361` |
| `0x200708EC` (0x100 B) | Cordio SMP DB: 10×24-byte records plus a timer | `g2/docs/memory-map.md:402-409` |
| `0x200712A4` (196 B) | Cordio `dmConnCb`: 3 CCBs | `g2/docs/memory-map.md:447-453` |
| `0x20073394` / `0x20073B78` | `dmAdvCb` / `dmCb` | `g2/docs/memory-map.md:433-442` |
| `0x200004B8` | `pSmpCfg` pointer | `g2/docs/memory-map.md:407-409` |

FreeRTOS heap: `configTOTAL_HEAP_SIZE = 0x2F000`, using `heap_4`
(`g2/docs/research/freertos-g2-config-port-audit.md:220`). The heap base
address is not recorded here.

### 2.3 Bootloader SRAM

The bootloader state is distinct from main. Confidence: Proven.

| Address | Object |
|---:|---|
| `0x20026700` / `0x200270E4` | EasyLogger logger object / assertion hook |
| `0x200270D4` | event-flags handle literal |
| `0x200271C5` | MSPI-guard bypass byte |
| `0x20000518` | thread-pointer anchor returned by the IAR TLS leaf |

Sources: `g2/docs/upstream-inventory.md:912-913`, `g2/docs/memory-map.md:107,4371-4377`,
`g2/docs/upstream-inventory.md:43`.

### 2.4 External memory (MSPI1 NOR, MX25U25643G, 32 MiB)

The transport is AmbiqSuite 5.1.0 MSPI:

- MSPI1/CE0, SPI mode 0, 96 MHz;
- IRQ 21, priority 4.

The main application maps the device as a read-only 32 MiB XIP window at
`0x80000000`. Bootloader erase uses 4 KiB sectors with a 32 MiB bound; program
uses 256-byte pages.

Sources: `g2/docs/upstream-inventory.md:414-418`; bootloader rows
`g2/docs/upstream-inventory.md:59-60`. Confidence: Strong.

| NOR offset | End (excl.) | Size | Owner | Source |
|---:|---:|---:|---|---|
| `0x00000000` | `0x01400000` | 20 MiB | not characterised (resources, staged images, other) | Unverified |
| `0x01400000` | `0x01FC0000` | 3,008 × 4 KiB | littlefs v2.10.1 (both main and bootloader) | `g2/docs/upstream-inventory.md:386-392` |
| `0x01FC0000` | `0x01FF8000` | 224 KiB | FlashDB FAL partition `kvdb` (database `sysenv`) | `g2/docs/research/flashdb-configuration-recovery-audit.md:154-162` |
| `0x01FF8000` | `0x02000000` | 32 KiB | FlashDB FAL partition `NVdb` (database `factory`) | same |

littlefs geometry (Proven; `g2/docs/upstream-inventory.md:327-352`):

| Parameter | Value |
|---|---|
| read size | 16 |
| program size | 256 |
| block size | 4096 |
| block count | 3008 |
| block cycles | 500 |
| cache size | 4096 |
| lookahead size | 256 |

Both images use the same geometry. The `lfs_config` structures are at
`0x006E83A4` (main) and `0x00431070` (bootloader).

The FlashDB `fal_flash_dev "norflash"` is `{addr 0x01FC0000, len 0x02000000,
blk 0x1000, write_gran 1}` at `0x00722B30`. Confidence: Proven.

## 3. Apollo bootloader layout

The bootloader is a raw image at `0x00410000`
(`g2/docs/memory-map.md:28-250`). It contains:

- AmbiqSuite 5.1.0 MSPI HAL;
- the MX25U25643G driver;
- littlefs 2.10.1;
- EasyLogger;
- TLSF;
- a CMSIS-RTOS2-style RTOS;
- the DFU service task.

Documented anchors (Proven):

| Range / address | Function | Source |
|---|---|---|
| `0x00415128–0x0041531C` | littlefs public API subset | `g2/docs/upstream-inventory.md:377-378` |
| `0x0041F9D8–0x0041FA40` | boot initializer/delay services | `g2/docs/upstream-inventory.md:35` |
| `0x00420002–0x00420F70` | MX25U25643G driver (timing scan, JEDEC, erase, program, quad/4-byte modes) | `g2/docs/upstream-inventory.md:46-60` |
| `0x004212D8–0x004213D8` | littlefs block callbacks | `g2/docs/memory-map.md:3996-4058` |
| `0x0042DE58–0x0042E104` | DFU service task: header, CRC, program, handoff to `0x00438000` | `g2-bootloader-dfu-service-task-42de58-source-closure.md:1-19` |
| `0x00430000–0x004301D6` | platform bring-up | `g2-bootloader-platform-bringup-430000-source-closure.md:1-3` |

## 4. EM9305

Sources: `g2/docs/memory-map.md:1778-1886`;
`g2/manifests/g2-2.2.6.10.json:55-116`.

| Address | Size | Content | Conf. |
|---:|---:|---|---|
| `0x00300000` | 224 B | record 0 | Proven |
| `0x00300400` | 656 B | record 1 | Proven |
| `0x00302000` | 56 B | FHDR image descriptor; entry point `0x00302028` | Proven |
| `0x00302400–0x00335BC7` | 210,888 B | application: vector table, QK port at `0x00302518`, QP/C cluster `0x00310D18–0x003117EB`, controller and vendor code, tail tables | Proven |

Anchors in the application record (Proven; `g2/docs/memory-map.md:1845-1872`):

- `BOOT_BootUp @ 0x00302AE8`;
- `wsfDispatcherThread @ 0x00333C44`;
- ARC IRQ entries begin at vector word 16. IRQ 0/1 are the ARC timers and
  IRQ 20/21 are radio TX/RX (`0x00306440`/`0x00306384`).

RAM lies in the `0x0080xxxx` data region:

- QP callback globals at `0x0080FE04–0x0080FE1F`
  (`g2/docs/memory-map.md:1827-1828`);
- `QK_attr_` at `0x00801394`;
- linker-provided stack limits `0x0080E978`/`0x0080F978`
  (`g2/docs/research/em9305-residual-provenance-audit.md:139`).

Confidence: Strong. ROM and full RAM extents are Unverified.

## 5. GX8002 codec

Sources: `g2/docs/research/g2-codec-fwpk-segments-recovery.md:43-52,99-103`;
`g2/docs/research/g2-codec-stage2-sections-recovery.md:44-95`.

| Region | Address | Use | Conf. |
|---|---|---|---|
| MCU IRAM | `0x10000000` | UART boot stage 1 (`0x10000000`, entry `+0x100`) and stage 2 (`0x10002800`, entry `0x10002900`); BINH stage-1 block (12 KiB) | Strong |
| NPU SRAM reservation | `[0x10000000, 0x10023400)` in image A | gxNPU working memory (`NPU_SRAM_SIZE = 0x23400`) | Strong |
| App SRAM text/data (image A) | `[0x10023400, 0x10026D7C)` | entry `0x10023500`; text to `0x100264E4`, data from `0x100264E8` | Proven |
| App SRAM (image B) | `[0x10003000, 0x1001708C)` | backup firmware, entry `0x10003100` | Proven |
| DRAM | `0x20000000` | UART stage-2 BSS `[0x2000953C, 0x2000A1FC)`; KWS staging `0x20003304` (commands), `0x200056D0` (weights); stacks `0x2002F7FC` (A), `0x2002FFFC` (B) | Strong |
| Flash XIP | `0x10200000` (public SDK default) | image-A XIP text (36,484 B) | Inferred |
| External SPI NOR | offsets `[0x0, 0x46440)` | dual BINH image; 512 KiB geometry assumed | Strong (offset), Inferred (geometry) |

## 6. Touch: PSoC 4000T

Sources: `g2/docs/memory-map.md:1888-1894`;
`g2/docs/research/g2-touch-identity-recovery.md:15-18,33-44,78-100`.

The part has 64 KiB flash at `0x00000000` and 8 KiB SRAM at `0x20000000`.
The initial SP is `0x20002000` (the top of SRAM) and reset is `0x00004675`.

**Link base `0x3300`** (Proven, 2026-09-29). The application payload is linked
at flash `0x00003300`, above a resident region that holds the bootloader.
Payload offset `+0x3300` is the flash address. Evidence:
- The reset vector `0x4675` is the recovered reset entry at payload
  `+0x1375`.
- A Ghidra 12.1.4 export at base `0x3300` places 276 of the 291 named
  function seeds exactly on discovered entries. Base 0 misplaces them.

An earlier record assumed base 0; the offsets below are payload offsets.

Payload regions (payload offsets; add `0x3300` for flash addresses):

| Interval | Region |
|---|---|
| `[0x0000, 0x00C0)` | vectors: 48 slots, 13 IRQs, all on the default handler `0x465D` |
| `[0x00C0, 0x775C)` | code |
| `[0x775C, 0x7DC4)` | EasyLogger strings; firmware version `2.2.0.1` |
| `[0x7DC4, 0x8650)` | tuning and config tables |
| `[0x8650, 0x867C)` | `FF` padding |
| `[0x867C, 0x8680)` | trailing CRC-32C |

A resident region beyond the payload holds the RX dispatch table at `0xB0C4`
(`g2-touch-identity-recovery.md:124-128`); its extent is Unverified.

Peripheral bases used:

| Block | Base |
|---|---|
| SCB1 (I2C to host) | `0x40250000` |
| MSCLP0 (CapSense) | `0x40290000` |
| CPUSS | `0x40100000` |
| GPIO PRT2–4 | `0x40040200`–`0x40040400` |

## 7. Case: STM32G0 dual bank

Sources: `g2/docs/memory-map.md:1754-1776`;
`g2/docs/research/g2-box-stm32g0-platform-recovery.md:41-60,64-86` (SP at l.49);
`g2/blobs/official/case-backup-2026-08-09/PROVENANCE.md:27-44`.

| Logical range | Content |
|---|---|
| `0x08000000–0x08040000` | active 256 KiB bank; application `0x08000000–0x0800D9C8` |
| `0x08040000–0x08080000` | inactive bank (install target; same image aliases at `0x08040000`) |
| `0x0803F000+16`, `0x0803F800+8` | bank-1 device data (preserve) |
| `0x0807F000+16`, `0x0807F800+8` | bank-2 device data (preserve) |
| `0x1FFF7800` | option bytes (128 B), including `nSWAP_BANK` |

Update procedure:

1. erase 128 × 2 KiB pages in the inactive bank;
2. program 8-byte doublewords;
3. verify the additive sum;
4. toggle `nSWAP_BANK`.

Confidence: Proven.

Startup and RAM facts. Confidence: Strong for layout; the RAM budget is
Unverified.

- Initial SP `0x20002C88`.
- Reset trampoline `0x08000144`, then `SystemInit` at `0x080084AE`, then
  `_start` at `0x080000B8`.
- FreeRTOS kernel statics at `0x20000128`; `pxCurrentTCB` is the literal.
- Data reaches `0x2000FC1C`, so at least 64 KiB of RAM is in use (the part
  has 144 KiB nominal).
- The USART3/USART4 bases `0x40004800`/`0x40004C00` are present.
