# Azoteq IQS7211E provider, Nordic port, and R1 product boundary

## Decision

The IQS7211E path is no longer an unresolved four-function vendor gate. Two attributable source
references are pinned:

- Flipper One's IQS7211E driver at commit
  `0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067`. Its repository's authoritative
  `REUSE.toml` assigns MIT to the driver files. This is an authenticated compatible provider
  reference, not a claim that the stock R1 used Flipper source.
- `include/iqs7211e_init.h` at commit
  `436d3c42172abf812ec104521f29384fc02fc50e` of
  `sekigon-gonnoc/zmk-driver-iqs7211e`. That file contains its own MIT grant and an Azoteq
  copyright notice. It establishes a licensed vendor-authored settings-block schema; its sample
  values are not used as R1 values.

The provider references supply device/register/state-machine semantics. Nordic SDK bus and GPIO
primitives now supply the nRF52840 transport. openR1 owns only the R1 register values,
ring-size/electrode data, board lifecycle, communication-window glue, IRQ routing, and bounded ATI
recovery policy. The portable implementation is in `r1/src/r1_iqs7211e.c`; source board bindings
exist for both Nordic SDK and Zephyr. The Zephyr target binds reconstructed YHM2710 shared power,
but still fails closed until a valid device identity and wear/factory request are supplied. The
legacy Nordic target retains the abstract power seam.

## Pinned source inputs

| Input | Pin | Hash |
| --- | --- | --- |
| Flipper One archive | `0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067` | `4a957ea082ae2146692567ece71abd0b122a6c7c914bc964cee64d3d68656199` |
| `iqs7211e.c` | same | `68441fb6856ed05bf94406772f47b3d1612db8fa20aae80e9ba3806019819184` |
| `iqs7211e.h` | same | `22999801ffb919cd259ed105e5ccb027a67a6806c759ca00677f312bd3efaa84` |
| `iqs7211e_reg.h` | same | `5886e493dcdb0ac65ef4507e748e0dbd3f1947c64e309b979c92b0c39c760756` |
| Flipper `IQS7211E_init.h` | same | `91edd0a6098bbbb67d06f96338d14545bdf59207c02add3c3799e59ca764099b` |
| Flipper `REUSE.toml` | same | `55a271c44547fc95dcc15930984efb29d3bb2ed453c93603c9a7295e2286b644` |
| Explicitly MIT Azoteq settings header | `436d3c42172abf812ec104521f29384fc02fc50e` | `266efea581cb5c55726e2e06402ca0c657e14c4a5e684fa4880160f81ca2c5ba` |

The source locations and archive hashes are machine-pinned in `third-party/fetched/manifest.json` and
checked by `third-party/fetched/verify_vendor.py`.

The official Arduino Example Code v1.1 archive remains correlation evidence only:

- archive SHA-256: `b7b845d80fbb3eca3e08392e5010ff3f29be4de6072e59eb6cf41221f8dc9c12`
- `IQS7211E.cpp`: `208eef9a283089246572bfc5b6c7f5bd0ae5c68cf597082edf6e6ae68389825f`
- `IQS7211E.h`: `0845461ec37acdd10acf30aa56bd2d12a34bb92f2c5f2d901a67c22b48a13de7`

Those v1.1 files do not contain a license grant accepted by this project, so they are not copied or
compiled.

## Function ownership split

The exact adapter-entry digest is
`81b2e89b28cbd6ca0b88a3db4f60c7f2ec01ee75beb2125495c1e0f5d1ffd266`.
Every body is independently pinned by size and SHA-256 in the verifier.

| Recovered entry | Size | openR1 role | Ownership |
| --- | ---: | --- | --- |
| `0x0002F866` | 26 | factory communication-end marker | R1 factory glue |
| `0x0002F880` | 1,274 | complete profile writer | R1 configuration around provider semantics |
| `0x0002FDC8` | 26 | IRQ-time config-byte refresh | R1 communication-window glue |
| `0x0002FDE2` | 20 | address-only communication end | provider port/glue |
| `0x0002FDF8` | 80 | suspend request | R1 lifecycle adapter |
| `0x0002FE9C` | 16 | register-read port | Nordic/provider transport adapter |
| `0x0002FEAC` | 52 | bounded register-write port | Nordic/provider transport adapter |
| `0x00030E6C` | 434 | normal IRQ worker | R1 status/event policy |
| `0x00046650` | 578 | touch-task event dispatcher | R1 lifecycle/event/factory glue |
| `0x0006F9E4` | 300 | ATI retry and hardware-restart policy | R1 recovery policy |
| `0x0006FCE8` | 120 | reset-triggered reconfiguration | R1 event adapter |
| `0x00087BA4` | 24 | one-word register read | provider adapter |

No stock function is asserted to be a Flipper private symbol. The correlation is semantic and the
local split is deliberately at the provider/R1 boundary.

## Recovered R1 behavior implemented

The portable implementation and tests preserve:

- 7-bit address `0x56` and little-endian register words;
- ten ring sizes (`6` through `15`) for both 8-Tx/3-Rx and 7-Tx/3-Rx layouts;
- all twenty byte-exact 30-byte calibration records, including compensation divider, fine
  fractional divider, trim span, and 24 channel slots;
- the `0x1F`, `0x21`, `0x28`, `0x36`, `0x41`, `0x4B`, `0x56`, `0x5D`, `0x6C`, and `0x33`
  initialization writes;
- final bytes `33 A0 00 6C 47 00 00`, which acknowledge reset and queue trackpad re-ATI;
- normal communication end through register `0xFF`;
- suspend by reading system control `0x33`, setting `0x0800`, writing it back, and ending the
  communication window;
- reset flag `0x0080`, ATI error flag `0x0008`, and too-many-fingers flag `0x1000`;
- trackpad reseed `0x0008` and re-ATI `0x0020` system-control requests;
- saturating consecutive ATI-error count, restart threshold `5`, at most `3` hardware restarts,
  restart delay `0x66` ticks, and factory marker `0x55` suppression;
- configuration rollback/board close on transport failure and `R1_ERROR_UNSUPPORTED` with no
  provider binding.

The recovered board evidence fixes TWIM0 at 400 kHz, SCL `P0.12`, SDA `P0.01`, touch LDO
`P0.30`, and the bidirectional active-low RDY/MCLR line at `P0.17`. The portable adapter does not
hard-code live GPIO access; the SDK binding owns those board operations.

## Nordic SDK binding

The linked nRF52840 target now compiles Nordic's `nrfx_twim.c` and `nrfx_gpiote.c`, rather than a
local bus or interrupt-driver substitute. The build and map verifier require the two Nordic object
files, the touch-port object, and the retained `nrfx_twim_*`, `nrfx_gpiote_*`, and
`GPIOTE_IRQHandler` symbols.

| Property | Recovered value | SDK realization |
| --- | --- | --- |
| peripheral | TWIM0 at `0x40003000` | `NRFX_TWIM_INSTANCE(0)` |
| address | 7-bit `0x56` | checked by the provider callbacks |
| SCL / SDA | `P0.12` / `P0.01` | explicit `nrfx_twim_config_t` pins |
| frequency | 400 kHz, raw `0x06680000` | `NRF_TWIM_FREQ_400K` |
| TWIM priority | `2` | explicit priority `2` |
| hold bus after uninit | false | `hold_bus_uninit = false` |
| LDO enable | `P0.30` | Nordic GPIO output |
| RDY/MCLR | `P0.17`, active-low | bidirectional Nordic GPIO/GPIOTE pin |
| RDY event | high-to-low, no pull, low accuracy | `NRFX_GPIOTE_CONFIG_IN_SENSE_HITOLO(false)` |

Blocking TWIM mode keeps every transfer in the worker thread. A read transmits the one-byte
register address without STOP and then receives the requested bytes. A write uses an EasyDMA-safe
RAM frame containing the register byte and at most 33 payload bytes; communication end is the
one-byte `0xFF` register frame. The GPIO ISR only posts flag bit `1`. The worker rejects a high RDY
level and opens TWIM only for an active-low request before calling the portable IRQ processor.

The board-open implementation follows the recovered order and raw tick delays:

1. acquire shared-power client bit `2` and request its release after `0x800` ticks;
2. delay `1`, raise `P0.30`, then delay `10`;
3. close the RDY input, drive `P0.17` high and then low, and delay `130`;
4. drive `P0.17` high, delay `10`, return it to the default state, and delay `20`;
5. install and arm the active-low GPIOTE input, delay `20`, then mark hardware active.

Close marks the device inactive, disarms and uninitializes the RDY input, lowers the LDO, and leaves
RDY/MCLR driven low. The portable `r1_iqs7211e_deactivate` path first issues the recovered suspend
read/modify/write when the controller is configured, then always performs that power-down and
clears retry state. This orderly suspend is a deliberate fail-safe addition; it is not asserted to
be an instruction-for-instruction copy of the stock service-close wrapper.

ATI recovery closes the board and uses a one-shot CMSIS timer with the recovered `0x66`-tick delay.
The timer posts a restart flag to the worker; it never performs bus or GPIO work in timer context.

## Provisioning and lifecycle policy

There is no guessed ring variant. `OPENR1_TOUCH_LAYOUT` defaults to `255` and
`OPENR1_TOUCH_RING_SIZE` defaults to `0`, which cannot select a calibration record. A product build
may set the two Make variables, or a trusted provisioning layer may call
`openr1_touch_set_identity`. The selection is accepted only for one of the two recovered layouts
and ring sizes 6 through 15, and cannot change while hardware is active.

The separate `openr1_touch_power_ops` boundary is mandatory. It represents the recovered shared
power-client acquisition and delayed-release operations; no dummy success implementation is
installed. The R1 three-client ownership policy is now implemented behind one semantic provider
operation, while YHM2710 register/transport code remains vendor-gated. Touch leases can be
recorded before provisioning, but no LDO or bus activity occurs
until both identity and power boundaries are valid. If delayed release cannot be scheduled after
acquisition, the board port attempts an immediate release and powers the local pins down.

Lease source `0` is reserved for the recovered wear/touch consumer and source `2` for factory use.
The first effective lease posts open and the last posts close. `touchSwitch` (`01/00/07`) now
reaches a runtime effect hook and changes the enable policy without impersonating the missing wear
sensor: disabling closes an active leased controller, while enabling only permits a real wear or
factory lease to open it. The stock wear transition and its `0x96000`-tick delayed removal close are
still awaiting an admitted wear-provider board adapter. While the factory lease is present, IRQ
processing supplies the recovered `0x55` factory marker that suppresses normal ATI-error recovery.

## Verification and remaining work

Host, sanitizer, freestanding Cortex-M4, and Nordic SDK image builds compile the adapter. Host tests
pin the configuration-frame order and selected bytes, both layout/ring calibration lookup, suspend
read/modify/write, communication end, the four re-ATI retries followed by restart scheduling, and
the too-many-fingers reseed path. They now also pin orderly deactivation and the runtime
`touchSwitch` effect callback. The verified Nordic image contains the Nordic TWIM/GPIOTE drivers,
CMSIS timer/thread operations, portable adapter, and board port. Its current hashes are:

- HEX: `1ee7af3316adfc4d09f8964315b52104c1a4a04d21d9e17d0aa5284cc7869869`
- BIN: `297adf03553260c93013a4bc87a1f56287d15bcf342c6d308e0871fc1cde9553`

Owned-hardware completion still requires an authenticated shared-PMIC/power-manager provider,
device-specific identity provisioning, the wear-provider lease source, and logic-analyzer plus
touch-event validation. The Nordic TWIM/GPIO/IRQ binding itself is installed; it remains
deliberately unable to energize hardware while either provisioning boundary is absent.
