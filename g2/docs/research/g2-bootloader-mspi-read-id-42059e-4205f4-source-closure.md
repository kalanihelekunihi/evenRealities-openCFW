# G2 bootloader MX25U25643G JEDEC-ID source closure

The complete authenticated 86-byte entry `[0x0042059E,0x004205F4)` now routes
to `open_cfw_bootloader_mspi_read_id_42059e` in maintained clean-room C. The
stock SHA-256 is
`76375cc441140c585f955d99008ebaf467fb7eb54882cc857cff55b7aaa0f48e`;
the 2,853-byte source SHA-256 is
`3e279abf9a149279da6fdb72009884e62224800e7843d487a803e5fa7293e1b6`.

Stock disassembly and host tests pin command `0x9F`, a three-byte receive
buffer, status propagation, failure-only logging at line `0x2D8`, preservation
of the caller's output word on failure, and successful packing as
`byte0 << 16 | byte1 << 8 | byte2`. Direct-call scanning identifies the timing
scan at `0x0042003C` and public initializer at `0x004204C4`; both enter through
the replaced authenticated address. The retained transaction seam begins at
`0x004205F4`, and the retained logger seam is `0x004176CE`.

Apple Clang emits a relocation-free 100-byte leaf at offset 12,068/runtime
`0x0043739C`, SHA-256
`cbd9055d50d62d9ff1208d66fd3e62785e8e20021b311a318d22c1aab4bf4dbe`.
Linux Clang emits a relocation-free 100-byte leaf at offset 12,048/runtime
`0x00437388`, SHA-256
`da002d908de4dfb93c9c93a69f6039ce55769ebe8503031cdf5507faa7b5837f`.
The Apple/Linux overlay identities are 12,168 bytes /
`324e199c6fba626e6b264555a42266b4048f99417b8b8973de0f868395d7a9fa`
and 12,148 bytes /
`fb847985f4771452c0e616207e71edfe56c438515ea36e3d1dde6ae4d481fc87`.
Provider identities are 160,768 bytes /
`e90099f27ae281cd342579b5c51e6902c4701d271b79eed8178d368ccfc902a8`
and 160,748 bytes /
`6230811e643262ec2aaac9bd20824e633ea2e061f87d05f28d7b2a1343f01399`.

Canonical accounting is 12,153 source-owned, 13,466 generated patch, 16
alignment, and 135,133 retained official bytes across 178 routed functions,
159 relocated leaves, and 176 patch sites. Unsigned Apple/Linux packages are
4,742,346 / 4,518,336 bytes with SHA-256
`53b039b04aabdb53e78cfb9b793162d72c8997de85412d7eff1f6ae9da8dd37c` /
`5e06ca3604364f4c4036dd688b2cbbb9541e1eaab94fcb9089d3f40fffcaab3b`;
their flash plans contain 6,507 / 3,454 placed regions and two unresolved
hardware regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live command acceptance, JEDEC byte order, MSPI/XIP/external-flash behavior,
and cold boot validation are blocked because no authorized responsive right G2
temple is available; the left temple must remain stock. Executable bodies at
and after `0x004205F4` remain software gaps, so firmware-wide completeness is
not claimed.
