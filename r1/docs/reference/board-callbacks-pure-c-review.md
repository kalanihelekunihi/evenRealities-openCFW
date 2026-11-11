# R1 board callbacks in C

This is a historical 877-unit receipt. The later
[profile callback review](event-profile-update-c-review.md) records the C body
and retained raw-register branch for `425b0`; the latest strict-link status is
in [application-source-link-review.md](application-source-link-review.md).

Twenty callback bodies in `r1/src/application/board/native_event_callbacks.c` now use ordinary C. This follows the user's revised target: byte identity and a paid compiler are not required. Existing stock behavior remains the basis for accepting replacements.

The [machine-readable receipt](board-callbacks-pure-c-review.json) pins sources, objects, REA bytes, test harnesses and build reports. The final report is `build/sources-goal-r1-board-callbacks-pure-c-final/report.json`; its 877 units compile and compose with no duplicate strong symbols. The import sets remain 61 application and 22 bootloader symbols. Composition uses `ld -r`; this is not a bootable image.

The converted entries are `42118`, `42788`, `42840`, `42856`, `42860`, `4286e`, `4287c`, `42896`, `428a4`, `428b4`, `42960`, `42964`, `4296a`, `42978`, `42a10`, `42a20`, `42b20`, `42bc2`, `42bc6`, and `42bca` (hex addresses). Their 700 native instruction bytes agree with fresh REA reads and all execute across the direct corpus.

Verification passed 23,880 paired native/C cases: 5,760 pointer/length guards, 7,800 scalar/gate cases, 10,080 clock boundaries, and 240 provider-mutation cases. Comparisons include provider arguments and packet snapshots, packet read widths/order, saved registers, stack, interrupt masks and guards. Activity/stress consumer lengths are unused in the actual consumers and excluded from those call-boundary comparisons. Caller scratch, void return registers, APSR and private stack addresses are excluded. Null accesses test logical access shape, not physical MCU fault handling.

A separate 7,200-case chain executes the actual C callback, connection-presence predicate, charge notification packet builder and response-header helper against native execution. The charge builder/header helper each execute 2,160 times. Charger queries, connection-handle getter and final response transport remain modeled. The historical gate name does not establish authentication. Source execution cannot enter stock code; modeled providers return through BX LR stubs.

Twelve successfully compiled defects are rejected: missing pointer guard, wrong packet length, full-word command comparison, ignored connection gate, reordered health services, missing hour cleanup, inclusive clock cutoff, signed timezone, unconditional pending mark, missing key offset, wrong stress field, and wrong hour event.

Two provider declarations now accurately describe their incoming R0 packet pointer (`native_health_daily_fixture.c` and `native_health_get_dispatch.c`); their machine objects remain unchanged. The callback unit adds the CMSIS RTOS include path for its shared subscriber declaration. No new persistent state or imports are introduced. The 864 other nongenerated source/object pairs, callback strings and retained callback assembly body/normalized relocations are unchanged. Existing generated startup and uecc objects differ. The tested callback object equals the normal build object.

Callback `425b0` remains assembly: its fallback record consumes implicit incoming R2/R3 whose caller contract is unresolved. The `42724` string-interior assembler alias also remains. Physical sensor/charger/flash/BLE operation, final executable linking, startup and boot are still open. No instruction or image identity is claimed.
