# NV recovery report construction and sending in C

The C report builder, envelope sender and response helper replace the missing
report boundary at stock `0x7b634`, `0x7bbe8` and `0x839b4`. Existing cached-class
handles, CRC code, phone handle and protocol response API are reused.

The builder clears a 116-byte output, copies the first 74 serial-class bytes,
and appends battery type at 92, signed ADC calibration at 94 and ring size at 96.
It admits battery types 1–4, ADC values -500 through 500 except -1, ring sizes
6–15 and serial lengths 1–30. Invalid fields retain their native diagnostics.

The sender allocates 121 bytes, emits command 2 with a little-endian length and
Modbus CRC16, and sends the envelope through the existing response API. Invalid
local data is withheld. Every successful allocation is freed once. The response
helper preserves null admission, live phone lookup and 16-bit length wrapping.

All 1,356 stock/C comparisons pass under the stated return normalization. Every
one of the 686 native instruction bytes executes. Tests check output bytes,
validation edges, diagnostics, allocation failure, unaligned output, live handle
changes, wire CRC, cleanup and preserved ABI. Actual C memory, CRC, builder and
envelope functions execute; the final response interface is modeled. CRC is
also checked with an independent implementation.

Another 774 cases execute actual cached-class reads and check critical-section
balance, report admission and class-size mismatch handling. Two C-only cases
check defined output/cleanup after non-writing reads. Four compiled defects
changing ADC admission, battery admission, CRC span and cleanup are rejected.

The C reporter defines its return as zero, including allocation failure, rather
than expose incidental registers from void logging/free APIs. Reporter returns
are normalized in stock comparisons; builder and response-helper results are
compared exactly. Cached-read scratch is initialized instead of consuming old
private stack bytes.

All 854 units compile and both relocatable payloads compose. All 843 prior
nongenerated objects remain unchanged. Application imports fall from 65 to 64;
bootloader imports remain 22. R1 manifest validation passes. NV merge remains
unresolved. Physical persistence, radio delivery, full linking and boot remain
unverified. [Machine evidence](nv-recovery-report-c-review.json) binds sources,
REA, replays, negative controls and build reports.

The later [merge review](nv-recovery-merge-c-review.md) closes the merge dependency recorded as open above. Physical persistence and final boot remain unverified.
