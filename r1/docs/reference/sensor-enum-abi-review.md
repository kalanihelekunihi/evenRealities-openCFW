# Sensor and RTC enum ABI audit

The remaining wide-enum linker attributes do not by themselves establish a
hardware-driver ABI defect. Five existing R1 candidates were compiled using
their configured `r1-application-6` profile and again with only
`-fshort-enums` added: `rtc_device`, `gxt310`, `qma6100`, `yhm2710`, and
`sensor_stream`.

Every allocated section's name, type, flags, size and bytes matched within
each pair. Every normalized relocation matched as well, including target
section, offset, relocation type, symbol name and explicit addend. Clang's
complete record-layout dumps were identical within each pair, covering
field offsets, sizes and alignment. ARM enum attributes intentionally differ
and were excluded from the executable/data comparison. Compiler identity,
input hashes and per-module results are in
[sensor-enum-abi-review.json](sensor-enum-abi-review.json).

These headers use explicit-width fields and pointers in their records.
GXT310 additionally exposes `gxt310_failure_operation` as a callback
argument. Its enum width changes from four bytes to one, although the current
provider emits only constants zero and one and produces identical code.
No other source currently names that enum type. A new callback consumer or
enum-valued storage must be checked explicitly; the provider comparison does
not prove those future cases compatible.

No compiler flags or reconstructed bodies were changed. This bounded result
does not justify suppressing warnings, changing every remaining wide-enum
unit, or treating the candidate APIs as stock-equivalent. The separate
[FlashDB repair](flashdb-abi-review.md) addressed measured native offsets and
execution counterexamples; no comparable discrepancy was found here.

Reproduction probes and raw layout dumps are under ignored
`build/goal-r1-sensor-abi/`. This audit does not establish physical peripheral
behavior, final firmware linking, source completeness or byte identity, and
does not change the G2 workflow gates or source qualification plan.
