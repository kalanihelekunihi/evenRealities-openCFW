# R1 memory map (stock 2.2.6.0009, nRF52840)

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


Target: nRF52840 QIAA (1 MiB flash, 256 KiB RAM, Cortex-M4F), MBR + S140 7.2.0, application
2.2.6.0009, nRF5 SDK 17.1.0 secure BLE bootloader.

Confidence tags: **Proven** means byte- or hash-pinned in the image or a live dump. **Strong** means
several independent recovered facts agree. **Inferred** is a derived value. **Unverified** is a
claim or placeholder with no image evidence. Columns headed "Source" cite the original repository
path and line, relative to the repository root.

Two kinds of value appear below and must not be mixed up. Stock values come from the image. openR1
values were design choices of the deleted clean-room build. They are listed only so readers can
recognise them in older material.

## 1. Rebuild oracle (the byte-equality target)

The oracle is `r1/research/decompilation/rebuild/` (kept). `manifest.json` pins four supplied
images. `emit_image.c` re-emits them from locally supplied `*.bytes.inc` arrays, which are not
tracked. `verify.py` then checks size and SHA-256. This is a hash oracle, not a source
reconstruction.

| Image | Load address | Bytes | SHA-256 | Tag | Source |
|---|---|---:|---|---|---|
| application 2.2.6.0009 (OTA payload) | `0x00027000` | 646,408 | `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a` | Proven | `r1/research/decompilation/rebuild/manifest.json:4-9`; `r1/research/decompilation/artifact-inventory.csv:2` |
| bootloader (live 24 KiB span) | `0x000F8000` | 24,576 | `566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b` | Proven | `manifest.json:16-21`; `artifact-inventory.csv:3` |
| UICR (live partial snapshot) | `0x10001000` | 776 (`0x308`) | `1a6dc7725aa1903ed240dd245ecd036a6c72b244e8b26179affdd0fdde74b150` | Proven | `manifest.json:22-27`; `artifact-inventory.csv:4` |
| APPROTECT runtime words | mixed registers | 12 | `fafdd44c03daf5f7ecfa57113ebd319de6fb8f84fa0b7b0c5ac60d09f811fb71` | Proven | `manifest.json:10-15`; `artifact-inventory.csv:5` |
| S140 7.2.0 SoftDevice hex (SDK copy) | `0x00000000..` | n/a | `c52b61a6ceeb58438dbef075abfc5f6812718dda78630b39e82a20829f09c125` | Proven (file pin) | `third-party/fetched/manifest.json` component `nordic-s140` |

Notes:
- Original source file names were `firmware/analysis/r1-2.2.6.0009/application.bin` and
  `firmware/analysis/r1-live-2026-08-10/r1-{bootloader,uicr,approtect-runtime}-live.bin`
  (`manifest.json:8,14,20,26`).
- Array format for `*.bytes.inc`: 16 bytes per line, `0x%02x, ` (`rebuild/PROVENANCE.md:43-46`).
- The signed OTA init packet and package signature are not in the corpus. The bootloader span
  necessarily contains the public key (`r1/research/decompilation/README.md:104-109`).
- No MBR/S140 bytes, gap/private flash, MBR parameter page or settings page are in the corpus.
  A full-device image therefore cannot be synthesized from it (`research/decompilation/README.md:37-39`).
- The SoftDevice required by the signed init packet is S140 7.2.0, FWID `0x0100`
  (`research/decompilation/README.md:28`). Tag: Proven.
- A later owned-ring capture read all 216 live pages `0x27000..<0xFF000` plus the 0x308-byte
  UICR. That capture was on a unit running 2.2.8.0002 and is not part of the oracle
  (`r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md:42-45`).

## 2. Flash layout (1 MiB)

| Range | Size | Pages | Owner | Tag | Source |
|---|---:|---:|---|---|---|
| `0x00000000..0x00000FFF` | 4 KiB | 1 | MBR (part of the S140 hex). MBR config words at `0xFF8` (bootloader addr) and `0xFFC` (param page addr) are programmed by the retail bootloader | Strong | `r1/tools/probes/r1_228_mbr_config_dump.S:1-10` |
| `0x00001000..0x00026FFF` | 152 KiB | 38 | S140 7.2.0 | Proven (FWID) | `research/decompilation/README.md:28` |
| `0x00027000..0x000C4D07` | 646,408 B | – | Application 2.2.6.0009 image (logical end) | Proven | `artifact-inventory.csv:2` |
| `0x000C4D08..0x000D0FFF` | – | – | Application-aligned tail / DFU bank space. Contents not captured | Inferred | `research/decompilation/README.md:30` |
| `0x000D1000..0x000D3FFF` | 12 KiB | 3 | Nordic FDS (Peer Manager bonds): 2 data pages + 1 swap page on a live unit | Proven | `r1/docs/correlation/INTERNAL-FLASH-CORRELATION.md:23-35`; `AUGUST-18-PHYSICAL-VALIDATION-BLOCKER.md:37-41` |
| `0x000D4000..0x000F7FFF` | 144 KiB | 36 | `device_flash` FAL region (7 partitions, section 3) | Proven | `INTERNAL-FLASH-CORRELATION.md:27` |
| `0x000F8000..0x000FDFFF` | 24 KiB | 6 | Secure bootloader (logical image 24,420 B = `0x5F64`, ends `0x000FDF64`, then 156 B of `0xFF`) | Proven | `r1/research/bootloader-reconstruction/README.md:16-17`; `MEMORY-MAP.md:14` |
| `0x000FE000..0x000FEFFF` | 4 KiB | 1 | MBR parameter page / settings backup (ACL-protected) | Proven | `research/bootloader-reconstruction/MEMORY-MAP.md:28-29` |
| `0x000FF000..0x000FFFFF` | 4 KiB | 1 | Bootloader settings, primary and writable | Proven | `MEMORY-MAP.md:30` |

Derivations:
- Stock `fds_init` at `0x00063EB8` subtracts `0x24000` from the bootloader boundary, then
  `0x3000` for its three pages. This is the compiled form of `FDS_VIRTUAL_PAGES_RESERVED = 36`.
  The body SHA-256 is `9fa3e325b3955765dcda42a277d30292ba377611d54ef89d2a5032b71695abd7`
  (`INTERNAL-FLASH-CORRELATION.md:31-35`; `r1/docs/correlation/NORDIC-SDK-CORRELATION.md:463-466`). Tag: Proven.
- The `device_flash` adapter reads `FICR.CODEPAGESIZE`, `FICR.CODESIZE` and `UICR.NRFFW[0]`. It
  assigns the 36 pages just below the bootloader. If `NRFFW[0]` is erased it falls back to
  `CODEPAGESIZE*CODESIZE` (`INTERNAL-FLASH-CORRELATION.md:5-8,37-40`). Tag: Proven.
- The bootloader reserves the same 36 pages as app data (`NRF_DFU_APP_DATA_AREA_SIZE = 36*4096`).
  This is the retail two-byte delta at `0xFB54E` from the SDK example
  (`r1/research/bootloader-reconstruction/sdk-overlay/r1_sdk_overrides.h:17-19`). Tag: Proven.
- The maximum application link region is `0x27000..<0xD1000` (170 pages). This limit comes from the
  layout, not from a stock linker file. The stock scatter file is unknown (`INTERNAL-FLASH-CORRELATION.md:25`). Tag: Inferred.

## 3. FAL partitions (`device_flash`, base `0x000D4000`)

All seven entries carry magic `0x45503130` (`"01PE"` little-endian). The embedded FAL version
string is `0.5.99`.

| Name | Offset | Length | Absolute range | Format owner | Tag | Source |
|---|---:|---:|---|---|---|---|
| `kv.bin` | `0x00000` | `0x02000` | `0xD4000..0xD5FFF` | R1 fixed-class store | Proven | `r1/port/fal_cfg.h:13`; `r1/src/r1_storage.c:8` |
| `health.db` | `0x02000` | `0x06000` | `0xD6000..0xDBFFF` | FlashDB 2.0.0 TSDB | Proven | `fal_cfg.h:14` |
| `sleep.db` | `0x08000` | `0x02000` | `0xDC000..0xDDFFF` | R1 circular journal | Proven | `fal_cfg.h:15` |
| `pKey.bin` | `0x0A000` | `0x01000` | `0xDE000..0xDEFFF` | GoMore key / prior-state | Proven | `fal_cfg.h:16` |
| `reserve` | `0x0B000` | `0x0B000` | `0xDF000..0xE9FFF` | unused / unknown | Proven (entry) | `fal_cfg.h:17` |
| `ep.bin` | `0x16000` | `0x02000` | `0xEA000..0xEBFFF` | 1,024 x 8-byte records | Proven | `fal_cfg.h:18` |
| `log.bin` | `0x18000` | `0x0C000` | `0xEC000..0xF7FFF` | 12-sector circular log | Proven | `fal_cfg.h:19` |

Stock anchors:
- FAL initializer `0x00062F40` embeds `0.5.99` (`r1/docs/correlation/FLASHDB-FAL-CORRELATION.md:24`).
- Storage adapter descriptor `0x20006F98`, operations table `0x20006FC4`, ten adapter functions
  `0x00054970..0x00071054` (`INTERNAL-FLASH-CORRELATION.md:47-62`).
- Formats are covered in `storage-formats.md`.

## 4. UICR

| Field | Value | Tag | Source |
|---|---|---|---|
| `NRFFW[0]` (`0x10001014`), bootloader address | `0x000F8000` | Proven | `INTERNAL-FLASH-CORRELATION.md:18-20` |
| `NRFFW[1]` (`0x10001018`), MBR param page | `0x000FE000` | Proven | same; `sdk-overlay/README.md:14` |
| PSELRESET | pin reset on P0.18. The app is built with `CONFIG_GPIO_AS_PINRESET`, and `SystemInit` programs it | Strong | `r1/docs/correlation/NORDIC-SYSTEM-INIT-CORRELATION.md:49-53` |
| NFCPINS | converted to GPIO (`CONFIG_NFCT_PINS_AS_GPIOS`) | Strong | same |
| APPROTECT / DEBUGCTRL | the tested legacy ring had physical debug protection disabled. Exact word values are only in the uncommitted snapshot | Strong | `research/bootloader-reconstruction/SECURITY-MODEL.md:33-37`; `r1/tools/probes/r1_227_uicr_dump.S:1-7` |

## 5. RAM

| Item | Value | Tag | Source |
|---|---|---|---|
| Application RAM origin (S140 `sd_ble_enable` RAM start) | `0x200064A8` | Proven | `r1/docs/reference/r1-capability-matrix.csv:201` (R1-200); `r1/docs/README.md:694` |
| RAM end | `0x20040000` | Proven (device) | nRF52840 architecture |
| Scatter-loaded application records seen (examples) | storage descriptor `0x20006F98`; TWI records `0x20006FF4`/`0x20007060`; software TWI `0x20007400 + n*0x70`; GPIO input registry `0x200070C0`; ADC records `0x20006EF8`; watchdog `0x20007630`; `device_stacmd` ops `0x20007614`; EUS module table `0x20006B90` | Proven | `r1/docs/correlation/BUS-REGISTRATION-CORRELATION.md:25-35`; `GPIO-INPUT-IRQ-DISPATCH-CORRELATION.md:11-12`; `r1-capability-matrix.csv:83`; `WATCHDOG-DEVICE-CORRELATION.md:32`; `r1/docs/PROVENANCE.md:15` |
| FreeRTOS static idle task | TCB `0x2002B4D0`, stack `0x2002B540` (256 words) | Proven | `r1/docs/correlation/FREERTOS-STATIC-MEMORY-CORRELATION.md:10` |
| FreeRTOS static timer task | TCB `0x2002B940`, stack `0x2002B9B0` (256 words) | Proven | same `:11` |
| Legacy-command workspace (36 B) | `0x2001A174` | Proven | `r1/docs/correlation/LEGACY-COMMAND-DISPATCH-CORRELATION.md:14-16` |
| Connection-state module | `0x2002BDB0..0x2002BDC8` accessors | Proven | `NORDIC-SDK-CORRELATION.md:394-396` |
| RW data initialisation | armlink `__scatterload` + `__scatterload_decompress` (compressed RW) | Proven | `r1/docs/correlation/TOOLCHAIN-RUNTIME-CORRELATION.md:47-48` |

Bootloader RAM:

| Region | Start | End (excl.) | Bytes | Tag | Source |
|---|---|---|---:|---|---|
| `.data` (load `0x000FDE9C`, length `0xC8`) | `0x20005978` | `0x20005A40` | 200 | Proven | `research/bootloader-reconstruction/MEMORY-MAP.md:20` |
| `.bss` (zero length `0x7560`) | `0x20005A40` | `0x2000CFA0` | 30,048 | Proven | `MEMORY-MAP.md:21` |
| Initial MSP (vector word 0) | `0x2000CFA0` | – | – | Proven | `MEMORY-MAP.md:22` |

## 6. Bootloader image layout

| Start | End incl. | Bytes | Content | Source |
|---|---|---:|---|---|
| `0x000F8000` | `0x000F80FF` | 256 | 64-word vector table | `MEMORY-MAP.md:7` |
| `0x000F8100` | `0x000F81FF` | 256 | zero-filled | `:8` |
| `0x000F8200` | `0x000FD867` | 22,120 | Thumb code, literal pools, tables | `:9` |
| `0x000FD868` | `0x000FD8A7` | 64 | **DFU public key**, raw P-256 `X‖Y`, little-endian | `:10` |
| `0x000FD8A8` | `0x000FDE1B` | 1,396 | constants, pointer tables, crypto constants, leaf helpers | `:11` |
| `0x000FDE1C` | `0x000FDE9B` | 128 | scatter-load / BSS-zero / init records | `:12` |
| `0x000FDE9C` | `0x000FDF63` | 200 | `.data` load image | `:13` |
| `0x000FDF64` | `0x000FDFFF` | 156 | erased `0xFF` | `:14` |

Other fixed bootloader constants:
- `nrf_clock_lf_cfg_t` bytes `00 10 02 01` at `0x000FDC68`: LFRC, 16 x 0.25 s calibration,
  temperature interval 2, 500 ppm (`r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md:30-35`). Tag: Proven.
- Handoff ACL write-protects `0xF8000..0xFEFFF` and flash `0..` the page-aligned application end
  (`SECURITY-MODEL.md:18-19`; `MEMORY-MAP.md:28`). Tag: Proven.
- Public key bytes (`9d 11 56 44 ... 42 34 55`) are in `config-recovered/r1_dfu_public_key.c`,
  a copy of `r1/research/bootloader-reconstruction/sdk-overlay/r1_dfu_public_key.c:13-22`. Tag: Proven.

## 7. Values that are openR1 choices, not stock

| openR1 value | Where | Status |
|---|---|---|
| GCC linker `FLASH ORIGIN 0x27000 LENGTH 0xAA000`, `RAM ORIGIN 0x200064A8 LENGTH 0x39B58` | `r1/platform/nrf52840/sdk/openr1_sdk.ld:7-8` | Origins match stock; lengths are openR1 limits. Stock uses an armlink scatter file whose contents are unknown |
| `.openr1_*` retention sections, `KEEP` of reconstructed modules | `openr1_sdk.ld:21-117` | openR1 only; not stock |
| `__STACK_SIZE=8192`, `__HEAP_SIZE=0` | `r1/platform/nrf52840/sdk/Makefile:303` | openR1 choice; stock MSP/stack size not recovered |
| Zephyr partitions `mcuboot 0..0x27000`, `openr1-settings 0xD1000`, `openr1-data 0xD4000`, `retail-boot-migration-reserve 0xF8000` | `r1/platform/nrf52840/zephyr/boards/openr1/openr1_nrf52840/openr1_nrf52840.dts:125-155` | openR1 replacement runtime only. Only the `0xD4000/0x24000` data window mirrors stock |
| Bootloader GCC rebuild: MSP `0x20040000`, key at `0x000FDA44` | `firmware-project/verification/reproducibility.json:14-15` | GCC reference build; differs from stock `0x2000CFA0` / `0x000FD868` |

## 8. Open questions

- The stock application scatter file is unknown. Needed: execution/load regions, RW compression,
  ZI limit, and stack/heap placement.
- The contents of `0xC4D08..0xD0FFF` and of the `reserve` partition were not captured in the
  oracle.
- The settings page (`0xFF000`) and MBR param page (`0xFE000`) bytes are not in the oracle. Only
  their layout (SDK 17.1.0) is known.
