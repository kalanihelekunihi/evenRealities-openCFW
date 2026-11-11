# R1 living-probe callback in C

`native_wear_living.c` supplies stock `0x3ce44` as ordinary C. The
[review receipt](wear-living-c-review.json) binds REA bytes, production hashes,
direct and sequential comparisons, rejected defects and qualification.

The callback ignores context and length and reads payload byte 1 without a null
guard. It stores the byte to living status before calling the OS tick provider,
then publishes that provider's raw timestamp after the call. It preserves fresh
mode queries and short-circuit logging, reloading status separately for each
enabled log path. After logging it freshly captures the living-stream handle,
unregisters `wear` when nonzero and clears the handle after unregister returns.
Provider changes to status, timestamp and handle are therefore observed in stock
order. Null payload faults at address 1; payload `0xffffffff` wraps to a read at
zero. No new RAM is introduced: the status, timestamp and handle remain owned by
the existing wear-off unit. Its callback prototype is refined to the established
three-word stream ABI without changing its compiled object.

Direct verification passes 5,380 paired stock/C cases with byte/status boundaries,
full-word ticks and handles, changing log modes, tick/log/unregister mutations,
payload aliases into status/timestamp/handle, null/wrapped faults and interrupt
masks. It compares public state, write widths, arguments and logical faults, and
checks preserved registers/SP on normal returns plus masks and FPSCR. Both native
and C direct callback provider frames are eight bytes; neither callback executes
FP instructions. Void R0, fault PC, caller-clobbered registers, APSR and private
stack residue are excluded.

Another 384 paired three-phase sequences execute actual C wear-off, callback and
wear-off, preserving state across calls. They exercise probe registration or an
existing handle, delivery/release, timestamp wrap and result ages at 0/2048/2049
and full-word wrap, then consumption or restart of the probe. Tick, registration,
unregister and logging providers remain modeled. Seven compiled defects are
rejected: wrong payload byte, truncated timestamp, wrong logged status, early
handle clear, wrong structured tag, null guard and stale handle. Physical and
concurrent behavior remain unverified.

All 650 units compile and both relocatable compositions pass without duplicate
strong symbols. All 649 earlier objects remain unchanged. The living callback is
resolved without new imports, leaving application/bootloader imports at 171/34.
Manifest validation passes. The body does not qualify as exact. The source plan
stays at 4,345 source-built bytes; a fresh hybrid matches the locked application
with 641,815 executable pull-through and 248 resource bytes. Complete source-only
linking and byte identity from C remain unfinished.
