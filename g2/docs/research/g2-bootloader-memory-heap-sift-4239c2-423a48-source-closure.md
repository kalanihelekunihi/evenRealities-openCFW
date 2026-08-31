# G2 bootloader Floyd max-heap sift source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The 134-byte helper at `[0x004239C2,0x00423A48)` has exact SHA-256
`e209d49057309bdeb649246ad594a18f708db52ff4893c7aad55cad8464edc34`.
Maintained source `runtime_memory_heap_sift_4239c2.c` is 3,296 bytes with
SHA-256
`7aa89646803c202da9f515e61235a243f0834a9fb93882fd55460af6a836ca91`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 both emit the exact 134-byte
body. Its unrelocated SHA-256 is
`593ed9c7ea06f66d428c418715f9c979327adf3ce50cb402412d3917aaba4b53`;
strict `R_ARM_THM_CALL` relocations at offsets 70 and 122 bind the
source-owned swap helper at `0x00423864`.

The recovered contract is `sift(base, start, count, width, compare)`, where
`count` is the exclusive element bound. The helper uses Floyd's max-heap
method: it descends through the larger child, including the exact left-only
boundary at `child == count`, then repairs upward while the moved element is
greater than its parent. Seven focused tests pin the authenticated body and
successor, exclusive bound, both-child selection, multi-level descent,
upward repair, subtree isolation, no-op boundary, comparator order, and both
target compilation profiles.

Canonical provider accounting is 24,133 source-owned, 16,528 generated patch,
16 alignment, and 123,163 retained official bytes across 291 source-owned
functions, 179 relocated leaves, five caves, and 88 exact in-place leaves.
The provider remains 163,840 bytes with SHA-256
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`.
The byte-identical package remains 4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.
Its deterministic 4,648,863-byte flash plan has SHA-256
`34174d5c0e21d3fadf725d23a1d3a3942ee9de42428d69a32007e71647dd9cf2`
with 6,679 placed, zero unresolved, six container-only, and six protected
regions.

No signing, flashing, reset, boot, device, SRAM, or MMIO operation occurred.
This helper is fully qualified offline, but firmware-wide completeness is not
claimed. The earliest retained executable remains `0x0042308E`; the sequential
frontier is the retained sort routine beginning at `0x00423A48`. Physical
qualification remains blocked by unavailable authorized responsive right-
temple evidence.
