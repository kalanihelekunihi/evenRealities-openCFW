# Respiratory history helper C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-modulo-c-review.md) records single-owner consolidation and production replay.

The first coordinator stage, respiratory update `0x60680` (734 bytes), calls
history helper `0x94938` (110 bytes). An experimental C implementation of that
lower dependency compiles without inline assembly. The
[receipt](gomore-modulo-c-investigation.json) binds REA bytes, parent pseudocode,
source/object and replay under `build/goal-r1-gomore-modulo-c/`.

The native ABI is `(record, secondary_word, primary_word)`, returning the raw
pointer record+40. Counter is an unsigned byte at offset 40. Only multiples of
five publish samples: primary at 41+counter/5, then secondary at
45+((fresh_counter/5)&1). Sentinel replacement applies only when the full input
word equals 255; 511 and UINT_MAX instead store their low byte unchanged.
Finally the helper rereads counter and stores `(counter+1)%20`. Counter 255
therefore becomes 16, rather than wrapping to zero before the modulus.

The current generic checked helper has a length parameter, rejects counters
20..255, narrows both arguments to bytes and returns bool. It cannot be used as
a direct stock provider. Stock can write primary slots as far as byte 92 for
counter 255. Primary and secondary destinations overlap for some noncanonical
counters, and the native write order determines the final byte.

**12,544 native/C cases** pass against independent byte expectations: all 256
counter values crossed with seven primary and seven secondary words, including
sentinel, low-byte lookalikes and word extremes. Complete 112-byte guarded views,
raw return, saved integer registers and final SP agree. The C candidate preserves
live counter reads and adds no state/range guard or persistent RAM.

Six independently compiled defects are rejected: byte-narrowed sentinel
comparison, wrapping before modulus, counter-range guard, incorrect primary or
secondary slot, and wrong raw return. Forty-two boundary cases also match,
including 28 faults, on invalid access address/size, earlier writes, RAM-tail
contents and completed raw return. Fourteen boundary cases complete normally.

The actual native respiratory caller prefix passes **3,884 paired executions**
with the native helper versus this C helper. Coverage crosses all 256 initial
counters with elapsed extremes, missing-fill limits, sentinel codes and unavailable
flags. The fixture stops at estimator entry `0x69834`; complete history bytes,
all six estimator argument words, pointed-to zero scratch values, 96-byte native
parent frame depth and FPSCR agree. This is caller-prefix evidence, not proof of
the remaining respiratory algorithm or estimator behavior.

Before promotion, consolidate the generic checked helper owner and run normal
production-object replay, build and qualification checks. No source manifest or canonical image
selection changes at this checkpoint; the normal build remains 685 units with
179 application and 34 bootloader imports.

Respiratory update itself also calls estimator `0x69834`, gap reset `0x883d4`,
positive-history counting `0x967a0`, peak/index selection `0x760ec`, selected
aggregation `0x76120`, square root and software FP conversions/arithmetic. Its
pseudocode contains omitted arguments and raw-bit range predicates; instructions
and replay must govern their C interfaces. Physical execution, source-only final
linking and byte identity remain unproven.
