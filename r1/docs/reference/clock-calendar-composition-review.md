# RTC calendar providers in normal composition

Three existing candidate units now participate in the normal R1 composition: `native_clock_calendar.c`, `native_clock_port.c` and `clock-calendar/selected-calendar.c`. Together they provide nine previously excluded definitions: calendar read/write callbacks, both inverse converters, RTC write/bind/read requests and the two backend wrappers. The bootstrap unit remains compile-only pending its own ABI validation.

The calendar-write callback now calls the existing `r1_time_utc_offset_get` provider instead of reading the state field directly. Stock entry `0x50d8a` retains the input pointer in R4, calls that accessor, converts the calendar with the returned signed offset, then writes the epoch with request offset zero. It returns 1 for nonnull input regardless of RTC write status. The read callback at `0x50d64` obtains an epoch and tail-calls conversion with offset zero. Null input/output returns zero without provider calls. No extra validation or changed status policy is introduced.

Validation uses normal Clang objects:

- **640 paired callback cases / 1,280 executions** model timestamp, offset, conversion and request providers. They compare the native call sequence and arguments, read tail-call stack restoration, write SP minus 8 and active R4, callback mutations, null handling, sign extension, full return registers and flags, saved state and guards.
- **3,610 paired inverse cases / 7,220 executions** execute actual stock/C inverse conversion. They cover recovered year/month/day/time validation, leap dates, signed and full-width offsets, null input, unchanged packed input, return epoch and final saved registers/masks.
- **408 paired integrated cases / 816 executions** execute ten actual C units: callbacks, forward/inverse conversion, offset getter, timestamp/write requests, memset and registry dispatch. Only registered RTC snapshot/write operations are modeled. The fixture compares request contents, native registered-operation stack depths, packed output, zero write offset, status policy, guards and final ABI state.

Invalid calendars retain stock's behavior: the inverse adapter can produce zero, and the nonnull write callback still submits that epoch. Negative controls reject an incorrect write offset, an incorrect callback return status and the preceding implementation's missing offset-provider boundary.

All **575 R1 units** compile and compose without new failures or duplicate strong symbols. Nine new strong providers are verified; the existing strong providers remain. All 574 other compiled objects are unchanged. Application/bootloader imports remain **164/34**. Enabling the request unit resolves the write-request dependency introduced by the newly participating calendar callbacks. Only the three manifest link flags and their validation notes change; profiles and other manifest fields remain unchanged.

REA read the native 70-byte callback window. The provenance index adds the two confirmed callback entries and points inverse-converter ownership to the current selected C unit. Thirty-five generic qualification variants compile. The initial GCC matrix compiled 27/28: the unchanged UTC-offset accessor inherited Clang's `-Oz`, which GCC9 rejects. An explicit supported `-O2/-Os/-Og` matrix compiles all 21 variants. Normal manifest flags are unchanged. All selected regions were already admitted; no new exact regions are claimed.

The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. The source plan remains unchanged at 4,023 source-built bytes (including assembly and data), 642,137 fallback bytes and 248 resource bytes. Source completeness remains false.

Execution proof is separate from GCC compilation/qualification. Inverse internal scratch order and stack aliases, raw caller-clobbered registers/flags in integrated cases, arbitrary faults, concurrency and physical peripherals remain unverified. This enables tested source components; it does not establish a complete final firmware link, bootstrap correctness or physical RTC operation.

Evidence: [clock-calendar-composition-review.json](clock-calendar-composition-review.json). Local probes and rejected variants are under ignored `build/goal-r1-clock-calendar-composition/`; final normal report `build/sources-goal-r1-clock-calendar-composition-final/report.json`, hybrid report `build/hybrid-goal-r1-clock-calendar-composition/build-report.json`.
