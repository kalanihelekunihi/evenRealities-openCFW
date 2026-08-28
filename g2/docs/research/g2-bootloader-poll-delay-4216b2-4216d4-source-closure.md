# G2 bootloader bounded poll-delay source closure

The complete authenticated helper at `[0x004216B2,0x004216D4)` now compiles
from maintained clean-room C at its exact stock address. Apple clang 21 and
Homebrew clang 22.1.8 reproduce all 34 installed bytes exactly.

The helper accepts a volatile activity byte and volatile 32-bit remaining
counter. While both are nonzero it invokes the retained delay service at
`0x0041D1C0` with duration 10, then decrements the counter. A flag change
during the delay still consumes the current counter unit before the next
condition check. A zero counter or inactive flag causes no delay and no
mutation. The complete installed stock body SHA-256 is
`eb69fa2933ef30723f342fbc330927d681c6ca5d2ac077b77bf5e7ed1689a795`.

`runtime_poll_delay_4216b2.c` is 1,340 bytes with SHA-256
`c8bcb3ab9f12a8aa50222c4a8ef56525a90aacf5549da96a655b0b2ed269bbd3`.
Its sole executable relocation is a reviewed `R_ARM_THM_CALL` at offset 10 to
the retained authenticated delay service. The unrelocated body SHA-256 is
`f8c611938fd6436eab1873dc9ca2ab43dc3ecf0dda4f632304c1c63c97a51f26`.
Five focused tests pin the body, call and successor boundary; exercise both
short circuits, full counter exhaustion, and asynchronous flag clearing; pin
the constant duration 10; and compile with both reviewed Cortex-M55
toolchains. Three direct callers are authenticated at `0x00421BB4`,
`0x00421D38`, and `0x00421E9C`.

Canonical accounting becomes 15,937 source-owned, 16,528 generated patch, 16
alignment, and 131,359 retained official bytes, including 362 cave bytes and
350 exact in-place bytes across 211 source-owned functions and 201 patch
sites. Apple/Linux providers remain 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`;
unsigned packages remain 4,745,418 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,578,404-byte flash plan has SHA-256
`9fce38cd17a480199e97cc3b624b679b98d3d5111db06af281b2f2d96eb41a13`
with 6,579 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The loop contract is exercised offline and
the installed bytes are exact, but real delay timing, asynchronous producer
behavior, volatile-memory visibility, and caller integration require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x004216D4`.
