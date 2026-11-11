# RTC UTC adapter logic moved into C

The full assembly adapter at `0x8af40` is replaced by a C kernel in
`r1/src/application/board/native_calendar_utc.c` and a 14-byte ABI bridge in
`native_calendar_frames.c`. The bridge retains the native eight-byte R4/LR
save and 40-byte scratch allocation, passes its address as the fourth kernel
argument, and restores the original frame. Arithmetic and packed-field copy
logic are C. The two superseded generic UTC implementations were removed.

REA confirms that the native adapter stores a wrapping 32-bit
`epoch + offset_minutes * 60` at scratch +36 and passes that word's address
with the scratch base to the forward converter. Null output returns zero
without conversion. A null converter result also returns zero. Otherwise,
stock reads a halfword year at +20, then byte fields at +16,+12,+8,+4,+0,+24,
writing the packed output after each read. The year adds 1900 and the month
adds one, truncating at their native output widths. C uses volatile accesses
to preserve those widths and ordering when output aliases the returned data.

The adapter kernel is a separate translation unit from the forward converter,
retaining the native converter-return check in this non-LTO build. The forward
converter and kernel keep explicit call boundaries. A plain automatic scratch
object would not preserve the converter's native pointer arguments or output
aliases into that frame; the small bridge retains this observable storage.

The ignored probe `build/goal-r1-calendar-utc-c/verify.py` passes 4,950 paired
cases (9,900 executions). It models the converter to isolate adapter behavior:
null/frame/alternate results, arbitrary returned words, full-word arithmetic,
null/ordinary output and aliases into returned/native scratch storage. It
compares ordered memory access widths/values, the exact scratch pointers and
epoch word, final memory, return status, stack restoration, callee-saved
registers and interrupt masks. The compiled kernel is 74 bytes plus the
14-byte bridge; this is not a native-byte-identity claim.

A deliberate variant snapshots the seconds byte before writing the packed
year. It is rejected when output equals the returned buffer: a returned year
124 becomes packed 2024, whose low byte overwrites the later seconds source.
Stock returns seconds 232 there, while the hoisted variant retains seven.

Another 2,800 cases execute the actual C converter and C adapter, including
output aliases at native scratch offsets 0,16,32, full-word offset wrapping,
null returns and packed-output guards. Ordinary dates are independently
checked with Python datetime. The forward converter's 26,250 stock comparisons
also pass against the current object, including its own overlap and ordered
memory checks.

The full R1 build at `build/sources-goal-r1-calendar-utc-c-split/report.json`
compiles 567 units without failures or duplicate strong symbols. Import sets
remain 204 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](calendar-utc-c-frame-review.json) binds REA, source,
execution probes, negative control and the normal build report by hash.

The canonical source plan is unchanged and these adapter bodies are not
byte-qualified. Private C kernel frames, caller-clobbered registers/flags,
invalid pointers, aliases into saved-register words, concurrent mutation,
physical RTC behavior and complete source-only placement/linking remain
unproven. G2 workflow gates are unchanged.

The subsequent [direct C adapter review](calendar-utc-direct-review.md) supersedes this bridge and private helper. It preserves the native provider frame directly in C and adds actual-forward-converter integration plus GCC9 adapter validation.
