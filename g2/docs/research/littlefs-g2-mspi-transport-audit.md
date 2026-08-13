# G2 littlefs MSPI/external-NOR transport audit

## Verdict

The main-firmware and bootloader MX25U25643G transports are now recovered
through their board-facing initialization boundary. Both use Apollo510B
**MSPI1**, chip select **CE0**, SPI mode 0, a **96 MHz** device clock, one-byte
instructions, four-byte addresses, and the same byte-identical serial, quad,
timing, timing-scan, and GPIO objects.

This closes the major unknowns left by
`littlefs-g2-block-port-audit.md`:

- exact MSPI instance, interrupt, TCB, and chip-select selection;
- serial and quad command/address/clock configurations;
- GPIO 49/95/96/97/98/103/104 pin policy;
- the fallback timing and complete 36-by-32 timing sweep;
- retained deep-sleep/wake and mutex policy;
- the main image's XIP aperture and the boot image's non-XIP behavior; and
- the relationship between NOR offsets, the main XIP aperture, and the
  littlefs partition.

The open-source Apollo510 HAL imported from AmbiqSuite 5.1.0 is a
source-equivalent replacement for the identified HAL bodies. The G2 pin
selection and MX25U25643G lifecycle remain downstream board policy, but their
material values are now recovered well enough to implement as ordinary
source rather than preserve the complete driver blob.

No hardware, serial, debug, pogo, flash, or write operation was performed.

## Reproducer and authenticated inputs

The standalone reproducer is read-only:

```sh
python3 tools/analyze_g2_littlefs_mspi_transport.py
python3 tools/analyze_g2_littlefs_mspi_transport.py --json
```

It verifies both authenticated image hashes, resolves and decodes the exact
IAR initialized-data records, requires byte-identical main/boot MSPI objects,
checks all seven GPIO configuration words, pins the initialization and timing
function bodies by SHA-256, and verifies the main XIP object. It uses only the
Python standard library and cannot address a physical device.

| Image | SHA-256 | Installed mapping |
|---|---|---|
| `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte package header, payload at `0x00438000` |
| `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

The IAR scatter records independently recover the initialized SRAM rather
than treating an uninitialized RAM address as evidence:

| Image | Record | Handler | Stream | Encoded field | Destination | Decoded bytes | Decoded SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---|
| Main | `0x0075D3F0` | `0x0043A11F` | `0x0079189E` | `0x54E0` | `0x20000000` | 17,752 | `df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743` |
| Boot | `0x00433100` | `0x00415327` | `0x004341C0` | `0x04E2` | `0x20000000` | 1,371 | `e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843` |

The two decompressed configuration regions are not merely semantically
similar: their 24-byte serial object, 24-byte quad object, six-byte fallback
timing, and 216-byte timing table are byte-for-byte equal.

## Transport topology

```text
littlefs v2.10.1 callbacks
        |
        | NOR offset = 0x01400000 + block*0x1000 + offset
        v
G2 MX25U25643G policy
  read: QREAD4B 0x6C
  prog: PP 0x02
  erase: SE 0x20
        |
        v
Ambiq Apollo510 HAL (source-equivalent)
  MSPI1 / CE0 / SPI mode 0 / 96 MHz
        |
        +-- PIO blocking transfers used by littlefs
        |
        `-- main only: read-only 32 MiB XIP aperture at 0x80000000
```

The littlefs read callback does **not** load through the XIP window. Main and
boot both use a constructed `am_hal_mspi_pio_transfer_t` and the blocking PIO
HAL path. XIP is a concurrent main-firmware capability and power-policy
constraint, not the littlefs data path.

## Exact device configurations

The current public `am_hal_mspi_dev_config_t` names map cleanly to the
recovered 24-byte IAR short-enum ABI. Source should use field initializers and
named enums, not reproduce this packed ABI.

| Offset | Field | Serial object | Quad template |
|---:|---|---:|---:|
| `0x00` | `ui8TurnAround` | 8 | 8 |
| `0x01` | `eAddrCfg` | `AM_HAL_MSPI_ADDR_4_BYTE` | same |
| `0x02` | `eInstrCfg` | `AM_HAL_MSPI_INSTR_1_BYTE` | same |
| `0x04` | `ui16ReadInstr` | `0x0003` | `0x006B` |
| `0x06` | `ui16WriteInstr` | `0x0002` | `0x0002` |
| `0x08` | `eDeviceConfig` | `AM_HAL_MSPI_FLASH_SERIAL_CE0` | `AM_HAL_MSPI_FLASH_QUAD_CE0_1_1_4` |
| `0x09` | `ui8WriteLatency` | 0 | 0 |
| `0x0A` | `eSpiMode` | `AM_HAL_MSPI_SPI_MODE_0` | same |
| `0x0B` | `eClockFreq` | `AM_HAL_MSPI_CLK_96MHZ` | same |
| `0x0C` | `bEnWriteLatency` | false | false |
| `0x0D` | `bSendAddr` | true | true |
| `0x0E` | `bSendInstr` | true | true |
| `0x0F` | `bTurnaround` | true | true |
| `0x10` | `bEmulateDDR` | false | false |
| `0x11` | `eCeLatency` | 0/default | 0/default |
| `0x12` | `ui16DMATimeLimit` | 0 | 0 |
| `0x14` | `eDMABoundary` | 0/default | 0/default |

Raw objects and hashes:

```text
serial:
08 03 00 00 03 00 02 00 00 00 00 14 00 01 01 01 00 00 00 00 00 00 00 00
SHA-256 afe6fe0edd2efdb10cdc4e1dd9021916709ab9f52077eee6e8bfa3018ae46986

quad template:
08 03 00 00 6B 00 02 00 10 00 00 14 00 01 01 01 00 00 00 00 00 00 00 00
SHA-256 bae2c3ff93a23cefbdb43825a67be78b67a6ab47f090616d16a0a694b0b3d598
```

The serial object is at main `0x200007F0` / boot `0x2000020C`. The quad
template is at main `0x20000808` / boot `0x20000224`.

The quad-mode helper copies the template, then explicitly sets:

```c
cfg.ui8TurnAround = 8;
cfg.ui16ReadInstr = 0x006C; // QREAD4B
cfg.eDeviceConfig = AM_HAL_MSPI_FLASH_QUAD_CE0_1_1_4;
cfg.bTurnaround = true;
```

Thus the live quad read command is `0x6C`, not the template's `0x6B`. The
mixed PIO selection is 1-1-4: instruction and address are sent on one wire,
with data received on four wires. It is not 1-4-4 QPI.

The serial helper applies zero effective turnaround after device
reconfiguration; the quad helper applies eight. Both do this through the
HAL timing-scan-set semantic request, so the static serial object's initial
eight does not imply eight serial dummy cycles.

## Board pin and interrupt policy

Both images call the same BSP-style pin helper with `(module=1,
device=AM_HAL_MSPI_FLASH_QUAD_CE0_1_1_4)`. Its MSPI1/quad path configures
these exact pins:

| GPIO | Apollo510B function | Role | Raw `am_hal_gpio_pincfg_t` word |
|---:|---|---|---:|
| 49 | `AM_HAL_PIN_49_MNCE1_0` | MSPI1 CE0 | `0x00000582` |
| 95 | `AM_HAL_PIN_95_MSPI1_0` | data bit 0 | `0x00000480` |
| 96 | `AM_HAL_PIN_96_MSPI1_1` | data bit 1 | `0x00000480` |
| 97 | `AM_HAL_PIN_97_MSPI1_2` | data bit 2 | `0x00000C00` |
| 98 | `AM_HAL_PIN_98_MSPI1_3` | data bit 3 | `0x00000C00` |
| 103 | `AM_HAL_PIN_103_MSPI1_8` | MSPI1 clock | `0x00000C00` |
| 104 | `AM_HAL_PIN_104_MSPI1_9` | MSPI1 DM0/DQS0 | `0x00000C00` |

GPIO 104 is configured by the common board helper even though the selected
quad-SDR device mode does not consume octal DQS data. A source port should
preserve the recovered pin setup first and simplify only after board
measurement.

The GPIO roles are corroborated by Ambiq's
[Apollo510B SoC datasheet](https://contentportal.ambiq.com/documents/20123/4530417/Apollo510B-SoC-Datasheet.pdf)
and the pin/function definitions in the public Apollo510 HAL import.

The driver installs:

```text
IRQ:      21 = MSPI1_IRQn
priority: 4
mask:     0x00001A80
```

In the public Apollo510 register definitions, `0x1A80` is
`SCRERR | CQERR | CQUPD | DERR`. The driver clears that mask before enabling
it and enables the NVIC line after setting its priority.

## Controller allocation and instance lifetime

The low-level initializer accepts an instance argument, but both public G2
initializers pass instance 1 and the downstream device-state array reserves
one slot.

| Property | Main | Boot |
|---|---:|---:|
| MSPI instance | 1 | 1 |
| HAL handle global | `0x20074544` | `0x200270DC` |
| downstream device handle output | `0x20074540` | `0x200270D8` |
| TCB pointer | `0x203799A0` | `0x200F4C00` |
| TCB size | 256 words / 1,024 bytes | same |
| `bClkonD4` | false | false |
| downstream state base | `0x20073E34` | `0x20026FD0` |

The controller order is:

1. `am_hal_mspi_initialize(1, &handle)`;
2. `am_hal_mspi_power_control(handle, AM_HAL_SYSCTRL_WAKE, false)`;
3. `am_hal_mspi_configure(handle, &controller_cfg)`;
4. `am_hal_mspi_device_configure(handle, &quad_template)`;
5. `am_hal_mspi_enable(handle)`;
6. install the fallback timing with serial/zero turnaround;
7. configure the recovered MSPI1 quad pins;
8. configure XIP only in main;
9. clear and enable interrupt mask `0x1A80`;
10. set `MSPI1_IRQn` priority 4 and enable it; and
11. publish the initialized downstream handle.

Return values from initialize, power, configure, device-configure, enable,
and interrupt setup are checked. Later transaction wrappers log some mutex
and mode failures without propagating them, as documented in the block-port
audit.

## Main XIP versus boot non-XIP

Main copies this 16-byte short-enum XIP object from flash address
`0x00785D00`, calls the HAL XIP-config semantic request, then calls XIP-enable:

```text
00 00 00 00  00 00 00 00  00 00 00 80  01 09 00 00
```

Its SHA-256 is
`b164ea6b22fe58fab81549c6ad12726b528a0182303e599866dc8a5f0441fa8b`.

Decoded semantically:

| Field | Value |
|---|---:|
| scrambling start | 0 |
| scrambling end | 0 |
| aperture base | `0x80000000` |
| aperture mode | read-only |
| aperture size | 32 MiB |

The Apollo510 register map defines the MSPI1 aperture as
`0x80000000..0x84000000`; the G2 selects its first 32 MiB. NOR offset zero
therefore maps to CPU address `0x80000000`.

The boot driver's corresponding low-level initializer makes no XIP-config or
XIP-enable call. It uses the same PIO transfers and pin/device objects without
enabling an aperture in this initialization path. This statement is bounded
to the recovered NOR initializer; it does not assert that no unrelated boot
code can ever touch MSPI XIP registers.

The HAL request ordinal numbers in the binary are not copied into the source
design. The binary maps semantic operations at request values `0x10`
(timing set), `0x12` (XIP config), `0x15` (XIP enable), and `0x18` (PIO mixed
mode). The later public header's enum ordinals differ by two. Named
`AM_HAL_MSPI_REQ_*` constants must be used against the selected HAL revision.

## Exact littlefs partition relationship

The physical NOR is 32 MiB:

```text
NOR offsets: 0x00000000..0x02000000
```

The littlefs callbacks cover:

```text
start: 0x01400000
size:  0x00BC0000 (3,008 * 4,096)
end:   0x01FC0000 exclusive
tail:  0x00040000 (256 KiB)
```

Under main's recovered XIP mapping, the same bytes are:

```text
NOR 0x01400000..0x01FC0000
CPU 0x81400000..0x81FC0000
```

This is an address translation, not a second copy. The littlefs callback
still supplies NOR offsets `0x01400000..0x01FBFFFF` to PIO. The audit does
not assign a meaning to the 20 MiB before littlefs or the 256 KiB after it;
doing so requires independent callers or a golden external-flash capture.

## Timing calibration

The initialized fallback timing object is identical in both images:

```c
{
    .bTxNeg = 1,
    .bRxNeg = 0,
    .bRxCap = 1,
    .ui8TxDQSDelay = 6,
    .ui8RxDQSDelay = 14,
    .ui8Turnaround = 8,
}
```

Raw bytes are `01 00 01 06 0E 08`, SHA-256
`fd3470730e23fba9e5d4c55ba67a15924ea2467786ef8ed836ccb3a86f60cccc`.
The objects are at main `0x20000820` / boot `0x2000023C`.

The 216-byte timing table, SHA-256
`a26d40aacdbb0889ec7da60e94af64373ba35610ca63a92b0555b718cdeae182`,
contains 36 six-byte rows:

```text
TxNeg:      fixed 1
RxNeg:      0..1
RxCap:      0..1
TxDQSDelay: 1..9
RxDQS seed: fixed 1
turnaround seed: 32
```

For each of the 36 coarse rows, the scan substitutes:

```text
RxDQSDelay: 0..31
turnaround: 8
```

It therefore performs at most 1,152 JEDEC-ID reads. A pass requires the
packed return value `0x002539C2`. The read-ID helper's buffer ordering makes
that packed integer correspond to the Macronix on-wire ID bytes
`C2 39 25`.

Each coarse setting accumulates a 32-bit pass mask. The code finds the
widest contiguous passing window, selects its midpoint as the receive-DQS
fine delay, and copies that coarse row plus the chosen delay into the active
timing object. If calibration fails, it retains the active fallback fields.
Mode helpers subsequently force effective turnaround to zero for serial and
eight for quad, so the table's byte-five seed of 32 is not used as a live
quad dummy-cycle value.

The main and boot timing algorithms differ mainly in diagnostic density:

| Image | Timing scan | Bytes | Timing auto | Bytes |
|---|---:|---:|---:|---:|
| Main | `0x0046F788` | 622 | `0x0046F9F6` | 278 |
| Boot | `0x00420002` | 440 | `0x004201BA` | 154 |

Their recovered table, loops, ID criterion, window selection, and result
layout agree.

## NOR initialization and mode lifecycle

The public initializer sequence is the same in both images:

1. low-level MSPI1 initialization using the quad template;
2. delay 10 ms;
3. send reset-enable `0x66`;
4. delay 1 ms;
5. send reset `0x99`;
6. delay 50 ms;
7. reconfigure to serial mode;
8. perform automatic timing calibration;
9. reconfigure to serial mode again;
10. read three JEDEC-ID bytes with `0x9F`;
11. send enter-four-byte-address-mode `0xB7`;
12. set and verify the Macronix QE bit;
13. create the flash mutex; and
14. put the MSPI peripheral into retained deep sleep.

The public initializer checks whether the ID command succeeded and logs the
value, but does not reject a successfully read non-Macronix ID. The timing
scan is the path that requires exact packed ID `0x002539C2`.

QE handling reads status with `0x05`, treats bit 6 as QE, clears protection
bits `0x3C`, uses write-enable, writes status with `0x01`, waits, rereads, and
verifies the requested QE state. This matches the device-specific status
policy in the
[Macronix MX25U25643G datasheet](https://www.macronix.com/Lists/Datasheet/Attachments/8766/MX25U25643G%2C%201.8V%2C%20256Mb%2C%20v1.1.pdf).

Program and erase use `0x02` and `0x20` after the global `0xB7` transition,
while reads use dedicated QREAD4B `0x6C`. Program/erase temporarily select
serial PIO and restore quad PIO on exit. Read selects quad before submitting
the transfer.

## Busy polling and transfer timeouts

The status helper sends `0x05`, reads one byte, and interprets bit zero as
WIP/busy.

The general wait helper has two phases:

1. at most 200 polls, each after a 5 ms delay: nominally 1,000 ms; then
2. a caller-selected number of polls, each after one RTOS tick when the
   kernel is running or a 1,000 us busy delay otherwise.

The default wrapper supplies 500 phase-two polls, for a nominal maximum of
about 1.5 seconds. Page program uses the default before WREN and a shortened
10-poll phase two after PP, nominally about 1.01 seconds total. Erase uses the
default wait before and after erase.

The underlying blocking PIO calls receive `1,000,000` microseconds as the HAL
timeout. The read driver calls the general busy wait before QREAD4B but
ignores its result; program and erase classify selected wait failures as
downstream status 4 or 3 as described in the block-port audit.

These nominal durations assume a 1 ms CMSIS tick. A source port should express
the RTOS portion in kernel ticks and document the configured tick frequency
instead of silently assuming it.

## Mutex and retained-power policy

Both transports use a CMSIS-RTOS2 mutex named `flash_mutex`, with a static
80-byte control block:

| Property | Main | Boot |
|---|---:|---:|
| mutex handle global | `0x20074548` | `0x200270E0` |
| control block | `0x20072A88` | `0x20026C60` |
| control-block size | `0x50` | `0x50` |

The composite transaction lock:

1. calls `osMutexAcquire(handle, osWaitForever)`;
2. unless the no-auto-sleep policy byte is one, calls
   `am_hal_mspi_power_control(handle, AM_HAL_SYSCTRL_WAKE, true)`.

The composite unlock:

1. unless that policy byte is one, calls retained deep sleep; then
2. calls `osMutexRelease`.

| State | Main | Boot |
|---|---:|---:|
| no-auto-sleep policy byte | `0x20074FB8` | `0x200271C5` |
| retained-sleep state byte | `0x20074FB9` | `0x200271C6` |

Main additionally has separate helpers that acquire the mutex, force a
retained wake, and set the policy byte to one; or clear it, enter retained
deep sleep, and release the mutex. This supports consumers that must keep
MSPI/XIP continuously available.

The "deep sleep" here is the Apollo MSPI peripheral power state with register
retention. It is not the MX25U25643G deep-power-down command. The public
Ambiq HAL saves/restores the MSPI register set, manages the MSPI clock
request/gate, and controls peripheral power for these retained transitions.

Mutex acquisition, release, and creation failures are logged, but some
transaction paths continue. A new source implementation should initially
preserve ordering while changing these failures to hard operation failures
before any erase/program path is enabled.

## Open-source source-equivalent boundary

The authoritative public source reference is Ambiq's Apollo510 HAL import,
commit
[`5efc0228528a8adce5eae0d226fac85d2551eb3b`](https://github.com/AmbiqMicro/ambiqhal_ambiq/commit/5efc0228528a8adce5eae0d226fac85d2551eb3b),
whose commit message identifies AmbiqSuite SDK 5.1.0. The source itself
identifies revision `release_sdk5p1p0-366b80e084` and carries Ambiq's
three-clause redistribution terms.

Pinned Git blobs:

```text
mcu/apollo510/hal/mcu/am_hal_mspi.c
  c12ef914660227aba3ebef3a0fb3ec749510c1bc
mcu/apollo510/hal/mcu/am_hal_mspi.h
  738ae35ffbe8ca3158df18d3b28794bf0c7b2589
mcu/apollo510/hal/am_hal_gpio.h
  9cbc5ea43722c16ede6f577457db5da2c11ddad6
mcu/apollo510/hal/am_hal_pin.h
  840d3a1793f9e5337a7bb3623e133abf57b0279d
mcu/apollo510/regs/am_reg_base_addresses.h
  3b7338a3711ebb10b45335412ba6ae69da437a89
```

The following are source-equivalent HAL responsibilities and should be
compiled from the Ambiq source rather than decompiled:

- MSPI initialize/configure/device-configure/enable/disable;
- blocking PIO transfer;
- MSPI control requests for timing, XIP, and PIO mixed mode;
- interrupt clear/enable/service;
- retained MSPI power control;
- clock-manager and peripheral-power hooks;
- GPIO pin configuration; and
- Apollo510 register and IRQ definitions.

The CMSIS-RTOS2 mutex API and CMSIS NVIC primitives are also public source
interfaces. Their concrete backend should come from the OpenCFW RTOS port;
this audit does not need to re-create mutex or NVIC internals.

The following remain G2/downstream policy even though their values are now
recoverable:

- selecting MSPI1/CE0 and the seven G2 pins;
- the two 24-byte device policies and 96 MHz clock choice;
- XIP enabled only in main, with its exact aperture policy;
- timing scan table, ID criterion, and fallback tuple;
- MX25 reset, address-mode, QE, WIP, program, and erase sequencing;
- power cycling around the flash mutex; and
- downstream status-to-littlefs error mapping.

`drv_mx25u25643g.c` and `littlefs_mx25u25643g_porting.c` do not appear in the
public Ambiq HAL repository. They should be recreated as compact G2 board
source around the Ambiq HAL, not mislabeled as upstream Ambiq files.

The public commit postdates the opaque firmware and is therefore a
source-equivalent reference, not proof that Even's historical build used
that exact Git checkout.

## Source re-creation plan

A bounded source replacement can now be organized as:

```text
platform/ambiq/
  upstream AmbiqSuite 5.1.0 HAL and Apollo510 register headers

boards/even_g2/
  g2_mspi1_pins.c
  g2_mx25u25643g_config.c
  g2_mx25u25643g_timing.c
  g2_mx25u25643g_power.c

fs/
  checked read-only littlefs block port
```

The first hardware-capable revision should remain read-only:

1. compile the pinned public Ambiq HAL;
2. configure MSPI1/CE0 and the recovered pins;
3. reproduce reset, serial calibration, ID read, four-byte mode, and QE setup;
4. implement QREAD4B PIO only;
5. check the complete requested range against
   `0x01400000..0x01FC0000`;
6. mount the pinned littlefs core with `LFS_READONLY`; and
7. compare a complete external-flash capture and repeated reads before
   enabling any mutation.

Named HAL enums must be used rather than binary request ordinals or raw
short-enum structures. Compile-time assertions should cover the PIO transfer
ABI only where retained binary interoperability is still required.

Program and erase should remain unreachable until read-only capture,
filesystem validation, power-loss testing on disposable copies, and
hard-failure mutex/mode handling pass.

## Remaining unknowns and hardware gates

The source configuration is no longer materially blocked by unidentified
MSPI values. The remaining gates are empirical or intentionally out of
scope:

- a golden 32 MiB external-flash capture;
- observed filesystem disk version and full host-side tree/content
  comparison;
- electrical confirmation that the recovered drive-strength words are
  appropriate on production G2 boards;
- measured 96 MHz timing margins across temperature/voltage and multiple
  units;
- confirmation that GPIO 104 should remain configured in quad-SDR mode;
- cache/DAXI coherence requirements for consumers that actually dereference
  the main XIP aperture;
- ownership rules between those XIP consumers and the auto-sleep policy; and
- destructive program/erase and power-loss qualification on expendable
  hardware or image copies.

No remaining item justifies guessing a register or issuing a write on a
production device.
