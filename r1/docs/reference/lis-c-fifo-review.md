# R1 LIS2DW12 FIFO reader C conversion

`r1_lis2dw12_fifo_read` now uses C instead of its naked assembly body at
stock `0x750E8`. It initializes a one-byte count, asks the canonical level
getter to update it, bounds a nonzero count by the unsigned request, calls
the burst reader and returns the count. Both transport statuses are ignored,
as in stock. When a nonzero level meets a zero request, the zero-length
burst call is retained. REA confirms the stock branch and call structure.

All 3,372 controlled comparisons pass. The successful-data sweep covers all
256 level-register bytes and requests around the masked six-bit count,
including zero, 255, 256 and UINT32_MAX. Further cases vary level and burst
callback errors independently. Another 108 probes leave the level callback's
destination untouched and vary incoming r3, requests and error codes; the
retained assembly getter reads its saved r3 scratch byte in that case. This
last result describes the compiled candidate, not a portable C guarantee
about an unspecified incoming register.

The comparisons cover callback identity/order, handle, register, length,
destination contents and returned count. Scratch buffer addresses are
normalized by role and recorded separately with callback stack depths;
stock and candidate differ in private stack layout. Callback mocks poison
r0–r3, while checks verify preservation of r4–r7 and entry SP. The level
getter's assembly remains unchanged. The FIFO source file itself now has
no inline assembly.

The compiled reader is 78 bytes versus stock's 52 and inlines the burst and
transport wrappers. No byte identity, complete fault-state or timing claim
is made. Physical accelerometer/I2C operation and startup context binding
remain untested. All 561 R1 units compile and both compositions succeed
without duplicate strong symbols; unresolved sets remain 238 application
and 34 bootloader. `make sources-check` passes for both trees. No source
qualification or workflow gate changed.

[lis-c-fifo-review.json](lis-c-fifo-review.json) binds native/candidate bytes,
build identities, REA data, comparison results and ignored probe hashes in
`build/goal-r1-lis-fifo/`. See the preceding
[burst conversion](lis-c-burst-review.md) and
[transport conversion](lis-c-transports-review.md) for their separate scopes.
