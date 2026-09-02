# G2 bootloader CLKGEN HFADJ enable source closure

The authenticated bootloader entry `[0x00426C58,0x00426C72)` controls bit 0 of
the CLKGEN HFADJ register at `0x40004044`. The stock ABI interprets only the low
input byte as a boolean, preserves every other register bit, writes the updated
value, and returns zero.

`runtime_clkgen_hfadj_enable_426c58.c` expresses that contract as freestanding
MIT C. Apple clang 21.0.0 and Homebrew clang 22.1.8 both emit the same 24-byte
Thumb leaf with no relocations. Its embedded literal is the authenticated HFADJ
register address. The compiled body occupies `[0x00426C58,0x00426C70)`; the
authenticated stock return at `[0x00426C70,0x00426C72)` is retained as an
unreachable two-byte tail. There is no direct call or stored Thumb entry pointer
into that tail.

Host tests verify disable, enable, low-byte truncation, preservation of all
non-control bits, and the zero return value. Both canonical provider builds and
the exhaustive post-MSPI ledger verify the target leaf and tail. No live MMIO,
package transmission, signing, reset, erase, or flash operation was performed.
Live-device qualification is blocked by unavailable physical evidence.
