# G2 bootloader two-word bitmap-helper source closure

The three complete authenticated helpers at `[0x004215AE,0x00421632)` now
compile from maintained clean-room C at their exact stock addresses. Apple
clang 21 and Homebrew clang 22.1.8 reproduce all 132 installed bytes exactly,
so the provider and unsigned package payloads do not change.

The helpers operate on the authenticated table rooted at `0x20026E74`. Each
low-byte selector names one two-word (64-bit) row:

- `[0x004215AE,0x004215DC)` returns whether either word is nonzero. Its
  46-byte body has SHA-256
  `11a6cf814c1a66760a988880dac541c55419e26aa1f4c7ef2de27b9a0d7e019f`.
- `[0x004215DC,0x004215FE)` tests one bit, narrowing the bit index to eight
  bits before selecting word 0/1 and shift 0..31. Its 34-byte body has
  SHA-256
  `8dc0a88874cc74f9148e7ae8b6e70f50b7cd1f732db5b74982a8abcccb1bd6f5`.
- `[0x004215FE,0x00421632)` sums the population counts of both words and
  returns the low byte. Its 52-byte installed body has SHA-256
  `2c98fb87af946ccd169b0e0f8225c9455b682478941053f2a25da7ac6e23c689`.
  Its sole relocation is a reviewed `R_ARM_THM_CALL` at offset 30 to the
  exact source-owned population-count helper at `0x00421584`; the unrelocated
  body SHA-256 is
  `20ce988b2a2a8800a0e12ab177298cde413bdd1dd57e67e22c4abc82005ad6eb`.

`runtime_bitmap_helpers_4215ae.c` is 3,719 bytes with SHA-256
`2963fafa33288f0e2076dd3e46b0d427d1c5d7cda9d8b5279b0b41a48f82b9e8`.
The target branch fixes the recovered instruction spelling while the host
branch expresses the same table contract in portable C. Five focused tests
pin the complete bodies, table literal and popcount call; exercise empty,
nonempty, selector-narrowing, boundary-bit, two-word, and count behavior; and
compile all three leaves with both reviewed Cortex-M55 toolchains.

Canonical accounting becomes 15,775 source-owned, 16,528 generated patch, 16
alignment, and 131,521 retained official bytes, including 362 cave bytes and
188 exact in-place bytes across 209 source-owned functions and 201 patch
sites. Apple/Linux providers remain 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`;
unsigned packages remain 4,745,418 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,577,013-byte flash plan has SHA-256
`b3d6202b548907ee00c12279378c888dca7907405684910171dcb6af7d53ae24`
with 6,577 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The helpers' software contracts are exercised
offline and their installed bytes are exact, but live table ownership,
concurrent mutation, and downstream register/memory effects require authorized
hardware evidence. That evidence is unavailable because no authorized
responsive right temple exists and the left temple must remain stock.
Firmware-wide functional completeness is not claimed; the next retained
executable body begins at `0x00421632`.
