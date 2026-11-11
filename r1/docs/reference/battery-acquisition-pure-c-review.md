# Battery acquisition in ordinary C

`native_battery_voltage_read.c` replaces the pinned-register and native-stack
implementation of stock 0x506a4 with ordinary C. It opens the YHM VPMIC ADC,
reads three signed samples, clips negatives to zero, clears the halfword after
each read, closes the device and applies the existing 1200/4096 scaling.
Every dispatch reloads the handle from YHM context +16. The separate VBAT
runtime context remains untouched.

`stock_battery_average_frame.c` replaces the naked stock 0x50c90 wrapper with a
C local sample buffer and the existing canonical averaging body. The latter
object is unchanged: the rectifier ADC path retains ten 64000-cycle delay
calls and three samples. Scaling and paired acquisition consumers also remain
unchanged. Both buffers have four bytes of storage, allowing the full-word
writes exercised by the historical fixture as well as signed halfwords.
The low halfword is explicitly reset; upper bytes and saved-register frames
are private implementation details with no output semantics.

Normal compiled objects, previous compiled objects and locked stock firmware
match in 416 cases each for direct VPMIC reads, direct rectifier averages,
scaled reads and paired reads (1664 cases, 4992 executions). Tests include
boundary and seeded random values; zero-, one-, two- and four-byte callback
writes; negative clipping; handle changes after every dispatch; ignored error
statuses; interrupt masks; open/read/close ordering and paired-output store
ordering. Source execution is guarded against entering stock instructions.
Return values, callback traces, distinct context state and paired outputs
match. Saved registers, SP and interrupt masks are checked. Private stack
addresses/content, incidental live callee-saved values during callbacks,
caller-clobbered output registers, arbitrary private-stack aliases and
concurrency are excluded from this typed C contract.

Five compiled defects are detected: wrong handle owner, omitted reset,
omitted negative clamp, wrong scaling constant and a corrupted average
return. A clean baseline is rerun afterward. Fresh REA bytes for both stock
entries match the locked application. Hashes and evidence identifiers are in
the companion JSON.

R1 source check passes at 784 units; no compile failures or duplicate strong
symbols occur. Application imports remain 114 and bootloader linker metadata
imports remain 22. Strict bootloader linking succeeds. An audit finds 780
identical prior object hashes; the two acquisition objects change, and two
generated bootloader object metadata hashes change while their allocated
bytes and relocations remain identical. The global source check still fails
on the unrelated unlisted G2 resident_rom_thumb_set.S.

Dispatch, ADC and delay callbacks are modeled. These tests do not prove
physical ADC conversion, electrical calibration, elapsed delay timing or
live device boot. The application is not yet fully linked. No source-plan
qualification or byte-identity claim is made.
