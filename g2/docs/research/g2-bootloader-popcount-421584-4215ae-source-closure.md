# G2 bootloader population-count source closure

The complete authenticated helper at `[0x00421584,0x004215AE)` now compiles
from maintained clean-room C at its exact stock address. Apple clang 21 and
Homebrew clang 22.1.8 both reproduce all 42 stock bytes exactly, so the
provider and unsigned package payloads do not change.

The stock body has SHA-256
`3e1aafd1c98933503de46a42099c9e0ea5b6af861f1edda36f8df25079ce834d`.
It implements the standard parallel 32-bit population-count reduction and
returns the low-byte count in `0..32`. Its sole direct caller at `0x0042161C`
adds the population counts of two words from an authenticated per-selector
table.

`runtime_popcount_421584.c` is 1,192 bytes with SHA-256
`f04d31d782b5254c75d5a479be1193561d807f611c549be2502516085ed1ff6b`.
The target branch fixes the recovered instruction spelling while the host
branch expresses the same unsigned algorithm in portable C. Three focused
tests pin the body/caller, cover boundary and 512 deterministic random values,
and compile with both reviewed Cortex-M55 toolchains. Both target objects are
42 bytes with no relocations and the stock SHA-256 above.

Canonical accounting becomes 15,643 source-owned, 16,528 generated patch, 16
alignment, and 131,653 retained official bytes, including 362 cave bytes and
56 exact in-place bytes across 206 source-owned functions and 201 patch sites.
Apple/Linux providers remain 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`;
unsigned packages remain
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and `9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,574,891-byte flash plan has SHA-256
`23b0b3a47a662696d5f26f05be7b375dece06726b2f5c3352f62bb199f5c814b`
with 6,574 placed regions.

No hardware operation occurred. This arithmetic helper is fully exercised
offline, but its table-backed caller and downstream register/memory behavior
still require later software closure and authorized hardware evidence.
Firmware-wide functional completeness is not claimed; the next retained
executable body begins at `0x004215AE`.
