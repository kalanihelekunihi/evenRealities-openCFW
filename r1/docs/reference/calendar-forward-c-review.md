# RTC forward calendar conversion reconstructed in C

The 228-byte naked assembly forward converter at `0x5a7bc` is replaced by
`r1/src/application/board/native_calendar_forward.c`. It contains no inline
assembly. The older by-value generic implementation is removed rather than
kept as a second stock provider. Its public declaration and four C callers
now use the native pointer ABI; the existing assembly UTC adapter already
passes a pointer to its epoch word.

REA confirms the input epoch is loaded before output writes and reread for
weekday after the year/day/month stores. The signedness is unsigned 32-bit
throughout. C uses the recovered nine-word structure, volatile input/output
accesses and the stock write order: hour, minute, second, year, year-day,
day, month, weekday, zero tail. The Gregorian year walk starts at 1970 and
uses the divisible-by-4/100/400 rule. Month subtraction keeps the native
eight-bit counter. There is no inferred input-pointer guard.

The existing shared fallback at native address `0x20016ae4` and 24-byte
dual month table at `0x99c5c` now have C-owned storage with dedicated sections.
The table is ordinary calendar data; its compiled bytes match the locked
stock table. Null output selects the fallback, whose pointer is returned.
The normal composition resolves both previously missing data symbols,
`unix_to_broken_down_fallback` and `month_days_forward`; no imports are added.

The ignored probe `build/goal-r1-calendar-forward-c/verify.py` passes 26,250
paired cases (52,500 executions). There are 24,546 ordinary cases spanning
month boundaries through the entire unsigned epoch range, full-word boundary
values and random epochs, each with explicit or fallback output. An independent
Python datetime oracle checks every ordinary result. Another 1,704 cases
overlap the epoch pointer with output words and adjacent guards, including
fallback storage. Ordered input/table reads and output writes, final buffers,
return pointer, preserved registers, stack restoration and interrupt masks
match stock. Private frames and caller-clobbered registers/flags are excluded.

A deliberate variant reusing the initial epoch for weekday fails when input
aliases output +0 with epoch `0x12345678`: stock rereads the written seconds
word and produces weekday four, while the snapshot variant produces three.
This is why a by-value input or hoisted read is insufficient.

An additional 1,120 integrated cases execute the actual native UTC adapter
with the C forward converter. They check its stack-pointer ABI, unsigned
offset wrapping, null-output return, packed eight-byte dates, surrounding
guards and preserved registers against stock and a datetime oracle. This
does not model electrical RTC operation.

The full build `build/sources-goal-r1-calendar-forward-c/report.json` compiles
566 R1 units without failures or duplicate strong symbols. Imports decrease
from 206 to 204 application; bootloader imports remain 34.
`make sources-check` passes.
[Machine evidence](calendar-forward-c-review.json) binds REA, source, verifier,
negative control, integration results and the build report by hash.

The compiled C converter is 386 bytes and is not byte-qualified. The canonical
source plan is unchanged. A fresh hybrid after the shared-header change still
matches stock, retaining 3,735 source-built bytes and 642,425 executable
pull-through bytes. It does not admit this new converter as byte-identical.
Sampled full-word epochs and explicit overlap tests
do not prove every possible input/pointer; invalid pointers, concurrent
mutation, physical RTC behavior, final placement/linking and complete source
reconstruction remain unproven. G2 workflow gates are unchanged.
