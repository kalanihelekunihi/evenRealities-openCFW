# LIS interrupt route setter C extraction

`lis2dw12_pin_int1_route_set` at stock address `0x756da` now delegates its
read, update, write and error sequence to `r1_lis_int1_route_body` in
`native_lis_aux.c`. The field computation continues to use the existing
attributed ST C helper. REA analysis and native execution support the change.
The 128-byte native routine becomes a 10-byte frame bridge and a 78-byte C body
with the current compiler, in addition to the existing field helper.

The bridge preserves incoming R2/R3 at entry SP-24 and SP-20. Reads of registers
0x24 and 0x3f use the low bytes of those words in reverse order. A successful
read need not fill its output, so substituting initialized C locals would
change behavior. C consumes the explicit frame, reads the live route byte,
then the two scratch bytes in native order, and updates only the low byte at
SP-24. It writes the caller's original route buffer to 0x23 and the updated
scratch byte to 0x3f. Every nonzero I/O status stops the sequence immediately.
The native pop restores both modified words to R2/R3.

The ignored `build/goal-r1-lis-route-set/verify.py` probe passes 1,728
stock-versus-C scenarios. It executes actual transport wrappers on both sides
and the actual C field helper. Cases sweep all 256 values of each computation
byte, every I/O failure position, full-width statuses, non-writing reads,
route buffers aliased with either scratch byte, callback changes to retained
buffers, and live transport callback/handle replacement. Checks include
ordered context and scratch accesses, I/O pointers and bytes, return values,
R2/R3 restoration, output guards, callee-saved registers, SP, interrupt masks
and eight-byte callback alignment. The other three function bodies in this
file are unchanged.

The complete R1 build compiles 562 units without failures or duplicate strong
symbols. Imports remain 227 application and 34 bootloader. Exact stock,
source, manifest, REA, integrated-source and probe bindings are recorded in
[the machine-readable review](lis-c-route-set-review.json).

Final bus callbacks are modeled. The C helper adds callback stack depth below
the preserved scratch words. Physical interrupt routing, sensor timing,
complete fault-state equivalence, final linking and byte identity remain
unproven. No provider selections or G2 workflow gates change.
