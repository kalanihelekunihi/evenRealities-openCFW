# R1 low/high-pass coefficient generation in C

`native_gomore_low_high.c` supplies stock `0x717ac`, resolving
`r1_gomore_coefficients_low_high_native`. The [receipt](gomore-low-high-c-review.json)
binds source/object, REA instructions, replay, controls and qualification. It adds
no assembly or persistent RAM. The generic guarded callback utility keeps its
behavior under the `_checked` name.

The implementation retains signed order conversions, non-fused multiplication
and multiply-add/subtract, native operand order, descending complex polynomial
updates, live feedforward reloads and high-pass sign changes. All math calls occur
128 bytes below entry, matching stock. Positive orders one through four are
covered. Larger positive orders overflow the native scratch arrays and are outside
this proof. Nonpositive orders omit unused reads of uninitialized private scratch;
observable math calls and stores remain checked.

The production object passes **1,376 native/C cases**, including **15 faults**,
with actual stock cosine, sine and power executing. Another **5,476 cases**, also
including **15 faults**, model math returns and caller-saved clobbers, including
NaNs, infinities, subnormals and signed zero. Checks include exact outputs/write
order, invalid accesses, FPSCR, preserved registers and FP registers, arguments and
provider stack depth. Nine compiled defects are rejected, including fused math,
wrong gain/product signs, polynomial subtraction and wrong power selection.

The C configuration caller passes **524 cases**, including **22 faults**, with
the production C coefficient object and native math. It covers orders one through
four, signed mode words and publication of the count after coefficient generation.
Bandpass setup still executes stock and remains an unresolved production import.
The wider optical estimator is unfinished.

This unit disables both GCC if-conversion passes. An earlier replay layout skipped
a constant move following a conditional memory-write IT block while a differently
linked layout passed. A branch-based profile passes both layouts and caller replay;
that experiment does not establish physical instruction behavior. Private scratch
bytes remain excluded. The underlying math source units still contain assembly;
this candidate does not claim that those dependencies are fully C.

The normal build compiles **693 units** with no failures or duplicate strong
symbols: **619 application / 74 bootloader**. All **691 prior units** outside the
renamed generic owner retain source/object hashes. Application imports fall from
181 to **180**, with **34 bootloader imports**. Qualification selects no replacement.
The canonical plan and hybrid totals remain 4,369 source-built executable bytes,
641,791 stock executable bytes and 248 resource bytes. Hybrid equality is not a
complete C rebuild or source byte identity. No physical validation is claimed.
