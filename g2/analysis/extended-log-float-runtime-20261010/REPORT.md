# Extended logger FP64 and fatal frontiers

The authenticated stripped main image has SHA-256
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.
The stock formatter reaches `vmul.f64 d0,d0,d1` at `0x4d435c` for a nonzero
`%f` fixture. Unicorn Cortex-M4, M7 and M33 models stop at that instruction;
`extended-log-common-format-20261010/float_probe.json` records the attempts.

`run_qemu.py` builds a standalone Cortex-M55 assembly probe and runs it on
QEMU 11.1.2 MPS3 AN547. It enables CP10/CP11, multiplies 1.5 by 1.5 with
`vmul.f64`, checks the exact double result, and prints `M55 FP64 PASS` through
semihosting. QEMU therefore provides a working FP64 instruction engine.
Its MPS3 AN547 board, however, has no memory at the stock main image base
`0x438000`: a loader attempt followed by monitor `xp /4wx 0x438000` returns
`Cannot access memory`. `qemu_probe.json` retains both observations. The
standalone arithmetic probe is **not** stock formatter execution. A QEMU
machine with the original code/data addresses mapped, plus initialized
formatter RAM and callback state, is needed before stock float output can be
compared to any C candidate. Static caller `0x49d580` establishes only that
three float32 values are promoted to three FP64 stack arguments at offsets
+8, +16 and +24 for `day_high:%f, day_low:%f, dark_price:%f`.

The direct-call inventory now resolves three earlier misses via ADR strings:
`0x5326d6` points to a blank string, and `0x5b5572`/`0x5e8f02` each point
to `%s`. Twelve of 6,239 syntactic BL sites remain with runtime format
pointers. Four stores use the function's `r8` parameter (`0x56d4c0` through
`0x56d564`); eight store a pointer to a stack buffer at `sp+8`
(`0x56d5cc` through `0x56d7e6`). They need producer/value analysis, not
another flash literal search. The revised inventory resolves 6,227 sites
to 5,032 static format addresses; 18 resolved sites use float syntax and
lie outside the current source parser. Static syntax fit for the other
6,209 is not behavioral coverage.

`classify_runtime_formats.py` asserts those twelve origins against the
authenticated disassembly. The four `r8` slots come from the `r0` format
parameter of wrapper `0x56d478`, which has 30 syntactic direct callers; a
sample caller at `0x5e2c2c` loads a flash literal into `r0`. The eight
`sp+8` slots follow bytewise construction of a bracketed hexadecimal dump
in the same wrapper. The exact set of parameter values and every generated
buffer/terminator case remain unproved; `runtime_format_classification.json`
records all 12 sites and 30 wrapper calls.

`probe_fatal.py` executes four bounded stock paths. Null module in
`0x43d4b0` and level six in `0x43d574` each reach the configured callback
at cell `0x2007456c` with assertion line 481 and 572 respectively. With
the cell zero, each reaches the fatal loop call at `0x44b0ae`. The probe
stops on callback **entry** or the first loop call; it does not assume the
callback returns or identify its production target. The scanned flash has
five literal references to the callback cell. `callback_cell_xrefs.py` finds
17 direct code references through those literals, all reads of the cell;
this does not exclude computed writes, copies, or startup initialization.
No production callback target/value has been established. `fatal_probe.json`
records callback arguments and stop PCs, and `callback_cell_xrefs.json`
records the direct references.

No source unit was added. The archive remains 27 translation units and the
direct SMP logger count remains 10/11. The remaining distinct evidence tasks
are an address-compatible FP64 runtime for 18 static float call sites,
producer contracts for 12 runtime-format sites, and installed fatal callback
ownership/return semantics. These are scope counts, not a time estimate or
a claim that all parser-fitting sites have been tested.
