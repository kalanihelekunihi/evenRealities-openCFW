# R1 bandpass coefficient generation in C

`native_gomore_bandpass.c` supplies stock `0x711b4`, resolving
`r1_gomore_coefficients_bandpass_native`. The [receipt](gomore-bandpass-c-review.json)
binds source/object, REA instructions, direct/caller replay and qualification.
No assembly or persistent RAM is added. The guarded generic callback utility
keeps its behavior under the `_checked` name.

The C implementation retains ordered live cutoff loads between math calls,
non-fused multiply-add/subtract and operand order, the coupled gain recurrence,
descending complex polynomial updates, feedforward publication and sign changes.
A sixteen-byte volatile private reservation makes math calls occur 160 bytes
below entry, matching stock. It adds one private write; private frame bytes remain
excluded from replay. Positive orders one and two are covered, plus zero and signed
minus one. Other orders can overflow native scratch or expose uninitialized private
words and are outside this proof. Unused uninitialized private reads are omitted
for the covered nonpositive orders.

The production object passes **1,108 native/C cases**, including **18 faults**,
with stock cosine, sine and tangent executing. A further **6,260 cases**, including
**18 faults**, model math returns, caller-saved clobbers and input mutations.
Cases include signed zeros, subnormals, NaNs/infinities, reversed/equal cutoffs,
cutoff/state aliases and FP control settings. Checks include outputs, exact write
order, invalid access address/width, FPSCR, preserved integer/FP registers, math
arguments and provider depth. Eleven compiled defects are rejected, including
hoisted cutoff loads, fused arithmetic, wrong recurrence and wrong frame depth.

The C configuration caller passes **524 cases**, including **22 faults**, with
both C generators and native math. The actual optical caller passes **1,344
gap/reset/warmup cases** with C reset/configuration/coefficients and the previously
reconstructed append/compaction helpers. It executes 384 C resets, 5,088 compactions
and 5,088 appends. Bandpass arguments, parameter bits and pointers, state writes,
FPSCR and native root returns agree. The heavy optical estimation path remains
unfinished and is not covered here.

The normal build compiles **694 units** without failures or duplicate strong
symbols: **620 application / 74 bootloader**. All **692 prior units** outside the
renamed generic owner retain source/object hashes. Application imports decrease
from 180 to **179**, with **34 bootloader imports**. Both coefficient-generator
imports now resolve. Underlying math sources still contain assembly.

Qualification selects no replacement. The canonical plan and hybrid totals stay
at 4,369 source-built executable bytes, 641,791 stock executable bytes and 248
resource bytes. Hybrid equality is not a complete source-only link or source byte
identity. Physical hardware behavior remains unverified.
