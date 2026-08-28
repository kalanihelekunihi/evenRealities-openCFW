# G2 bootloader four-instance hardware-service initializer source closure

The complete authenticated 212-byte initializer at
`[0x00422AD4,0x00422BA8)` now compiles from maintained MIT C at
its exact stock address. Its SHA-256 is
`e9be5104b2affd8296338018098cf8b3f634e45617cff59c745d52983c3c6f65`
under both reviewed Cortex-M55 compiler profiles, with no relocations. The sole
direct caller is `0x0041F744`; the two-byte predecessor alignment and the next
executable entry at `0x00422BA8` are separately pinned.

The function validates a four-entry index and output pointer, rejects an
already initialized compatible handle, selects a `0x11C`-byte instance from
the pool rooted at `0x20024400`, preserves its high header byte while installing
the `0x00EA9E06` type bits, records the index, clears the authenticated state
fields, sets byte `+0xDE` to one, publishes the handle, and returns the stock
status values 0, 5, 6, or 7. Literal-pool words `0x01EA9E06`, `0x20024400`,
and `0x00EA9E06` are authenticated at `0x004233E0`, `0x004233E4`, and
`0x00423430`.

`runtime_hw_instance_init_422ad4.c` is 3,916 bytes with SHA-256
`05addb583ca84c006df193494adb224480cbc23297c201092b987bac52873ead`.
Five focused tests pin the body, callsite, pools and boundaries; cover invalid
arguments, all four slots, field-level preservation/initialization, compatible
handle rejection and incompatible handle replacement; and cross-compile both
reviewed profiles.

Canonical accounting becomes 21,077 source-owned, 16,528 generated patch, 16
alignment, and 126,219 retained official bytes, including 362 cave bytes and
5,490 exact in-place bytes across 260 source-owned functions and 201 patch
sites. Provider SHA-256 remains
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`.
The byte-identical 4,745,418-byte unsigned package remains
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.
Its 4,619,359-byte flash plan has SHA-256
`28bc8efdfe3ce66f76001c3c7dd58190ff5e945cabff97fa7558627cdbe629a7`
with 6,637 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. SRAM ownership, concurrent initialization,
peripheral side effects, cold-boot lifecycle, and caller integration require
authorized responsive G2 hardware evidence. That evidence is unavailable: no
authorized responsive right temple exists and the left temple must remain
stock. These physical claims are explicitly blocked, the next retained
executable body begins at `0x00422BA8`, and firmware-wide functional
completeness is not claimed.
