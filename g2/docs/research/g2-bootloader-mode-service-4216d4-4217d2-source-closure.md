# G2 bootloader mode/configuration service source closure

The complete authenticated service at `[0x004216D4,0x004217D2)` now compiles
from maintained clean-room C at its exact stock address. Apple clang 21 and
Homebrew clang 22.1.8 reproduce all 254 installed bytes exactly.

The service accepts a null or fixed `0x02DC6C00` instance, rejects other
instances with status 5, and requires the controller seam for the fixed
instance or returns 7. When no configuration is supplied it queries retained
service `0x00426C4E`, merges the returned low 12 bits into bits 8..19 of the
authenticated default word `0x0025B800`, and uses that local 12-byte
configuration. Query failures return before interrupt masking.

The transaction then saves interrupt state, queries source-owned bitmap row 4,
and selects the authenticated apply/disable policy. Busy-state transitions
start with status 3 and accept only null/fixed current/target states. Apply
failure invokes the stored fallback word; idle target changes disable the
mode and clear two auxiliary state cells. Success copies 12 configuration
bytes for a nonnull instance, publishes the current instance and readiness
byte, and restores the saved interrupt mask. Failure does not publish state.

`runtime_mode_service_4216d4.c` is 7,030 bytes with SHA-256
`978a3249f0305b48d64f9dfa854b95f8d864579f4ca0b2ab6fa3e692dfa929c3`.
Its eight reviewed `R_ARM_THM_CALL` relocations bind the query, critical-save,
source-owned bitmap count, disable, apply/fallback, and source-owned copy
seams. The unrelocated body SHA-256 is
`d3f2882e4d5af4dd661039eb78603c3904ee3ac48bb2c1d0de790a626e391938`;
the installed stock SHA-256 is
`0cd7003be718ce1986083724a97a682e58e6623d4a579da5a272a4c34df85036`.
Seven focused tests pin the complete body, literals, dispatcher caller and
successor; exercise validation, query/default merge, early query failure,
busy apply/fallback, idle disable/clear, publication and interrupt restore;
and compile with both reviewed Cortex-M55 toolchains.

Canonical accounting becomes 16,191 source-owned, 16,528 generated patch, 16
alignment, and 131,105 retained official bytes, including 362 cave bytes and
604 exact in-place bytes across 212 source-owned functions and 201 patch
sites. Apple/Linux providers remain 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`;
unsigned packages remain 4,745,418 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,579,118-byte flash plan has SHA-256
`a5193f45000c8cfcc122610a6e9cfe359931aacc005bb9b1d749d3f4c02300f0`
with 6,580 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The transaction and error ordering are
exercised offline and installed bytes are exact, but interrupt timing,
controller/register behavior, state-cell ownership, and physical mode changes
require authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x004217D2`.
