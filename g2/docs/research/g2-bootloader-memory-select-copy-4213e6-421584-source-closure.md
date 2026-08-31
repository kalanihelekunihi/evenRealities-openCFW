# G2 bootloader mapped-memory selector source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The authenticated mapped-memory service and its odd-selector wrapper at
`[0x004213E6,0x0042156E)` now route to maintained freestanding C placed wholly
inside their own generated replacement space. The following 22-byte
alignment/literal pool at `[0x0042156E,0x00421584)` is authenticated retained
data, so the executable software frontier advances to `0x00421584`.

## Recovered contract

- The 354-byte primary body has SHA-256
  `989242545e69349bd0ff976d0bdd47f5800523263ad0f2c35fa06c0a68ea5127`.
  It accepts `(kind, offset, size, destination)`, returns `6` for a null
  destination or kind outside `0..5`, returns `5` when the 32-bit wrapped
  `offset + size` exceeds the selected capacity, and returns `9` when the
  security bit forbids a selected external mapping.
- Kinds `0` and `1` choose compact or full mapped windows from control bits 4
  and 3. Kinds `2` and `3` select the compact windows directly; kinds `4` and
  `5` select the full windows directly. The recovered sources are rooted at
  `0x42000000`, `0x42002000`, `0x42004000`, and `0x42006000`, with word-scaled
  indices and calls to the exact in-place identity/threshold mapping helpers.
- A successful request copies exactly `size` bytes through the authenticated
  copy provider at `0x0041D28A` and returns zero.
- The 38-byte wrapper has SHA-256
  `3b5bbbf5927b1c40733445a47ac8ddcec46ba52837fd94cf3ee0dc20c28d9e72`.
  It accepts only low-byte selectors `1`, `3`, and `5`, returning `6` for the
  other values before forwarding the original arguments.

`runtime_memory_select_copy_4213e6.c` is 5,058 bytes with SHA-256
`749ff5c621d6524681087923b02518f66719c5acd3782e5d3aa635dd4c4b1909`.
Five focused tests cover the authenticated spans and callers, all selector
paths, capacities, security gating, overflow behavior, byte-copy forwarding,
wrapper filtering, and Cortex-M55 compilation.

## Placement and build closure

Apple clang 21 and Homebrew clang 22.1.8 both emit the same relocated bodies:

- primary cave `[0x004213EC,0x004214C8)`: 220 bytes, SHA-256
  `a9b45dceaaa8672d78e771bcd023dbdf609255960d1bd8640dba198081e19ce9`,
  with three strict calls to `0x004213D8`, `0x004213DA`, and `0x0041D28A`;
- wrapper cave `[0x004214C8,0x004214E6)`: 30 bytes, SHA-256
  `4f68053211831432222da8104d9efa5c3419bf62267a054dd0f13e0681f503ae`,
  with one strict tail branch to the primary cave.

The primary stock entry branches six bytes forward to its cave; its remaining
replacement bytes authenticate and contain both leaves plus generated NOP
fill. The wrapper stock entry branches backward to its cave. Fail-closed cave
checks authenticate the containing stock bodies, generated-NOP subspans,
runtime addresses, relocation contracts, and compiler digests.

Canonical accounting is 15,601 source-owned, 16,528 generated patch, 16
alignment, and 131,695 retained official bytes, including 362 cave bytes and
14 exact in-place bytes across 205 source-owned functions and 201 patch sites.
Apple/Linux providers are 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`.
Apple/Linux unsigned packages are 4,745,418 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,573,512-byte canonical flash plan has SHA-256
`e8f4afaf8b838eaa359360309d36ae5c36b664b28973fe011cc84c51a678a58c`
with 6,572 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Register configuration, security-state
selection, mapped-memory visibility, copy behavior, concurrency, and cold-boot
qualification remain blocked because no authorized responsive right temple is
available and the left temple must remain stock. Firmware-wide functional
completeness is not claimed; the next retained executable body begins at
`0x00421584`.
