# G2 touch-controller I2C source closure

Status: the shipped command/report protocol is implemented in freestanding
Cortex-M0+ C. Live electrical validation is blocked by unavailable physical evidence,
and the factory resident region at flash `>=0x8680` remains an explicit
unavailable proprietary input. No device, I2C bus, reset, signing, or flash
operation was performed.

The C/header pair is original openCFW clean-room work and contains no copied
GPL or vendor source. Under the repository's additional grant it is offered as
`MIT OR GPL-3.0-only`, preserving the existing GPL option while making the MIT
option explicit. This grant does not apply to the retained firmware bytes,
resident ABI, or separately licensed providers.

`components/shared/touch/runtime_touch_i2c_protocol.c` implements eight
source APIs covering:

- the authenticated 1–16-byte RX bound and command range 0–8;
- the seven recovered command bodies, with fail-closed handling for the two
  slots whose resident-table targets are unavailable;
- version, baseline, long-press, persistence, DFU-handoff, and sensor replies;
- 16-byte event reports, active-low attention lifecycle, pending state, and
  the exact `0x280` timeout;
- proximity-baseline persistence only when the absolute delta exceeds 49;
- long-press nonzero validation and both dirty flags;
- event 0–7, RX/TX FIFO descriptor, and power-mode bounds;
- a callback-only resident DFU mailbox/reset handoff.

The source owns protocol policy but cannot invent the missing resident command
and event switch tables, HAL descriptors, boot vectors, or resident DFU
engine. Those remain called through explicit ports or fail closed. The shipped
prefix therefore remains in the firmware package.

Seven focused tests authenticate the original ten machine-code spans and
state pools, compile all eight definitions for
`thumbv6m-none-eabi`/Cortex-M0+, and exercise every command, malformed lengths,
sensor reads, long-press validation, persistence threshold edges, report
layout, attention assert/release, events, FIFO state, power bounds, and DFU
handoff.

Run:

```sh
make touch-i2c-source-closure
```

Future qualification requires an authorized G2 touch controller and I2C/GPIO
capture validating resident table order, SCB1 IRQ/HAL descriptors, attention
timing, sensor values, EEPROM behavior, sleep/deep-sleep, and reset into DFU;
that validation is blocked by unavailable physical evidence.
