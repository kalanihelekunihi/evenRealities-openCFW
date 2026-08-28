# G2 touch sensing, gesture, and power-policy source closure

Status: implemented in freestanding Cortex-M0+ C; raw sensing and timing
validation is blocked by unavailable physical evidence. No device, sleep, reset, signing,
or flash operation was performed.

The C/header pair is original openCFW clean-room work and contains no copied
GPL or vendor source. Under the repository's additional grant it is offered as
`MIT OR GPL-3.0-only`, preserving the existing GPL option while making the MIT
option explicit. This grant does not apply to the authenticated machine-code
evidence or separately licensed providers.

The exact MSC loop at `[0x36C4,0x376C)` is authenticated independently. Its
source reduction copies six words per channel, applies the observed
`0xC000FFCA`, `0x00FF0004`, `0x00FF0063`, and `0x00400064` masks/values,
starts conversion selector `0x06D9`, returns status 4 on failure, and computes
the maximum 16-bit result across the runtime channel count.

The same source unit implements the four power transitions named in the
shipped image (`ACT->ALR`, `ALR->WOT`, `WOT->ACT`, `WOT->ALR`), left/right
swipes, configured long press, five-fast-click recognition, and a saturating
calibration threshold. MSCLP programming and conversion remain explicit port
callbacks; the code has no direct register or sleep access.

Seven focused gates authenticate the PSoC image and MSC body/literals, compile
all six definitions for `thumbv6m-none-eabi`/Cortex-M0+, and exercise channel
stride, descriptor rewrite, maximum reduction, conversion failure, every
observed state transition, held states, swipe directions, long-press boundary,
five-click reset, and calibration saturation.

Run:

```sh
make touch-sensing-closure
```

Production retains the shipped touch application. Future qualification uses
an authorized controller and golden raw MSCLP/gesture/power traces to validate
channel descriptors, noise margins, thresholds, direction, click and
long-press timing, ACT/ALR/WOT timers, sleep, and wake behavior; that validation
is blocked by unavailable physical evidence.
