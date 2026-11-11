# R1 temperature mode and periodic sensor-stream control in C

`r1/src/application/runtime/native_temperature_mode.c` supplies three native
bodies: mode transition `0x4b718` (256 bytes), mode setter `0x4bab4` (22 bytes)
and periodic entry `0x4bbf0` (54 bytes). The event-service symbol aliases the
setter's single implementation. [The review receipt](temperature-mode-c-review.json)
binds source, production object, REA bytes, startup replay and test artifacts.

The setter accepts full-width values below 3, loads the previous mode, performs
the transition, then stores the new byte after all provider calls. Equal modes
only log. Other transitions unregister the old mode's stream handle and clear
its slot after the call. Leaving mode 1 releases a nonnull timer and clears the
timer field after release. Entering mode 1 creates a timer only if a fresh read
finds no timer. Its callback is the reconstructed periodic entry, period is
600,000 ticks and context is zero; the diagnostic reports 600, matching stock.
The old-mode indexed access deliberately retains stock's unchecked 32-bit
address calculation, including corrupt old-mode values.

The periodic entry first checks the health-mode getter and then the timing
stream handle. If enabled with no handle, it clears the 14-byte timing record,
sets byte 12 to 1 and registers `temp` / `timing` with order 1 and flags 1. The
returned handle is stored after registration. The sample callback at `0x4bc40`
remains an explicit native dependency. Its frontier route now names that native
interface rather than suggesting that the differently shaped Gomore analysis-
plan API is an executable provider.

The new unit owns only an eight-byte mode/timer control at `0x20006e4c`, three
handle words at `0x2001e3cc` and a 14-byte timing record at `0x2001e3dc`.
Executing the locked application's RW decompression and ZI initialization on
poisoned regions with guards confirms all 34 cold bytes are zero. Independent
RW decoding agrees. Adjacent measurement state and the four-byte gap between
handles and record remain unowned.

There are 2,808 paired stock/C direct cases covering valid and invalid setter
inputs, equal and unequal modes, corrupt old-mode indices, null/nonzero handles
and timers, all logging bits, changing log sequences, interrupt masks, zero and
nonzero registration/constructor results, and mutations during provider calls.
They compare call ordering, arguments, provider-boundary state snapshots and
final state, preserved registers, stack restoration and masks. Six compiled
defects are rejected: wrong timer period, early mode storage, omitted handle
clearing, omitted existing-timer guard, short record clearing and omitted health
gating.

A further 384 cases execute the actual C periodic entry, health getter, memory
clear, `memset` and name-based registration wrapper together. They cover missing
objects and registration failure/success, including diagnostic paths and a
mutation of the timing handle inside object registration. Lookup and object
registration are modeled at their lower boundaries. Memory observers are
disabled; snapshots avoid the known Unicorn Thumb-IT observer interaction.

All three roots are void; raw return residue, caller-clobbered registers, APSR
and private stack bytes are excluded. Ordinary provider depths are native/C
48/40 bytes through the setter, 32/24 through direct transition, and 16/24 at
the periodic entry. SDK logging tails can release frames before calling.
These C bodies are not instruction-identical and exact qualification rejects
all three anchored patterns. The canonical source plan is unchanged.

All 620 units compile and both payloads compose without duplicate strong
symbols. All 619 prior objects are unchanged. The event-service import is
resolved while the native sample callback becomes explicit; counts stay at 166
application and 34 bootloader imports. A fresh hybrid retains 4,295 source-built
bytes and matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Physical temperature sensing, asynchronous timer/stream behavior, remaining
measurement providers and a complete source-only link remain open.

The [subsequent sampling review](temperature-sample-c-review.md) now supplies the
native measurement callback, checks and publisher in C. Periodic-to-sample
sequences match stock within the documented provider boundaries.
