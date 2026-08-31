# G2 bootloader register-service source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and authenticated bodies

This increment source-closes three executable per-instance register services
around the retained alignment/literal island `[0x004236FA,0x00423700)`.

| Function | Range | Bytes | Exact SHA-256 |
|---|---:|---:|---|
| register OR | `[0x004236CE,0x004236FA)` | 44 | `8d9b9730cd66a1de3b8886d2a29f71dc72f72bb61a252a10a45227dc309756b7` |
| register write | `[0x00423700,0x0042372A)` | 42 | `9af271cb1237dcd8aa9147adad8a333ce2c70532fba9e090bc9f1b8a2fa390b7` |
| register query | `[0x0042372A,0x00423764)` | 58 | `d2a8d31be1192d40a4240d1f392856b268a0005cf45bcc7f3fb769c0e17d518b` |

The maintained source is `runtime_hw_register_services_4236ce.c`, size 4,339,
SHA-256 `7168dda0bc531878aee6e43bf2928048ca945d9b55ec65e3cdb71e878ba5f4ec`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce all three bodies exactly
without relocations.

## Behavioral closure

All three services mask the instance type to 25 bits and require `0x01EA9E06`.
The register bank is selected by the word at instance offset `0x28` and the
retained `0x40039000` base with a `0x1000` bank stride. The first service ORs a
caller mask into register `+0x38`; the second writes register `+0x44`; and the
third returns `+0x3C` or `+0x40` according to the low byte of its selector.
Invalid types return status two. No direct `BL` caller or stored entry pointer
to these three entry addresses occurs in the authenticated bootloader image.

Five host tests pin all exact bodies, retained literal boundaries, bank
selection, bit preservation, writes, both query selectors, invalid-type
failure, and dual target compilation. Canonical provider accounting becomes
23,473 source-owned, 16,528 generated patch, 16 alignment, and 123,823 retained
official bytes, including 362 cave bytes and 7,886 exact in-place bytes across
285 source-owned functions, five caves, 82 exact in-place leaves, and 201 patch
sites. The 4,643,183-byte flash plan has SHA-256
`9618a0d0f2ad5dfb572479320d8ec8e15a011a600edcd8d9bbd542c3625c4d66`
with 6,671 placed and zero unresolved regions. The byte-identical package
remains 4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, register, SRAM, or MMIO operation
occurred. The earliest retained executable body remains the 570-byte
initializer at `0x0042308E`; the next retained executable begins at
`0x0042377C` after the 24-byte retained register/literal table. Live register
effects, bank selection, concurrency, interrupt ordering, and peripheral
behavior are explicitly blocked by the absence of authorized responsive
right-temple hardware and a controller/golden-capture fixture. Firmware-wide
functional completeness is not claimed.
