# G2 bootloader bounded memory-exchange source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and authenticated bodies

This increment source-closes two contiguous software-only helpers:

| Helper | Range | Bytes | Final SHA-256 | Unrelocated SHA-256 |
|---|---:|---:|---|---|
| two-buffer exchange | `[0x00423864,0x004238BA)` | 86 | `ad7509b25a0cfd0245ca73f96c5c84c4ed321d6676a184c9a4b00fca46658e08` | `115a62b4d96e01abae24036e352fe7e3fc7e4c3bdfb69c9163a1b0c84193a9cb` |
| three-buffer rotation | `[0x004238BA,0x00423928)` | 110 | `15ab5faaa76530e6ce93f1d9ece7899858802f1eb5a6a1cb42287c8966aba239` | `0e46dd234a9fa1d1039ea5411c09a0fec63c918879d9ca0f3bd83d3094777853` |

The maintained source is `runtime_memory_exchange_423864.c`, size 3,782,
SHA-256 `ebe95fae8429194095531fade5a988d15ef2d6f0f3f4162dae192a1c21f2667c`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce both bodies exactly.

## Behavioral and link closure

For sizes below 64 bytes, both helpers exchange bytes directly. At 64 bytes
and above, they use a 128-byte stack scratch area and repeat bounded chunks of
`min(remaining, 128)`. The two-buffer helper performs `A <-> B`. The
three-buffer helper performs `A <- C`, `C <- B`, `B <- A`. Zero length is a
no-op. Seven strict `R_ARM_THM_CALL` relocations bind the large-element paths
to the authenticated copy primitive at `0x0041568C`.

Four host tests pin both stock bodies and the 74-byte executable successor,
zero-length behavior, both sides of the 64- and 128-byte thresholds,
multi-chunk operation, bytes beyond the requested span, and dual target
compilation.

Canonical provider accounting becomes 23,845 source-owned, 16,528 generated
patch, 16 alignment, and 123,451 retained official bytes, including 362 cave
bytes and 8,258 exact in-place bytes across 288 source-owned functions, five
caves, 85 exact in-place leaves, and 201 patch sites. The 4,646,731-byte flash
plan has SHA-256
`d6ddc3470a69ae4b00ea43ae4cd8f7a511048e3934f9694d3974a634d21ed26e`
with 6,676 placed and zero unresolved regions. The byte-identical package
remains 4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, SRAM, or MMIO operation occurred.
These helpers are software-only and have complete offline behavioral and exact
binary evidence. Firmware-wide completeness is still not claimed: the
earliest retained executable body remains the 570-byte initializer at
`0x0042308E`, and the next retained executable after this sequential island is
the 74-byte rotation/move helper at `0x00423928`. Live hardware-dependent
qualification remains explicitly blocked by the absence of authorized
responsive right-temple hardware and a controller/golden-capture fixture.
