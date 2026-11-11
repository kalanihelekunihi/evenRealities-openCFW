# R1 factory temperature monitor and shutdown in C

`native_factory_temperature.c` supplies callback `0x3cd24` (86 bytes), and
`native_factory_stop.c` supplies shutdown `0x48c68` (82 bytes). Both live under
`r1/src/application/runtime/`. [The machine-readable review](factory-temperature-c-review.json)
retains REA byte readback, source/build hashes, replay results, startup proof,
negative controls and the retained shutdown frame gap. Local Thumb disassembly
was checked against the locked application. REA did not expose an analyzed
procedure at the monitor entry; its byte read API supplied the pinned evidence.

The existing temperature transport/calibration bridges remain unchanged. Their
raw stack and R3-restoration contracts are documented in the earlier temperature
reviews; this change does not claim to replace those architectural adapters with
plain C.

## Monitor behavior

An inactive factory mode returns immediately. Otherwise the monitor calls charger
state, charge status and the temperature-pair reducer in that order, ignoring
status returns. Its 24-byte local record reaches the reducer at caller SP minus
32 on both paths. The reducer supplies the first five bytes. The monitor loads
both unaligned sample halfwords at offsets one and three, retaining the second
at record offset sixteen; neither sample affects its counter decisions.

The counter at mode-state offset twelve increments modulo 32 bits. An unsigned
difference of at least five from the saved counter causes the saved value to be
updated before the NV word setter is called. The live counter is then reread.
At 240 or above, the monitor obtains the configuration byte, passes its full
word with mask `0x10` ORed in to the byte setter, then calls shutdown. Provider
changes between these operations remain observable. Clearing active state in an
earlier provider does not short-circuit the already-running monitor; shutdown
performs its own fresh active check.

## Shutdown behavior and ownership

Inactive shutdown returns zero. Active shutdown clears the active byte first,
releases a nonzero timer and then clears its slot. Saved configuration is read
before live configuration; a changed value is installed before NV persistence.
The aging and accelerometer handles are each reread, unregistered by name when
nonzero and cleared after the provider returns.

Only the nonzero accelerometer-handle path tests the late byte at state offset
one. If set, it clears that byte, writes reset-cache words in order two, one,
zero, then clears the state halfword at offset six. A zero accelerometer handle
leaves this conditional state/cache alone, even if the byte is set. Active
shutdown returns one. The existing mode-state owner is reused without extending
its 28-byte extent.

The only new data owner is the twelve-byte reset cache at `0x2001a198`, immediately
before the separate threshold cache. Native RW/ZI startup handlers were executed
on poisoned regions with guards and checked against an independent RW decoder.
The new object data matches twelve native zero bytes, with four-byte alignment
and no data relocations. This does not prove final placement or full startup
integration.

## Verification and limits

The direct fixture passes 1,834 paired native/C cases with the actual new monitor
and shutdown bodies. It compares provider ordering and arguments, ordered state
and cache accesses, final state/cache slabs and guards, normal return SP,
callee-saved registers, masks and shutdown R0. It also checks the defined five-byte
temperature prefix and halfword copied to record offset sixteen. Cases cover
inactive/noncanonical active state, resource combinations, conditional cache
reset, counter wraparound, unsigned persistence differences, the 240 threshold,
high configuration bits and 512 seeded provider-mutation sequences.

Another 120 paired cases run the monitor/shutdown with the actual reconstructed
temperature reducer. GXT transport, delay, calibration and diagnostics are
modeled there, as are charger/status, NV, timer-release and unregistration
boundaries. Calibrations use an all-FF record; channel samples include zero,
positive and negative/extreme words. Linked object hashes are recorded. These
cases prove the connected C reducer path under those boundaries, not physical
sampling or persistent writes.

Six compiled negative controls are rejected: retaining active mode during stop,
reversing the persistence condition, wrong cache-clear order, persistence at
four instead of five ticks, shutdown at 239 instead of 240 and a wrong completion
bit. The reducer model supplies all five output bytes; partial output writes,
undefined private record bytes, monitor R0, other caller-clobbered registers and
APSR are excluded.

The monitor's reducer pointer and ordinary provider depth match at 32 bytes.
Shutdown provider depth differs: sixteen bytes native versus eight C, or 48
versus 40 bytes when nested beneath the monitor. No full stack, exception or
instruction identity is established. The temperature bridges and deeper
configuration/unregistration behavior remain separate proof boundaries.

## Build status

The initial full build failed five GCC compilations because the Docker daemon
was unreachable. Colima's existing instance was restarted without changing its
configuration; Docker recovered and a fresh full build passed. The failed
report is retained under the ignored build directory and is not used as the
successful build receipt.

`make sources-check` passes. All 617 units compile (543 application and 74
bootloader), both relocatable compositions pass without failures or duplicate
strong symbols, and all preceding 615 objects are identical. The manifest adds
only the two new units. The temperature-monitor import resolves; stream
unregistration becomes explicit, leaving 168 application and 34 bootloader
imports. The two root frontier rows are updated and the unregistration candidate
name now reflects its consumed interface.

Scoped qualification compiles both units but admits zero bytes. The source plan
is unchanged. The fresh hybrid matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
with 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. A complete source-only link, candidate byte identity, hardware
timing, persistence and physical sensor validation remain incomplete.

Reports: `build/sources-goal-r1-factory-temperature-final-c/report.json` and
`build/hybrid-goal-r1-factory-temperature-c/build-report.json`. Fixtures and
audits remain under `build/goal-r1-factory-temperature-c/`; durable results are
in the JSON review above.

The subsequent [stream unregistration candidate](stream-unregister-c-review.md)
resolves the shutdown import. Eighty paired cases run actual factory shutdown
through unregistration and the existing C list, stop, retiming, conversion and
period providers. The factory shutdown frame gap remains; physical timing and
persistence are still unproven.
