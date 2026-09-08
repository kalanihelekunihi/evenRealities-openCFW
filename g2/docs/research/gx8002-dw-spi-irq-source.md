# DW SPI interrupt handler reconstruction

Current status: qualified 32-byte C candidate registered for integration.
All 4,644 decoded cases and five focused tests pass after the change below.
The earlier 40-byte limitation described in the history is resolved.

The stock function at package 0xf6fc / runtime 0x10206170 matches the
32-byte SDK spi_master_irq_handler section exactly. The C candidate reads the
context's register pointer at offset 4, then status at register offset 0x30.
Bit 1 causes an absolute word read at 0x38; bit 3 causes an absolute word read
at 0x3c. It returns zero and ignores the IRQ number. The meaning and mapping of
these low addresses remain unresolved; substituting controller-relative
addresses would change observed stock behavior without supporting evidence.

The native compiler rejected literal low-address C dereferences under its
array-bounds diagnostics. Linker-bound external volatile objects now express
those addresses without suppressing diagnostics or relying on an inferred
zero-sized C object. This emits 40 bytes, exceeding the stock 32-byte slot.
The candidate is unregistered and has no decoded qualification yet. It changes
no firmware bytes. Required next work includes placement, exact transaction
and ABI comparison, and investigation of the actual low-address mapping.

The decoded stock/C verifier now passes 4,644 cases. It checks read order,
status masks, preservation of the status snapshot despite values returned by
low-address reads, return zero, and the leaf ABI. Five focused tests pass,
including mutations of controller-relative address substitution, the second
mask, and a preserved register. The report hashes its verifier and builder.
This evidence does not resolve hardware address mapping, and the candidate
still exceeds its slot by eight bytes. It remains unregistered.

The current source uses literal volatile pointers with candidate-local
`-fno-delete-null-pointer-checks --param=min-pagesize=0`. The first option alone
did not resolve GCC array-bounds diagnostics; the second sets the minimum
page-size assumption used for warnings. Other warnings remain errors. This
expresses the observed low-address access without external-symbol literal
pools, producing 32 bytes (SHA-256
`770352405f41c74a6f1c1c3c213bb5167dd5da93c72116cfcc7b0fff2aeac6be`).
The regenerated decoded proof passes and the candidate is registered. These
compiler settings do not prove the physical address mapping or side effects.
