# G2 bootloader memset wrapper source closure

The authenticated bootloader entry `[0x00426C10,0x00426C24)` is the conventional
`memset(void *destination, int value, size_t count)` ABI wrapper. Seven direct
Thumb callers target the entry. The stock body preserves the destination,
reorders `value` and `count`, calls the Arm EABI byte-fill provider at
`0x0041560C`, and returns the original destination.

`runtime_memset_wrapper_426c10.c` expresses that contract as freestanding MIT C.
Apple clang 21.0.0 and Homebrew clang 22.1.8 both emit the same 18-byte Thumb
leaf. Its sole relocation is an `R_ARM_THM_CALL` at offset 10 to the already
source-owned byte-fill provider. The compiled body occupies
`[0x00426C10,0x00426C22)`; the authenticated stock return at
`[0x00426C22,0x00426C24)` is retained as an unreachable two-byte tail. There is
no direct call or stored Thumb entry pointer into that tail.

Host tests verify standard argument order, low-byte fill behavior, zero-length
behavior, and destination return semantics. Both canonical provider builds and
the exhaustive post-MSPI ledger verify the target leaf and tail. No MMIO,
package transmission, signing, reset, erase, or flash operation was performed.
Live-device qualification is blocked by unavailable physical evidence.
