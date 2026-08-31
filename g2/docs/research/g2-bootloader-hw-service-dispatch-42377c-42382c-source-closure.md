# G2 bootloader service-dispatch source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and authenticated body

This increment source-closes the 176-byte per-instance service dispatcher at
`[0x0042377C,0x0042382C)`, exact SHA-256
`2cbdef7278215a0c7195f2f1be71e0c9f945d4647d3d1bc1d15365cd6a52ad61`.
The maintained source is `runtime_hw_service_dispatch_42377c.c`, size 5,768,
SHA-256 `0cf432eabcd5692d74580f9d87451e6e00fe282b891673da1d7c1b772e62bda0`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce the body exactly. Its
unrelocated SHA-256 is
`6c0e2e8199552303b892ae2f6535266a27d25af5d1981a7963f25eeb8f4e6e11`.

## Behavioral and link closure

The dispatcher requires masked type `0x01EA9E06`. For an active service at
instance byte `+0x11B`, it optionally publishes a low-12-bit register-relative
progress value, routes flag bits 6 and 12 to shutdown/secondary-clear, maps a
bit-11 status and invokes the registered callback, clears the primary register
state, and clears active state. For an inactive service it routes flags `0x50`
to secondary progress, bit 5 to primary progress, and bit 0 to latch byte
`+0xDE`. Valid calls return one; invalid instances return two.

Six strict relocations pin shutdown `0x00422FDE`, secondary clear
`0x00422D4C`, retained status mapping `0x00422D7A`, primary clear
`0x00422D20`, secondary progress `0x00423608`, and primary progress
`0x00423524`. No direct `BL` caller or stored entry pointer to the dispatcher
occurs in the authenticated bootloader image. Five host tests pin the body and
surrounding pools, validation, active/inactive routing, mirroring, callback
arguments, cleanup, and dual compilation.

Canonical provider accounting becomes 23,649 source-owned, 16,528 generated
patch, 16 alignment, and 123,647 retained official bytes, including 362 cave
bytes and 8,062 exact in-place bytes across 286 source-owned functions, five
caves, 83 exact in-place leaves, and 201 patch sites. The 4,644,623-byte flash
plan has SHA-256
`8151fe29dbd1b22c69b72c96d01fc363ffbcd5e469e219cd105fe3f7172af7bd`
with 6,673 placed and zero unresolved regions. The byte-identical package
remains 4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, callback, register, SRAM, interrupt,
or MMIO operation occurred. The earliest retained executable body remains the
570-byte initializer at `0x0042308E`; the next retained executable begins at
`0x00423864` after a 56-byte retained literal/status table. Live interrupt,
register, callback, concurrency, progress, and peripheral behavior is
explicitly blocked by the absence of authorized responsive right-temple
hardware and a controller/golden-capture fixture. Firmware-wide functional
completeness is not claimed.
