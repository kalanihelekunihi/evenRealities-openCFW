# G2 touch-controller identity and memory-map recovery

Status: complete, device-free static analysis over the authenticated
`firmware_touch.bin` blob (FWPK type 3, `/firmware/touch.bin`). This is
analysis only; no device, flash, or hardware access was performed. The blob
remains a proprietary compatibility input; nothing here grants source or
license ownership.

Input: `blobs/official/g2-2.2.6.10/firmware_touch.bin`, 34,464 bytes, SHA-256
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`
(matches `blobs/official/g2-2.2.6.10/PROVENANCE.md`).

## Identity verdict

**The touch controller is an Infineon/Cypress PSoC 4000T, ordering part
CY8C4046FNI: ARM Cortex-M0+ (ARMv6-M), 64 KiB flash, 8 KiB SRAM, 48 MHz,
fifth-generation CapSense multi-sense converter (MSCLP), two SCBs, two
TCPWMs.** Confidence: high at family level; high at OPN level.

### Corroborating evidence

1. **Retained host-driver path.** The Apollo image contains the closed
   first-party translation unit `driver\touch\drv_cy8c4046fni.c`
   (`docs/research/g2-drv-cy8c4046fni-dependency-boundary.md`), naming the
   exact controller part in binary-resident path text.
2. **Vendor part data.** Infineon lists `CY8C4046FNI-T412T/T442T/T452T` as
   PSoC 4000T: Cortex-M0+, 64 kByte flash, 8 kByte SRAM, CapSense, 2 SCB,
   2 TCPWM, WLCSP-25/QFN packages. (Vendor catalog lookup, this audit.)
3. **SRAM size.** The image's initial stack pointer is `0x20002000`, the top
   of an 8 KiB SRAM at `0x20000000`. This excludes every PSoC 4 candidate
   with 4 KiB or less SRAM (4000, 4000S, 4100S) and matches 4000T exactly.
4. **ARMv6-M vector-table shape.** Reserved core slots 4–10 and 12–13 are
   zero; SVC/PendSV/SysTick and all thirteen external IRQ slots point to one
   default handler `0x0000465D`; HardFault is `0x0000465F`; reset is
   `0x00004675`. The thirteen populated external slots equal the PSoC 4000T
   NVIC count in Infineon's `psoc4000t.svd` (ioss 0–4, srss_wdt, scb0, scb1,
   msclp_lp, spcif, msclp, tcpwm0, tcpwm1). All-default vectors indicate a
   fully polled design (inferred).
5. **Peripheral register constants.** Every LDR-confirmed peripheral base in
   the code region is an exact PSoC 4000T SVD block base, and no out-of-map
   peripheral constant exists: PERI `0x40010000`, SRSSLT `0x40030000`, GPIO
   PRT2/3/4 `0x40040200/0300/0400` (0x100 port stride), CPUSS `0x40100000`,
   SCB1 `0x40250000` (I2C to the host), and MSCLP0 `0x40290000` — the
   fifth-generation CapSense block that exists only in PSoC 4000T.
   HSIOM `0x40020080/0x40020100` and CPUSS+8 (SYSARG) `0x40100008` appear as
   inferred pool constants. Apparent `0x40030018/1C/20` and other
   `0x40xxxxxx` aligned words decode as Thumb instruction pairs
   (`movs`/`ands`/`ldr` halfwords), not peripheral constants; they are
   recorded as census artifacts, not evidence.
6. **SROM syscall idiom.** The function at `0x58F4` reads CPUSS SYSARG
   (`[CPUSS,#8]`), masks the top nibble, compares against the
   `0xA.......`/`0xF.......` status classes, and dispatches through a
   20-entry GCC switch (`lsls #2; ldr r3,[r3,r2]; mov pc,r3`). This is the
   canonical PSoC 4 flash/SROM system-call status decoder, required for
   self-programming (DFU and EEPROM emulation).
7. **Toolchain/SDK lineage.** GCC/newlib startup idiom (init-array
   iterators at `0x00C0`), GCC `mov pc,r3` switch idiom, and EasyLogger
   format strings with the same color-prefix/`%s` convention used by the
   Apollo-side firmware. Firmware version string `2.2.0.1` with `TP VER:%s`
   log. ModusToolbox/PDL versus bare-metal provenance is unresolved (gate
   below).

### Candidate exclusion ledger

| Candidate | Verdict | Discriminating evidence |
| --- | --- | --- |
| PSoC 4000T CY8C4046FNI | **Proven** | all evidence above |
| PSoC 4000S CY8C4045/46 | Excluded | Cortex-M0 (not M0+); 32 KiB flash < 34,428-byte programmed length; 4 KiB SRAM (ISP would be `0x20001000`); CSD CapSense, no MSCLP at `0x40290000` |
| PSoC 4000/4000S smaller parts | Excluded | ≤16–32 KiB flash, ≤4 KiB SRAM; image exceeds both |
| PSoC 4100S / 4100S Plus | Excluded | 32-slot NVIC (13 here); CSD/CSDv2 block at different base; host-driver path mismatch |
| Goodix / FocalTech / Hynitron / Chipone / Zinitix / Ilitek touch ICs | Excluded | proprietary or 8051/RISC-V cores with vendor register maps; none exposes a byte-exact PSoC 4000T SVD peripheral map or the PSoC SROM syscall idiom; contradicts the retained `drv_cy8c4046fni.c` path |
| Atmel/Microchip maXTouch | Excluded | AVR32/proprietary cores and object-protocol report memory; no matching structures |
| Generic Cortex-M0+ MCU (STM32L0/nRF51/EFM32 class) | Excluded | peripheral constants all land inside the PSoC 4 MMIO map with exact SVD block bases; MSCLP0 `0x40290000` exists in no other family; NVIC count 13 |

## Memory map (flash-linear payload, base `0x00000000`)

The 32-byte FWPK wrapper carries a 34,432-byte (`0x8680`) flash-linear
payload. Per `g2-service-touch-dfu-recovery.md` the programmed length is the
record size minus four (`0x867C` = 34,428 bytes); the final word is a
reflected CRC-32C of all preceding payload bytes. Both CRC-32C
relationships were verified against the ARMv8 CRC32CB hardware instruction
(record CRC `0x48674BC7`, trailing CRC `0xF75CF6F4`).

| Region | Interval | Size | Class | Status |
| --- | --- | ---: | --- | --- |
| vectors | `[0x0000,0x00C0)` | 192 | ARMv6-M vector table, 48 slots, 13 external IRQs | confirmed |
| code | `[0x00C0,0x775C)` | 30,364 | Thumb code + embedded literal pools | confirmed |
| strings | `[0x775C,0x7DC4)` | 1,640 | EasyLogger log strings, version `2.2.0.1` | confirmed |
| const_tables_a | `[0x7DC4,0x8110)` | 844 | nine uint32 tuning constants (0x370E–0x384C) at `0x7DC4`; runtime descriptors | inferred |
| zero_gap_1 | `[0x8110,0x8120)` | 16 | zero fill | confirmed |
| const_tables_b | `[0x8120,0x8430)` | 784 | configuration tables with SRAM descriptors; likely MSC tuning | inferred |
| zero_gap_2 | `[0x8430,0x85D0)` | 416 | zero fill | confirmed |
| config_block | `[0x85D0,0x8650)` | 128 | config descriptor referencing MSCLP0/GPIO PRT4; one flash row | inferred |
| ff_pad | `[0x8650,0x867C)` | 44 | erased-flash pad | confirmed |
| trailing_crc | `[0x867C,0x8680)` | 4 | reflected CRC-32C of `payload[0:0x867C]` | confirmed |

Per-region SHA-256 pins live in
`tools/manifests/g2-touch-identity-regions.tsv` and are enforced by the
analyzer. SRAM: stack top `0x20002000`; 140 pointer-like words span
`0x20000000`–`0x200018E4` (plausible static data `0x20000400`+), so static
allocation reaches at least ~6.2 KiB of 8 KiB (inferred). NVIC: all
thirteen external vectors point to the shared default handler `0x465D`
(polled design, inferred).

## Update transport and container framing

Host side (closed in `g2-service-touch-dfu-recovery.md`, not re-derived
here): frames are `0x01 | cmd | len16le | payload ≤ 32 B | cksum16 | 0x17`
with commands `0x38` enter-DFU, `0x4C` set-app-metadata, `0x37` 32-byte
packet, `0x49` program 128-byte block, `0x31` verify-app, `0x3B` exit-DFU;
the application length is rounded to 128-byte blocks. The 128-byte program
granularity matches the PSoC 4 flash row size.

New device-side facts from this audit:

- **Container.** FWPK 16-byte header (`FWPK`, field@0x04 = `0x02020001`
  observed/unresolved, version 1, flags 0) + one 16-byte record
  (type 3, size `0x8680`, offset `0x20`, reflected CRC-32C `0x48674BC7`
  over the payload).
- **Self-checksum.** The payload's final word is a reflected CRC-32C over
  all preceding payload bytes (`0xF75CF6F4`), consistent with the
  host-side verify-app step; the programmed length excludes it.
- **Self-programming capability.** The SROM syscall status decoder at
  `0x58F4` and SYSARG pool constant `0x40100008` prove the firmware
  performs PSoC 4 flash system calls on-device.
- **Dispatch candidate (superseded).** The nine words at `0x7DC4` were first
  read as a GCC switch table; the protocol increment
  (`g2-touch-i2c-protocol-recovery.md`) corrected this to nine uint32 tuning
  constants. The real RX command dispatch is a 9-slot switch at `0x42C-0x444`
  whose table (`0xB0C4`) lives in the resident flash region.
- The vector table at payload offset 0 implies updates rewrite the boot
  region itself; the residency/recovery model during programming is
  unresolved (gate).

## Behavioral recovery (string-level, inferred)

Log strings identify: power state machine ACT/ALR/WOT with all four
transitions (`ACT->ALR`, `ALR->ACT`, `ALR->WOT`, `WOT->ACT`, `WOT->ALR`);
proximity baseline capture/save with difference thresholding; gesture
configuration with long-press threshold; slider direction LEFT/RIGHT with
`dx/dt` speed telemetry; press/release/click counting; long press; a
5-fast-clicks host-reset trigger with timeout; EEPROM-emulated config
persistence guarded by the `0x45564E55` ("UNVE") magic with first-use
default initialization; and a `%d, %d, %d, %d` event report. These are
identifications from retained strings, not function-level closures.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_touch_identity.py
python3 -m unittest openCFW.tests.test_analyze_g2_touch_identity
```

The analyzer authenticates the blob, both CRC-32C relationships, the
vector-table shape and NVIC count, all ten pinned regions byte-for-byte,
the peripheral and SRAM censuses, the SROM decoder span, the code-label
table, the config magic and config-block key words, and the required
strings; it writes the three manifests only after every check passes. The
twelve fail-closed tests mutate wrapper, vector, per-region, and checksum
bytes and confirm rejection; the CRC-32C implementation is pinned against
a hardware-verified check value.

## Confidence and remaining gates

- **Family identity: proven (high).** OPN CY8C4046FNI: high, resting on
  the retained host-driver path plus a complete parametric match; the
  image itself contains no silicon-ID string.
- **Memory map: confirmed at region granularity;** `const_tables_a/b` and
  `config_block` semantics remain inferred.
- **Update container/checksums: proven.** Device-side opcode→handler
  mapping and the boot/DFU residency model are open.
- **Behavior (transport handler, reports, gesture, calibration, power):
  string-level only.** Function-level closure of the SCB1 command
  processor (`0x0824` region), the `0x7DC4` switch targets, the MSCLP
  sensing loop, and the EEPROM-emulation module is future work.
- **SDK lineage: GCC/newlib + EasyLogger-style logging confirmed;
  ModusToolbox/PDL provenance unresolved.** No source candidate is
  claimed; production ownership remains zero.
