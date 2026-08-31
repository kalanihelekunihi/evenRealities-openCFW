# G2 bootloader public MSPI device-configure source closure

## Result

The public `am_hal_mspi_device_configure` entry at
`[0x00424BE4,0x00425066)` is no longer represented by a raw executable-byte
transcript or credited only through retained stock. A structured, freestanding
C implementation now occupies the first 672 bytes at the authenticated entry
address. It returns before the remaining 482 stock bytes, so those bytes are
unreachable compatibility padding rather than an alternate implementation.

This is a software source closure, not a hardware-validation claim. Live MSPI
register, clock-source, DMA/TCB, XIP, attached-flash, warm-reset, and cold-boot
evidence is **blocked by unavailable physical evidence**. No flash, sign, reset,
MMIO, or other hardware operation was performed.

## Recovered ABI and behavior

The implementation validates the handle prefix and configured state, enforces
the module/device/frequency restrictions, performs the HFRC/HFRC2 clock
release/request lifecycle, selects the clock mux and divisor, programs the
device, DDR, XIP, instruction, boundary, DMA-count, and threshold registers,
updates the recovered state fields, invokes the private device-configure leaf,
and applies the XIP-off delay selector.

The public configuration ABI is byte-oriented. Compile-time assertions pin the
read instruction at offset `0x04`, DMA time limit at `0x14`, and DMA boundary at
`0x16`; two recovered reserved bytes at offsets `0x12..0x13` prevent host ABI
padding from silently changing the target layout.

## Object admission

Both reviewed profiles produce the same object:

| Property | Value |
|---|---:|
| runtime address | `0x00424BE4` |
| compiled bytes | 672 |
| unrelocated SHA-256 | `7dcafb51bf0566d580cd6de6f1d90e473d78da82db97bd6e12f15be0da2d9658` |
| relocated SHA-256 | `344f6705aac2638cd47e64b83a76058b16f00dc9640ccb6edd9ea9d52072cf56` |
| alignment | 2 |
| strict relocations | 6 `R_ARM_THM_CALL` records |
| replaced stock-prefix SHA-256 | `6bab21c83cc97181377b3cdc7a318e3a959326eb97946eae14e0278571365a94` |
| complete 1,154-byte stock SHA-256 | `baf84c7a01d10528a6367c12651b215274674bbfe206d9d26edddda387d85658` |

The exact call relocations bind the admitted object to the already-routed MSPI
clock generator, clock release/request services, private device-configure leaf,
and XIP-off delay selector. The three authenticated callers remain
`0x0042032E`, `0x0042033E`, and `0x00420E36`.

## Verification

The host oracle covers all 23 frequency classes, module restrictions,
clock-release and clock-request failure propagation, same-source lifecycle
elision, invalid-frequency ordering, and handle/configured guards. The audit
also compiles both target profiles, validates every relocation, checks the
upstream AmbiqSuite semantic anchors, verifies manifest routing, and enforces
bootloader byte conservation.

Canonical Apple provider accounting is now 29,775 source-owned, 16,490
generated, and 117,575 retained bytes. The next executable frontier is
`am_hal_mspi_enable` at `[0x00425066,0x004250F0)`.
