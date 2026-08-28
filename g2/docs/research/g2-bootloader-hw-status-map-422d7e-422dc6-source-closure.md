# G2 bootloader per-instance status-map source closure

The authenticated relocation-free body at `[0x00422D7E,0x00422DC6)` now
compiles exactly from maintained MIT C under both reviewed
Cortex-M55 profiles. The 72-byte body and unrelocated image have SHA-256
`87a7c4d6609c8566af29c21281d2746ac1af8dc81b95867b99defa5fd6e64261`.
The source `runtime_hw_status_map_422d7e.c` is 1,702 bytes with SHA-256
`748f5a8c95b74e2908080e136c743dde54f6e2842d43641e63b2e201ac8258a7`.

The function reads register offset `0x3C` from the selected `0x1000`-stride
instance bank rooted at `0x40039000`, combines the value with the caller's
mask, and maps the first set authenticated status bit by priority. Bits 6, 7,
8, 9, 10, and 12 return `0x08000006` through `0x0800000B`; if none is set,
the caller-provided fallback is returned. The six result literals are retained
at `0x00423768` through `0x00423778` and `0x0042382C`. No stored-pointer
ingress or external direct call was identified; computed control flow remains
possible and the exact fixed-address body preserves that ABI.

Five focused tests pin the body, result pools, preceding datum, and successor;
exercise each mapped bit from both the argument and MMIO model across all four
banks; verify priority and fallback behavior; and cross-compile both target
profiles. The four-byte datum `0x20000002` at
`[0x00422D7A,0x00422D7E)` remains authenticated non-executable data.

Canonical provider accounting becomes 21,615 source-owned, 16,528 generated
patch, 16 alignment, and 125,681 retained official bytes, including 362 cave
bytes and 6,028 exact in-place bytes across 264 source-owned functions and 201
patch sites. The provider and byte-identical unsigned package hashes remain
unchanged. The 4,622,934-byte flash plan has SHA-256
`94d1d455c823fe27ccaffff91d44a7839c4b4b14396f5a71342849c6e1c78df9`
with 6,642 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body starts
at `0x00422DC6`. Live MMIO status, bank ownership, peripheral flags, controller
timing, and cold-boot qualification are explicitly blocked by unavailable
authorized responsive G2 evidence; firmware-wide functional completeness is
not claimed.
