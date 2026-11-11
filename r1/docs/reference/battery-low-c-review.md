# R1 low-battery escalation in C

`r1/src/application/board/native_battery_low.c` replaces the naked bridge and
its separate C kernel with one C function for stock application entry `0x3d88c`.
The compiler emits the prologue, saved-word accesses, return and count-nine
event tail branch. Empty register/stack constraints remain; this is not portable
ISO C or a claim that all firmware assembly has been removed.

REA/Ghidra read the locked stock body, literals and log strings. The raw
application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The companion [receipt](battery-low-c-review.json) records that evidence and the
normal source unit, compiler arguments, hashes and validation boundaries.

The production object passed 1,850 stock/C paired cases using the actual existing
battery-storage owner. Cases cover voltage thresholds, all byte counter values,
logging short circuits, wraparound, both interrupt-mask settings, and controlled
provider changes to the voltage, counter, handle and saved record words.
They check the native 16-byte frame and live R4-R11 at provider calls, the record
at caller SP minus 16, returned R0/R2/R3, and the restored SP/LR and callee
registers at the count-nine event tail handoff. Five deliberate threshold,
tail-count, voltage-width, saved-R3 and log-query errors were rejected.

One redundant same-value write to the private outgoing logger argument word is
normalized within a provider-free interval. Other observed record, context and
handle accesses remain ordered. Provider behavior is modeled; arbitrary aliases,
faults, concurrency, unrelated caller-clobbered registers and APSR are outside
this comparison. Real voltage sampling, KV writes, thread wakes and events have
not been tested on hardware. The frame proof is specific to the recorded Clang
profile and must be repeated after compiler or flag changes.

The normal R1 build compiled and composed all 590 units with no known failures
or duplicate strong symbols. The other 589 objects are byte-identical to the
previous PWM baseline; application/bootloader imports remain 164/34.
Exact-body qualification rejected the replacement, so the source plan is
unchanged. The hybrid application still matches the locked artifact using
4,245 source-built, 641,915 binary-pull-through and 248 resource bytes.
This does not prove a complete source link, a fully C firmware or physical
hardware support.

Ignored reproduction inputs and results are under
`build/goal-r1-battery-low-c/`; the current normal report is
`build/sources-goal-r1-battery-low-c-final/report.json` and the hybrid report is
`build/hybrid-goal-r1-battery-low-c/build-report.json`.
