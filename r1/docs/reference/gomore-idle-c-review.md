# R1 GoMore idle callback and shared sensor workspace in C

Follow-up: [accelerometer/raw-HR adapters](gomore-stream-adapters-c-review.md)
now resolve the remaining stream callbacks and readiness gate. Counts below
describe the preceding idle-callback build.

`native_gomore_sensor_idle.c` implements stock idle callback `0x6aca4`, count
clear `0x6acc8`, timestamp helper `0x6acd8` and failure counter `0x6c1c0` in C.
The [receipt](gomore-idle-c-review.json) binds REA bytes, objects, startup replay,
independent state/call oracles, qualification and source composition.

One **52-byte ZI workspace at `0x2001a56c`** replaces the former separate
eight-byte HR/HRV sample owner. Its nested sample fields remain at workspace
+36/+40 (`0x2001a590`/`0x2001a594`). It also names time/UTC-offset, sensor buffer
pointer slots, accelerometer/raw-HR counts, time validity and activity fields.
The authorization header provides the existing sample view through this owner.
The 148-byte authorization state remains separate. Native RW/ZI startup handlers
and an independent decoder match all **200 owned bytes**, with guards unchanged;
the consolidation adds 44 net bytes and leaves no duplicate sample owner.

Timestamping stores a fresh backend time, then the **low halfword of the signed
UTC-offset provider**, marks time valid and records whether health mode is zero.
The idle callback passes the workspace to native sensor update `0x94384`, then
feeds its returned status to the C failure helper. Status zero clears the
failure byte and returns success; the callback clears raw-HR count before
accelerometer count and returns the workspace address. Nonzero status returns
zero without those count clears.

Failure diagnostics run only when the entry counter is below three. Log modes
and timestamps are freshly loaded at the native boundaries. After logging, the
counter is reloaded, incremented with eight-bit wrap and stored. Values at least
60 cause a zero store **before** reinitialization. Thus an incoming 255 wraps
to zero without reinitialization. Provider changes during logging remain visible.

**11,088 paired native/C/oracle cases** pass across all four roots: 7,632 idle
and 1,152 each for stamp, clear and failure. Coverage includes status words,
counter thresholds/wrap, health modes, time endpoints, signed UTC offsets,
changing log modes and mutations of counters/time/counts inside providers.
Return values, exact provider/state sequence, guarded workspace/state, preserved
registers, SP, masks and FPSCR match. Lower time/health/update/log/reinitialization
providers remain modeled. Eight compiled defects are rejected; the quick control
set explicitly includes the counter-58 case needed to distinguish threshold 59
from 60.

The relocated shared views also pass **10,323 HR/HRV pairs**, including 1,200
expected faults and 720 actual authorization-chain cases, plus **2,026 standalone
authorization pairs**. Those fixtures bind the consolidated workspace address;
they do not claim a complete linked sensor-update algorithm. The idle fixture
links the actual new workspace owner and authorization-state owner.

All **675 units** compile with no duplicate strong symbols; **672 prior
source/object pairs** are unchanged. Authorization and HR/HRV objects change
for the shared-owner relocation. Application imports remain **165** and
bootloader imports **34**: the idle-callback import is replaced by
`r1_gomore_sensor_update_native`. Accelerometer/raw-HR adapters and the native
sensor-update/lifecycle dependencies remain unfinished.

All four functions fail instruction qualification. The canonical plan remains
**4,369 source-built bytes** and the fresh hybrid matches the locked application
through executable pull-through. No new assembly is introduced. Whole-image
placement, full source-only linking, byte identity, concurrent execution and
physical sensor/timer behavior remain unproven.
