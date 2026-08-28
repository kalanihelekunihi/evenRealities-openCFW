# G2 bootloader instance register-service source closure

The complete authenticated 376-byte service at
`[0x00422BA8,0x00422D20)` now compiles from maintained MIT C at
its exact stock address. Its installed SHA-256 is
`983a7c399b4e7e44e7e6c49d2da6112709588c7f005820cc5cf2a4a0a82300d`;
the unrelocated body is
`f2498e3d8c1622d3e29caf4f5363243450e13a3903d245ca6c74c29e93afec28`.
Both reviewed Cortex-M55 profiles reproduce it exactly under five strict call
relocations. Three direct callers enter at `0x0041F66E`, `0x0041F86C`, and
`0x0041F912`; the next executable body begins at `0x00422D20`.

The service validates the instance header and action, derives resource
`index + 11`, and implements both register-transfer directions. Action zero
can reject an inactive transfer, enters the retained resource seam, optionally
sets the revision-gated clock bit, routes mode enable, writes seven consecutive
configuration words plus the eighth word at register offset `0x48`, and clears
the active byte. Actions one and two optionally read the same register set,
set the active byte, clear the revision-gated clock bit, route mode disable,
invoke retained teardown with `-1`, clear register offset `0x30`, and release
the resource. Status values 0, 2, 6, and 7 and low-byte argument behavior are
preserved.

Strict calls bind retained resource-enter `0x0041BF84`, source-owned mode
enable/disable routes `0x004222F0`/`0x00422364`, retained teardown
`0x00423700`, and retained resource-exit `0x0041C17A`. Literal-pool values
authenticate the `0x0016E361` threshold, revision register `0x4002000C`, clock
register `0x400201B0`, and bank base `0x40039000`.

`runtime_hw_instance_service_422ba8.c` is 8,051 bytes with SHA-256
`920b11582bd4f4f6a4dac12dea1bd8835c878e71088afbe71b99805b6df02eb6`.
Six host tests pin body/callers/pools/successor, cover validation and short
paths, all four register banks, both action classes, transfer/no-transfer
behavior, clock thresholds, field preservation, and teardown ordering, and
cross-compile both profiles.

Canonical accounting becomes 21,453 source-owned, 16,528 generated patch, 16
alignment, and 125,843 retained official bytes, including 362 cave bytes and
5,866 exact in-place bytes across 261 source-owned functions and 201 patch
sites. Provider and byte-identical unsigned-package hashes remain unchanged.
The 4,620,102-byte flash plan has SHA-256
`e5cbb6380db3f81e5dbb15d3e4ccfb7cefcb4e6fcf31d37b1407b8adb2746500`
with 6,638 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. MMIO register layout, revision gating, clock
effects, mode routing, teardown, resource arbitration, and cold-boot behavior
require authorized responsive G2 evidence. That evidence is unavailable: no
authorized responsive right temple exists and the left temple must remain
stock. These claims are explicitly hardware-blocked, and firmware-wide
functional completeness is not claimed.
