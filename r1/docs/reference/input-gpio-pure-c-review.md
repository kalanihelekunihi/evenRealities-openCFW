# Named input-GPIO wrappers in C

`gpio/stock_named_gpio.c` now provides its open and read wrappers in ordinary C.
Read passes a local pin word to its existing body. Open passes a local three-word
scratch area; its existing body initializes the decoded pin and complete GPIOTE
configuration before use. Both naked assembly wrappers are removed.

The existing open/read bodies, close, callback installation, IRQ dispatch and
registration sections retain identical allocated bytes and relocations. There
is no new GPIO implementation or state owner. Typed return values, output byte,
record state, PIN_CNF=2, GPIOTE arguments and callback selection are retained.
Private frame locations and restored caller-clobbered R1/R2/R3 values are not
outputs of these C APIs; the prior wrappers' incidental register behavior is
outside this contract. Final callee-saved registers and stack are preserved.

## Executed evidence

`build/goal-r1-input-gpio-pure-c/verify-open.py` passes 2960 cases against both
stock and the previous compiled wrapper. Cases cover seven named records and a
missing record, closed/open/already-open states, pins on both ports, initialized
and uninitialized GPIOTE, provider error words, pull/polarity bytes and controlled
provider changes to record pin/configuration. Configuration-pointer addresses
are normalized; all four configuration bytes and the actual callback target
are checked. The stock continuation after GPIOTE errors is retained.

`verify-read.py` passes 4608 read/callback/close cases, including 1536 read cases,
against stock and the prior compiled unit. It covers all 64 encoded pin values,
record/name misses and opened-state values; read deliberately does not acquire a
new opened-state gate. Output guards, complete controlled record state, port
register memory, returned status and ordered comparison/provider traces match.
The encoded-pin matrix does not claim 64 physical bonded target pins.

The Nordic port decoder and GPIO instructions execute in these probes. strcmp
and GPIOTE SDK calls are modeled; GPIO registers are ordinary emulator memory.
There are no memory hooks. The earlier name-read-order correction is retained
by the unchanged helper code, rather than reasserted from an empty read trace.
Checks also cover callback alignment, final R4-R11, SP and interrupt masks.

Four compiled defects—wrong pin, wrong pull, reopening an already-open record,
and inverted input byte—are detected. Both clean suites pass afterward. REA
byte readbacks at 0x54B90 and 0x54ED0 match the locked application; their evidence
IDs and hashes are in the adjacent JSON review.

## Build and limits

The report `build/sources-goal-r1-input-gpio-pure-c/report.json` compiles all
778 units with no failures or duplicate strong symbols. Imports remain 124
application and 22 bootloader linker symbols. The named-GPIO object changes only
its wrappers; all six other helper/operation sections match. Two generated boot
object hashes differ in debug-path metadata, with identical source hashes,
allocated bytes and allocated-section relocations. The other 775 payload object
hashes are identical. The strict bootloader link still succeeds without
undefined symbols; no source-plan/qualification selection is changed.

R1 manifest validation passes. Global sources-check retains the existing G2
unlisted assembly-file failure. Physical GPIOTE configuration/interrupt delivery,
electrical pin state, timing, arbitrary faults/concurrency and full application
linking remain unproved. No device or firmware was written.
