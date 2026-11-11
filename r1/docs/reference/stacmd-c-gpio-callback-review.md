# STACMD GPIO callback C types and raw result

`board/native_stacmd_transmit.c` now uses the actual void GPIO callback
types from the hardware configuration. Previously `line_call` invoked
those callbacks through a `uint32_t (*)(uint32_t)` cast, and the ignored
low call used the same mismatched prototype. The low call is now correctly
void. Calls whose native machine R0 must remain observable use a two-byte
`BX R1` gateway: R0 already contains the pin and R1 the void callback.
The explicit ARM ABI adapter captures raw R0 without a mismatched C call.

Raw instructions and REA for native zero-bit helper `0x5cbf0` show high,
output, high, low, a 13-iteration four-NOP loop, then a tail branch to the
live high callback. The dispatcher at `0x5cbe4` selects that helper or the
52-iteration one-bit helper at `0x5cc2c`. C retains those pulse loops and
live callback/pin reloads. REA's pseudocode omits the NOPs; raw instructions
and execution establish their counts.

The probe passes 2,224 stock/C comparisons through bit drive, seven/eight-
bit writes and idle. Of these, 1,111 execute actual probe-only void C
callbacks that write ordinary RAM. Other cases model GPIO return words and
clobber caller-saved registers. Cases cover all byte values, selected and
random full-width values/headers, live pin and high-callback replacement,
and modeled recovery-delay calls. The source gateway bytes are `0847`.

Checks compare raw R0, GPIO sequence and pin arguments, configuration and
callback RAM bytes, callee-saved registers, SP, interrupt masks and callback
alignment. Each driven zero bit executes 52 NOPs and each nonzero bit 208,
in both native and C runs. Parity retains its exact compiled body. The
other 561 source units are unchanged.

All 562 R1 units compile without failures or duplicate strong symbols;
eligibility and imports remain unchanged at 211 application / 34 bootloader,
and `make sources-check` passes. Exact bindings are in
[the machine-readable review](stacmd-c-gpio-callback-review.json).

This is C callback correctness and bounded execution evidence. The new
gateway and private frames change call overhead; equal NOP counts do not
prove equal cycles or physical pulse widths. Actual Nordic GPIO, recovery
delay, wire operation, arbitrary faults, exceptions, concurrency, final
boot/linking, provider qualification and whole-image byte identity remain
unproven. No G2 gate or source-plan selection changes.
