# Source closure for the reentrant newlib string formatter

The normal R1 composition now supplies the four remaining selected newlib
formatter imports: _ctype_, _localeconv_r, _dtoa_r and __ssprint_r. Nine
unchanged pinned newlib 3.3.0 compilation units provide character tables,
C/ASCII locale and conversions, multiprecision decimal conversion, the shared
string output helper and an explicit reentrant _snprintf_r entry. The upstream
INTEGER_ONLY/STRING_ONLY vfprintf variant owns __ssprint_r once; the existing
floating _svfprintf_r remains its separate upstream variant. The snprintf
unit renames its generic alias to r1_newlib_snprintf to avoid changing the
selected native public snprintf. No native formatter implementation or caller
is replaced, and no precompiled library is linked.

`runtime/newlib_assert_adapter.c` supplies newlib's assertion port through the
existing Nordic SDK assertion fault protocol: fault ID SDK_ASSERT, PC zero
and a file/32-bit-line record. The protocol has no function/expression fields.
The adapter remains nonreturning if an application fault-handler override
unexpectedly returns. It adds no new reset policy; the selected SDK handler
retains its existing fatal policy. Actual device reset is not proven here.

The probe links normal participating C objects, including _snprintf_r,
_svfprintf_r, __ssprint_r, dtoa/mprec, locale/classification, software double
math, the newlib allocation adapter, native heap and memory operations.
The scheduler suspend/resume and terminal Nordic fault handler are modeled;
there are no formatter, math, locale or allocator placeholders and no mapped
stock code. The selected native public snprintf is deliberately not the test
entry: it has different recovered large-number formatting behavior.

All 135 independently expected format cases pass at capacities 0, 1, 8, 64
and 1024, repeated over six sequences (4050 calls). Cases cover signed and
unsigned integers, long long, widths/precision, strings, hexadecimal floats,
fixed/scientific/general decimal formats, signed zeros, very small subnormals,
large finite doubles, infinity and NaN. Expected finite decimal strings come
from independent host formatting of exact hexadecimal C input literals;
integer/hex/special outputs are fixed expectations. Exact return lengths,
truncation, termination and output guards are checked, along with saved
core/VFP registers, SP and interrupt masks. The reentrant state and heap remain
live across the sequence. Free bytes are 48080 after the first pass and 47920
after each of the next five: caches stabilize after warming, rather than
returning all memory between calls. This is bounded evidence for this workload,
not a general allocator-fragmentation or formatting-exhaustion guarantee.

Four explicit assertion calls verify file/line forwarding (including lines
above 65535) and nonreturn when the modeled fault handler returns. Four compiled
defects are detected: wrong decimal point, wrong remaining output capacity,
wrong assertion fault ID and truncated line. A clean final baseline runs after
the defects. Default C/ASCII locale and FP environment are used. Arbitrary
format/precision combinations, non-C locales, live RTT, scheduler concurrency,
physical fault/reset behavior and extreme heap exhaustion remain unverified.
The existing native fatal allocation-exhaustion policy is retained.

All 799 R1 units compile (717 application, 82 bootloader) without failures or
duplicate strong symbols. Application imports fall from 101 to 97 with none
added; strict source bootloader linking succeeds with its 22 linker-metadata
imports. The 787 prior nongenerated objects are unchanged, including native
public formatter wrappers and the allocator. The two generated bootloader
objects retain allocated bytes and relocations despite metadata changes.
Global source checking retains the unrelated unlisted G2
resident_rom_thumb_set.S failure. Full application linking remains unfinished;
no source-plan qualification or stock byte-identity claim is made.
