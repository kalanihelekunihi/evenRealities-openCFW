# Padmux setter C candidate

The stock function at package 0xfb68 / runtime 0x102065dc accepts unsigned
pin IDs 0 through 32. It reads one word at 0xa0010090 + 4*(pin/8), clears
one four-bit field, writes the low nibble of the function argument into that
field, and calls padmux_check with the original arguments. A zero helper
result returns zero; any other result returns -1. Invalid pin IDs return -1
without MMIO or the helper call. Negative and oversized function values still
cause the write before the checker rejects them; the candidate preserves this.

Native macOS C-SKY GCC produces 76 bytes within the 84-byte stock envelope.
The SDK object/header identity is pinned to commit
8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 by the candidate builder. The object
is comparison evidence only and is not linked into the C candidate. Full
object relocation attribution and decoded MMIO/helper/ABI qualification remain
pending. This candidate is unregistered and is not hardware qualified.

Decoded stock/C execution now passes 12,432 cases spanning all valid pin IDs,
invalid boundaries, function nibble boundaries/negative values, four register
patterns, and four modeled checker results. Execution checks exact MMIO
addresses/order/value, original helper arguments, caller clobbers, optional
four-byte stack frame, and preserved ABI registers. Five tests pass, including
wrong-address and wrong-helper mutations, invalid-input behavior and a helper
hook observing the written word. Decoded checker/getter composition remains
pending; this is not source admission or physical pad qualification.

Decoded setter/checker/getter composition passes 12,096 combinations covering
all eight stock/C routine selections, valid and invalid pins, function values,
initial words, and both written and inverted readback states. It verifies that
failed readback returns an error without undoing the write. Seven focused tests
pass. The source-admission verifier now includes this composition, seven pinned
evidence files, a function placement row, and linked artifact export. Admission
covers the stated finite function contract; integration is still pending and
physical hardware qualification remains false.
