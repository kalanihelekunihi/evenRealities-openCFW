# Padmux check C candidate

The stock routine at package 0xfb44 / runtime 0x102065b8 rejects negative pin
or function arguments, calls the getter, converts its result to an unsigned
byte, and returns zero on equality or -1 otherwise. The C candidate preserves
that conversion. Consequently a nonnegative invalid pin whose getter returns
-1 can compare equal to function 255. This observed behavior must not be
silently changed by adding a different input bound.

Native macOS compilation produces 36 bytes within the 36-byte stock region.
The candidate is unregistered and decoded helper/return/ABI qualification is
pending. The getter binding is 0x1020658c; no getter bytes are imported into
this candidate. SDK interface/object provenance is recorded by the builder.

The decoded stock/C checker now passes 9,324 cases with modeled getter values
and caller-register clobbers, checking its optional eight-byte frame and
preserved registers. Four focused tests cover negative-argument early return,
invalid positive pin matching 255, byte truncation, and wrong helper target.
The verifier builds its getter prerequisite explicitly. Actual decoded getter
composition and evidence pinning remain pending before source admission.

Decoded checker/getter composition now passes 2,592 combinations of stock/C
outer and leaf routines, pins, expected functions and MMIO word values. It
checks actual getter read traces and returned values at the call boundary,
including early paths that skip the call. The 9,324 modeled-return cases and
six focused tests also pass after adding the callback interface. Getter leaf
ABI is checked independently; physical pad effects remain unproven.

The admission verifier now pins both builders and both decoded verifiers plus
composition, exports the linked checker artifact, and accepts this function's
finite source contract. All ten getter/checker mutation tests pass. It remains
unregistered pending the current SPI integration; hardware qualification is false.
