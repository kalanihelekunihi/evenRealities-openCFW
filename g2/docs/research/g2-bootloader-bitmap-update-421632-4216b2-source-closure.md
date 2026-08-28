# G2 bootloader bitmap-update source closure

The complete authenticated helper at `[0x00421632,0x004216B2)` now compiles
from maintained clean-room C at its exact stock address. Apple clang 21 and
Homebrew clang 22.1.8 reproduce all 128 stock bytes exactly with no executable
relocation, so provider and unsigned package payloads do not change.

The helper mutates the same authenticated two-word table rooted at
`0x20026E74` as the preceding query helpers. It narrows all three inputs to
their low bytes, rejects selector values `>= 7` or bit indices `>= 57` with
status 6 and no write, selects word 0/1 and bit 0..31, sets the bit when the
narrowed enable byte is nonzero, clears it otherwise, preserves all other
bits, and returns zero after a valid update. The complete stock body SHA-256
is `bc7fc361719841b4cd3b48adad0bb774fe817371892b0a9cbe4e8744c5ec2a8e`.

`runtime_bitmap_update_421632.c` is 3,011 bytes with SHA-256
`6dfd71fa0b99c592e84066b4877eb151dbb4b27ce6135899e08b4296c6ebe87b`.
The target branch fixes the recovered instruction spelling while the host
branch expresses the same validation and read-modify-write contract in
portable C. Five focused tests pin the complete body, table literal and
successor boundary; exercise validation and low-byte narrowing; cover bits
0, 31, 32 and 56; verify set/clear and unrelated-bit preservation; and compile
with both reviewed Cortex-M55 toolchains.

Canonical accounting becomes 15,903 source-owned, 16,528 generated patch, 16
alignment, and 131,393 retained official bytes, including 362 cave bytes and
316 exact in-place bytes across 210 source-owned functions and 201 patch
sites. Apple/Linux providers remain 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`;
unsigned packages remain 4,745,418 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,577,708-byte flash plan has SHA-256
`7ffaee3c38fba6872efdaf94580d199a4e4facc3d569766cb35e77777f9c2c23`
with 6,578 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The read-modify-write software contract is
exercised offline and the installed bytes are exact, but live table ownership,
concurrent mutation, and atomicity require authorized hardware evidence. That
evidence is unavailable because no authorized responsive right temple exists
and the left temple must remain stock. Firmware-wide functional completeness
is not claimed; the next retained executable body begins at `0x004216B2`.
