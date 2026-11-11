# Native battery-voltage acquisition C provider

The context-binding claim below is superseded by the [VPMIC correction](vpmic-binding-c-review.md). This historical implementation incorrectly used the battery runtime ADC owner. Its one-context fixture masked the error by relocating that owner to the YHM address. Its arithmetic/frame comparisons did not establish the correct normal hardware binding; use the corrected implementation and two-context evidence.


`adc/native_battery_voltage_read.c` supplies stock `0x506a4`, previously an
unresolved native source route. It opens the cached ADC device, acquires three
signed samples, clamps each negative sample to zero, closes the device and
returns `(((uint16_t)(sum / 3)) * 1200 + 2048) >> 12`. Raw provider statuses
remain ignored. This path has no delay and is distinct from the existing delayed
averaging routine at `0x50c90` and its separate scaling policy.

REA verified the 96-byte stock code and four-byte context literal. The C root
retains the 24-byte provider frame: the incoming R3 word becomes its sample
scratch, and only the low halfword is cleared and reset. High bytes and full-word
callback writes remain observable. The cached ADC handle is reloaded before
every call. Empty constraints preserve live R4-R7, the returned full R3 word and
the sample's position; the shared read-only SP helper avoids retaining an extra
frame pointer. All executed operations in this unit are C.

The normal product object passes 10,240 paired stock/C cases (20,480 executions):
6,144 signed-boundary grid cases and 4,096 deterministic partial-write cases.
Checks cover all live R4-R11, provider arguments and order, sample pointers,
signed clamps and integer scaling, untouched/one-byte/halfword/full-word writes,
status variation, callbacks mutating scratch and the cached ADC handle, R0/full
R3, final context, saved registers, SP and interrupt masks. Boundary-grid returns
also match an independent integer oracle.

Four compiled negative controls are rejected: removing signed clamping, using
the other ADC path's scaling coefficient, clearing the whole scratch word and
removing full loop unrolling. The latter adds an induction register and changes
the Clang provider frame to 32 bytes. The product uses guarded compiler unroll
pragmas. Strict GCC compilation succeeds but also reaches the open provider with
32 bytes instead of 24, so GCC behavior remains unqualified.

All 579 R1 units compile and compose without failures or duplicate strong
symbols. All 578 existing objects and import sets remain unchanged (164
application / 34 bootloader). The manifest adds only this unit. Official scoped
qualification compiles the root but selects no exact region. The source plan is
unchanged; no byte-exact source progress is claimed for this routine.

The canonical hybrid still hashes to
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource
bytes. Selected counts include assembly and data elsewhere. The normal report
is `build/sources-goal-r1-vbat-read-c/report.json`.

[Machine-readable evidence](vbat-read-c-review.json) retains hashes, REA records,
counterexamples and audits. Probes are under ignored `build/goal-r1-vbat-read-c/`.
Registry dispatch and ADC providers are modeled. Physical ADC/battery accuracy,
APSR, other caller-clobbered state, private saved-register/control-frame aliases,
faults and concurrency remain unproven. Original Arm Compiler 5 is unavailable.
Complete source-only, byte-identical firmware remains incomplete.
