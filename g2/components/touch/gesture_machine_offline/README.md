# Touch gesture machine — independent offline source

`gesture.c` reconstructs `0x4070..0x43da` and attention rearm `0x3afc`.
It composes independently validated speed and software-delay source; the
standalone linked module has no borrowed executable firmware calls. `gesture.h`
defines the exact 80-byte state layout and event flags.

Inputs are active 0/1, position byte and a delivered SysTick callback counter.
Direct tests also compare synthetic unsupported active values. Stable state,
valid speed-ring indices and sequential sample processing are preconditions.
Counters are not established milliseconds. Attention writes and delay loops
are verified offline against original instructions; electrical GPIO behavior,
interrupt timing and physical duration remain unverified.

The report/calibration composition loads selected native code into offline
fixed-address guest sections. It is not a production payload, exact-byte build,
hardware patch or independent source closure of the analog scan engine.
See [analysis](../../../analysis/touch-gesture-machine-closure-2026-10-08/REPORT.md).
