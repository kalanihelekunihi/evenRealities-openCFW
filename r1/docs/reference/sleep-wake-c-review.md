# R1 sleep wake controller and timer operations in C

`native_sleep_wake.c` supplies the force-awake controller `0x4a4b4` and timer
callback operations `0x4a56c`. The event-service symbol aliases the controller's
single implementation. [The review receipt](sleep-wake-c-review.json) records
REA bytes, production hashes, startup initialization and replay artifacts.

The controller gates on active exactly 1, logs, clears active before reporting
temperature status zero, invokes the native Gomore wake provider and publishes
event 12 using the live state byte. Only afterward does it read the timer field;
a fresh zero creates the wake callback with period 3,000 and context zero.
Provider changes to active/timer fields remain visible. The unit owns only the
authenticated eight-byte control at `0x20006ed4`; executing RW/ZI initialization
on poisoned regions with guards, plus independent RW decoding, confirms its
cold bytes are zero. Adjacent sleep state remains separate.

The timer packet starts at caller SP-24 in the saved incoming R2/R3 pair. Stock
writes byte 6, byte 1 and halfword zero into the first word, while retaining the
raw incoming R3 word as the packet tail. It publishes event 14 with all eight
bytes, releases the original callback timer argument and clears the global timer
after release. The C body preserves the native write widths/order and accesses
the live packet; mutations through the publish pointer remain reflected in the
restored R2/R3 words.

A small frame-only assembly bridge retains that raw register/stack contract.
It is not an opaque native body or opcode array. Ordinary C through the existing
one-argument timer interface cannot name the incidental incoming R3 word or
specify those restored output registers. The controller and callback operations
are C; this architectural boundary remains explicit.

There are 544 paired native/C cases covering exact active gates, existing and
absent timers, all logging bits and changing log sequences, constructor failure,
interrupt masks, incoming timer/raw-word boundaries and mutations during status,
Gomore, publish, constructor and release calls. They compare call order,
arguments, live-state snapshots, final state, preserved registers, masks, SP,
packet placement, ordered packet writes and both restored packet words. Seven
compiled defects are rejected: boolean active gating, late active clearing,
wrong period, zeroed raw tail, wrong header, early timer clearing and a shifted
packet frame.

Another 1,024 paired cases execute the actual C temperature reporter, sleep-
status controller and mode setter/transition under the new wake controller.
They cover valid/corrupt current and saved modes, timing handles, temperature
timers, wake timers and logging paths. The native Gomore entry at `0x6b50c`
remains unresolved; its route now names the native no-argument interface rather
than the differently shaped analysis-plan API. Timer, lower stream, event and
logging operations remain modeled boundaries in these replays.

Direct wake-controller call depths match stock at eight bytes. The C timer body
adds 16 bytes at its provider calls, while packet placement stays at SP-24. The
temperature reporting wrapper's previously documented frame difference remains
in the integrated path. Other caller-clobbered registers, raw void results,
APSR and private stack bytes are excluded; no exception-stack or physical
sleep/wake identity is claimed.

All 624 units compile and both relocatable payloads compose without duplicate
strong symbols. All 623 prior objects are unchanged. Resolving the event-service
import exposes the native Gomore provider, leaving counts at 164 application and
34 bootloader imports. Exact qualification rejects both new anchored bodies.
The canonical plan is unchanged; a fresh hybrid retains 4,295 source-built bytes
and locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Complete source linking, physical execution and full instruction identity remain
open.

The [subsequent native Gomore wake review](gomore-wake-c-review.md) now supplies
that controller body in C, exposing its four remaining lower native interfaces.
