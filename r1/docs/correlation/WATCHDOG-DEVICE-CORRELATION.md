# Watchdog device and Nordic provider correlation

## Decision

The R1 watchdog is implemented with Nordic nRF5 SDK 17.1.0's
`modules/nrfx/drivers/src/nrfx_wdt.c`. OpenR1 does not recreate that driver or the stock generic
device registry. Local code is limited to the recovered fixed configuration, one-channel
lifecycle, and scheduler feed seam.

The immutable census is
`../../scripts/firmware/summarize_r1_watchdog_device_boundary.py`.
It validates seven exact functions totaling 386 executable bytes against the rebuilt application.

## Exact function split

| Stock extent | Bytes | Ownership | Role |
| --- | ---: | --- | --- |
| `0x00056638..<0x00056654` | 28 | R1/Nordic adapter | validate open state and feed the allocated channel |
| `0x00056658..<0x0005668C` | 52 | R1/Nordic adapter | initialize, allocate one channel, enable, mark open |
| `0x00056694..<0x000566A6` | 18 | R1 configuration | bind the fixed watchdog record and operation table |
| `0x0007B470..<0x0007B4D6` | 102 | Nordic | `nrfx_wdt_channel_alloc` |
| `0x0007B508..<0x0007B516` | 14 | Nordic | `nrfx_wdt_channel_feed` |
| `0x0007B520..<0x0007B556` | 54 | Nordic | `nrfx_wdt_enable` |
| `0x0007B570..<0x0007B5E6` | 118 | Nordic | `nrfx_wdt_init` |

Ghidra omitted all seven entries and incorrectly attached a distant non-contiguous region to the
unrelated entry at `0x0007B448`. The ownership ledger therefore records these as exact manual
provenance supplements. Their sizes and SHA-256 digests are checked independently; no interval is
attributed merely because it is adjacent.

## Recovered configuration

The scatter-loaded record named `watchdog` is at `0x20007630`; its operation table is at
`0x2000765C`. The exact configuration is:

- behavior value `1`: run while the CPU sleeps and pause while halted by a debugger;
- reload interval 10,000 milliseconds;
- interrupt priority 6;
- one allocated reload channel; and
- a timeout handler that returns immediately, allowing the hardware reset to follow.

The four provider bodies reproduce Nordic's state byte, allocation index, WDT base
`0x40010000`, reload-request magic `0x6E524635`, interrupt setup, reload calculation, and state
transitions. These are compiled from Nordic source under `use_nordic_sdk`.

## OpenR1 integration

[`../../platform/nrf52840/sdk/openr1_watchdog.c`](../../platform/nrf52840/sdk/openr1_watchdog.c)
contains only the R1 adapter. It supplies the values above, allocates exactly one Nordic channel,
creates a low-priority scheduler-liveness worker, and feeds that channel every 1,024 RTOS ticks.
The provider implementation is the unmodified Nordic translation unit added to the SDK build.

This task-based feed is the functional equivalent of the stock event-loop feed in OpenR1's
FreeRTOS architecture: a stalled scheduler stops the worker and permits reset. It is not claimed
to reproduce the stock compiler output or generic device framework.

No BLE watchdog control, reload-value setter, debug bypass, signing bypass, or arbitrary reload
channel surface is exposed.

## Verification

The linked SDK map retains `nrfx_wdt.c.o`, `openr1_watchdog.c.o`, all four Nordic WDT entry
points, and `openr1_watchdog_initialize`. A clean GNU Arm Embedded 9-2020-q2 build produces an
unsigned application with 90,956 bytes text, 236 bytes data, and 132,456 bytes BSS. The standalone
HEX SHA-256 is `0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`;
the 85,020-byte BIN SHA-256 is
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`. These values are pinned by
the SDK image verifier; no SoftDevice merge, bootloader merge, signing, or flashing is performed.
