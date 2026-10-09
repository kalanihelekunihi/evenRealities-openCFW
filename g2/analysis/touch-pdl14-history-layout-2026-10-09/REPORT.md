# Eight residuals: authentic history and data-section closure

All eight selected functions now match their complete linked stock extents:

| Function | Runtime extent | Bytes |
|---|---|---:|
| Flash ClockBackup | 0x8CC4–0x8D00 |60|
| Flash ClockConfig | 0x8D00–0x8D20 |32|
| Flash ClockRestore | 0x8D20–0x8D50 |48|
| Flash WriteRow | 0x8D50–0x8E28 |216|
| ILO StartMeasurement | 0x9D90–0x9DDC |76|
| ILO StopMeasurement | 0x9DDC–0x9E18 |60|
| ILO Compensate | 0x9E18–0x9F34 |284|
| PM ExecuteCallback | 0xA444–0xA528 |228|

These1,004newselectedbytes await independent review. The46previously reviewed
entries total3,948bytes; denominator54remains fixed. No selected residual
mismatch remains under these source/compile contracts. Neither this census nor
its exact comparators establish whole-firmware source/pseudocode completeness,
unique producer, whole-payload equality or campaign admission.

## Why the old comparisons differed

Flash uses unmodified official PDL2.16 pin
`16aaf1d3d764ca3c426234c90cdeb6f19cb2d091`, with its authentic flash/device
headers explicitly overlaid. PDL2.17 removed the NOPs that stock still has and
changed status processing. Both predeclared historical flash compilations
(with/without data sections) agree at every non-relocated byte; final linkage
uses the recipe-supported data-section build. All headers actually consumed
are hashed, including current shared/device dependencies; this is not a claim
that an entire old producing BSP was authenticated.

ILO and PM retain the current unchanged public source. The single added
`-fdata-sections` option has independent support in authentic Infineon Category2
recipes at2020/2024/currentpins. It reproduces the distinct-variable literal
loads and corresponding instruction layout. No optimization/device/compiler
sweep, source fitting or full stock-flag claim was made. Raw failures, the
old source/header inputs and all prior reports remain preserved. `SELECTION.md`
predeclared these changes; `results.json` contains all argv, preprocessing,
consumed-input hashes and intermediate relocation outcomes.

## New behavior and layouts

The flash write path validates row/data, copies the row to a stack parameter
buffer, issues a SROM load request and executes the authentic NOP before
status processing. On load success it disables interrupts, backs up/configures
clocks, issues the selected flash/SFlash write request, reads status and
restores clocks; restoration failure replaces only an otherwise-successful
write result. PRIMASK is restored on the recorded source paths. These are
instructions and public source semantics, not executed flash operations or
physical completion/clock claims. The memcpy call remains explicitly external
at the stock-proven `0xAA2C` target; no executable stub was provided.

ProcessStatusCode matches all128bytes plus its80byte/20entry switch table at
`0xB51C`. The old58bytehistorical row truncates reachable case branches.
Original symbols are untouched; this additive mapping accounts for the full
helper section and table, separately from the eight selected functions.
Flash backup state binds to `0x20000F04` through original literal loads.

`test_status_original.py` passes32original decoder cases using synthetic
CPUSS_SYSARG backing. Every case reads that word exactly once and performs
no MMIO write. Success-prefix words return success; error-family inputs map
the authenticated SROM codes to PDL error/info results, including resume,
pending and in-progress distinctions; other prefixes return operation-started.
This validates the pure decoder and switch table, not a SROM request,
completion timeline or physical flash outcome. Results are in
`status-original-results.json`.

ILO's three one-byte states bind separately: compRunStat `0x20000F1C`,
preventIloMeasurment `0x20000F1D`, iloMeasurment `0x20000F1E`. Start/stop
honor the prevention flag and configure/reset the measurement selectors.
Compensate accepts source-contract desiredDelay100–2,000,000and a non-null
output, validates measurement configuration, starts a counter on first use,
reports started until completion, then calculates compensated counts using
the measured counter and SystemCoreClock word at `0x20000878`, with an overflow
avoidance arithmetic branch. No calibrated physical time/frequency is inferred.
The real matched libgcc division/zero-hook provider is reused rather than stubbed.

PM roots bind to `0x20000F34`, lastExecutedCallback to `0x20000F24`, and
failedCallback to `0x20000F28`. CHECK_READY/BEFORE_TRANSITION run forward,
respecting skipMode. CHECK_READY stops only on exact `CY_SYSPM_FAIL=0x4200FF`
and records that callback; an arbitrary nonzero callback status is not this
failure value. AFTER_TRANSITION runs backward from the tail. CHECK_FAIL runs
backward from the predecessor of the last executed callback, excluding the
callback that already reported failure. Parameters are copied into temporary
base/context storage for each callback.

`test_pm_original.py` validates80original-instruction compositions across
two supported types, failure locations, five skip masks and forward/rollback
or before/after sequences. Callback bodies/returns are explicit synthetic
providers; no real callback, sleep, IRQ or concurrency claim follows. The
initial fixture mistakenly supplied status1 as CY_SYSPM_FAIL and observed
continued dispatch. Correcting it to the preprocessed/header and stock literal
value0x4200FF yielded the80passing cases. This fixture correction is not a
firmware bug or physical-state observation. Results preserve ordered events,
parameter copies and callback-state outputs in `pm-original-results.json`.

Every linked BL/PC-relative data reference was checked against original
instructions before linkage. `linked-results.json` records the linked extents,
original reference evidence, input/script/ELF hashes and excluded dependencies.
No hand-patched relocation bytes, production changes, Git mutations, device
writes or shared campaign updates occurred. Independent review is pending.
