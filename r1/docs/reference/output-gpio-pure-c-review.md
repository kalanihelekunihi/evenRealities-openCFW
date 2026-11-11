# Output GPIO wrappers without inline assembly

The read operation `r1_output_gpio_slot10` and toggle driver
`r1_output_gpio_driver14` in `gpio/native_output_gpio_operations.c` now use
ordinary C locals for the pin scratch passed to their existing kernels. Their
naked assembly wrappers are removed. The existing configuration, read and
toggle kernel sections and their relocations remain identical.

The typed outputs are unchanged: toggle returns the decoded port address and
performs ordered OUT read, OUTSET write and OUTCLR write; read returns its
status and writes one output byte only for a found, opened record. Lookup order,
opened checks, the Nordic pin-port decoder and configuration aliasing behavior
are retained. Incoming/restored caller-clobbered R3, exact private stack frames
and intermediate provider-visible saved registers are not outputs of this C
interface. Final callee-saved registers and SP remain preserved.

## Executed evidence

`build/goal-r1-output-gpio-pure-c/verify.py` passes 7906 three-way comparisons
between locked stock instructions, the new C wrappers and the previous compiled
wrappers. It covers read, toggle and configuration operations; all five records
and lookup failures; closed/open records; 64 encoded pin values; varying GPIO
OUT/IN words; controlled device-name mutation and aliased/null configuration.
The 64 encodings test decoder/bit-mask behavior, not the existence of 64 physical
bonded pins on the target.

Tests compare returned values, configuration storage and output guards, ordered
name loads/strcmp arguments and exact GPIO access traces. Toggle explicitly
checks one OUT read followed by OUTSET=mask&~OUT and OUTCLR=mask&OUT on the decoded
port. Register accesses are inspected from instruction operands using code hooks;
there are no memory hooks that could interfere with Thumb conditional state.
GPIO registers are ordinary mapped emulator memory, not electrical peripherals.
strcmp is modeled; the Nordic decoder and register instructions execute.

Four compiled defects—forcing port zero, wrong clear mask, inverted input read
and reading closed records—are detected, followed by a clean baseline rerun.
REA readbacks for 0x54E20 and 0x54EA8 are pinned in the JSON review and checked
against the preserved application bytes. They are not a physical GPIO test.

## Composition

`build/sources-goal-r1-output-gpio-pure-c/report.json` compiles all 778 units
without failures or duplicate strong symbols. Import sets remain 124 application
and 22 bootloader linker symbols. The GPIO object changes only its wrappers;
its configuration and two kernel sections retain identical bytes/relocations.
Two generated boot objects differ in debug-path metadata with identical source
hashes, allocated bytes and allocated-section relocations; the other 775 payload
object hashes are identical. A strict bootloader link still succeeds without
undefined symbols. No source qualification or source-plan selection is changed.

R1 manifest validation passes. The global check still reports the pre-existing
unlisted G2 assembly file. Physical GPIO, asynchronous pin changes, faults,
arbitrary invalid pointers, timing and full application linking remain unproved.
No device or firmware was written.
