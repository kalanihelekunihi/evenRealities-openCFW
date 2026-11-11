# R1 watchdog IRQ and channel feed

The existing unmodified `nrfx_wdt.c` application object now has current evidence
for `WDT_IRQHandler` (stock `0x34a7c`, 26 code bytes) and
`nrfx_wdt_channel_feed` (`0x7b508`, 14 code bytes). Their frontier references
previously pointed at removed pre-consolidation objects and receipts.
The [receipt](wdt-irq-c-review.json) records the normal object, hashes, compiler
arguments, REA/Ghidra stock byte reads and test limits.

The test links the actual normal-build object, placing its handler cell at the
stock-observed `0x2000794c`. This is a test placement, not final-link or cold-start
proof. It uses bounded memory observers over watchdog MMIO and the handler cell.
The 480 paired IRQ invocations cover zero and nonzero event words, two handlers,
callback changes to the event and handler cell, repeated calls, and both PRIMASK
settings. They preserve the ordered event read, handler lookup, callback, zero
write and event readback. Callbacks run before clearing the event. The observed
callback frame is 16 bytes in both versions; native R5 is zero whereas C R5 retains
the incoming value. Live registers are recorded, not claimed equal.

Another 48 paired channel feeds cover all eight reload-request registers with
three initial values and both PRIMASK settings. Each writes only its selected
register using `0x6e524635`. Four deliberate errors—skipped callback, skipped
clear, inverted event condition and wrong feed channel—were rejected.

Private readback spills, nonargument caller-clobbered callback values and APSR
are excluded. The tests do not emulate watchdog time, expiry/reset latency,
feed deadlines, actual interrupts or exception frames. Init, enable, allocation
and feed-all APIs remain outside this runtime qualification.

No firmware source or manifest changed. The current R1 report remains
`build/sources-goal-r1-battery-low-c-final/report.json`: 590 compiled/composed
units, 164 application and 34 bootloader imports. Exact-body qualification
selected nothing; the source plan and hybrid result remain unchanged. A complete
source link and physical watchdog behavior are unproven. Ignored reproduction
inputs are under `build/goal-r1-wdt-irq-c/`.
