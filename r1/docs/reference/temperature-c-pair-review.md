# GXT310 paired temperature read in C

`runtime/native_temperature.c` now implements the native paired sample
routine at `0x50e4c` and four channel wrappers in C. It acquires the bus,
enables both channels, requests both one-shot samples, delays 80 ticks,
reads both temperatures, disables the pair, releases the bus, and reads
the six-byte calibration record in the native order. Intermediate status
returns remain ignored as in stock. The wrappers pass addresses `0x90`
and `0x94` to the existing temperature-read and one-shot providers.

The pair routine bypasses calibration only when all six bytes are `0xff`.
Otherwise mode zero subtracts the unsigned halfword offset, mode one adds
it, and other mode values leave that channel unchanged. Volatile byte and
packed halfword loads preserve native access widths and order, including
the unaligned halfword at offset one. Arithmetic uses unsigned 32-bit
wraparound; adding the sum's sign bit before extracting bits 1 through 16
preserves the native result without signed C overflow.

REA analysis of the locked stock bytes and raw instruction inspection
agree on the sequence and arithmetic. The execution probe passed 3,904
stock/C comparisons: 2,880 paired reads and 1,024 wrapper calls. It covers
each first-non-`0xff` position, mode values 0/1/2/128/255, zero and maximal
offsets, signed boundaries, overflow, random inputs, and calibration
changes during reads. Checks compare callback order and owned arguments,
R0, exact calibration load addresses/widths/values/order, guards,
callee-saved registers, SP, interrupt masks and callback stack alignment.
Callbacks clobber caller-saved registers and return varied status words.

The pair and wrappers execute; bus, mode, trigger, sample, delay and
calibration-read callbacks are modeled. Existing trigger, floating-point
conversion and calibration-frame assembly sections and all three data
sections retain their bytes and relocation identities. The other 561
source units are unchanged. All 562 R1 units compile without failures or
duplicate strong symbols; application/bootloader imports remain 214/34.
The manifest is unchanged and `make sources-check` passes.

The compiled pair body is 134 bytes versus the native 124-byte body;
the four wrappers compile to six bytes each. This is C reconstruction
progress, not byte identity or provider qualification. Physical sensor
transfers, conversion behavior, general concurrency, timing, complete
private-stack/fault identity, final firmware linking and boot integration
remain separate proof boundaries. No G2 gate or source-plan entry changes.

Exact source, stock, REA, build and probe bindings are in
[the machine-readable review](temperature-c-pair-review.json).
