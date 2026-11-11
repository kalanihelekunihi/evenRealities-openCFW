# RTC UTC offset accessor reconstructed in pure C

The naked assembly definition of `r1_time_utc_offset_get` was removed from
`native_calendar_frames.c`. Its sole linked implementation is now
`r1/src/application/board/native_time_utc_offset.c`, which uses the existing
typed `time_calendar_state` and a volatile signed-halfword load. A static
assertion checks the native field offset of eight. No new state owner, guard,
fallback or inline assembly was introduced.

Locked stock entry `0x8adb4` loads state address `0x20016ac4`, reads a signed
halfword at +8 and returns it in R0. The new C function preserves that signed
32-bit return. The source state continues to be owned by its existing module.
The standalone accessor unit participates in composition without enabling the
separately excluded, duplicate backend-calendar implementations.

`build/goal-r1-rtc-offset-c/verify.py` passes 131,072 paired cases (262,144
executions): every 16-bit field value with both clear and set APSR states.
It executes stock and C, checking R0 sign extension, one two-byte state read,
absence of RAM writes, R1-R12 preservation, stack restoration/untouched stack,
APSR and interrupt masks. A deliberate unsigned-load variant is rejected for
`0x8000`: native returns `0xffff8000`, while that variant returns `0x00008000`.

The official qualifier selected the complete 12-byte C body/literal at the
independently named native entry, recovering the compiler-marked state-address
relocation and verifying full linked byte equality. Only this official
selection was appended to the canonical plan; prior selections were preserved.
The two remaining executable sections in the old calendar-frame object retain
identical bytes. The unrelated excluded backend-calendar source is unchanged.

The full build `build/sources-goal-r1-rtc-offset-c-final/report.json` compiles
565 R1 units without failures or duplicate strong symbols. Import sets remain
206 application and 34 bootloader. `make sources-check` passes. A fresh hybrid
build adds 12 source-built bytes: 3,735 source-built, 642,425 retained executable
and 248 resource bytes. The application still matches the locked hash
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
[Machine evidence](rtc-offset-c-accessor-review.json) binds execution, negative
control, qualifier output, plan delta, build report and hybrid results by hash.

This accessor's exact qualification does not establish whole-image source
completeness. Physical RTC operation, concurrent updates and final source-only
placement/linking remain unproven. G2 workflow gates are unchanged.
