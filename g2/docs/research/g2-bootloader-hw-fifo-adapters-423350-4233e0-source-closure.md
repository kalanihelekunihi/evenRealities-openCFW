# G2 bootloader FIFO-adapter source closure

## Scope

This increment source-closes the two authenticated Thumb bodies immediately
after the per-instance FIFO read/write/drain cluster in the G2 2.2.6.10 S200
bootloader:

| Function | Stock range | Bytes | Exact SHA-256 |
|---|---:|---:|---|
| critical-section FIFO snapshot | `[0x00423350,0x00423390)` | 64 | `c50cb54905aafef204f60cc0a71919f9701853167579f85c789ee7729b8e9892` |
| critical-section FIFO pump | `[0x00423390,0x004233E0)` | 80 | `a51ed43345c464477c7c15d21737e0eb5ec937c962de4369b7da174c5a1088d7` |

The maintained implementation is
`components/bootloader/core_overlay/runtime_hw_fifo_adapters_423350.c`, size
4,898, SHA-256
`66ca0c33418fbd49d07373f3e0a00e83ed36e5a8d4c847315f8976d52a01b9de`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce both bodies exactly.

## Behavior and link closure

The snapshot adapter enters a retained critical section, reads at most 32 FIFO
bytes, passes successful data to the descriptor consumer, maps an empty
successful consume to `0x08000001`, restores the saved interrupt token, and
returns status. Its unrelocated body SHA-256 is
`6a4b712d02969e2e2c161c8b392c7ef9e393e08de49976c6110ec7c645f0b941`;
strict calls are at offsets 8, 22, and 40.

The pump enters the same critical section, checks register-bank status bit 5,
pulls one byte at a time from the retained descriptor, writes each byte through
the source-owned FIFO writer, stops on full/empty/error, restores the saved
interrupt token, and returns status. Its unrelocated body SHA-256 is
`b23e18ca00aae4fd82e98a98d7f2b2d031e0789c417e21fcbba44d6ee4991c46`;
strict calls are at offsets 10, 42, and 58.

Five host tests pin stock bodies and literals, error/empty/status behavior,
byte pumping, token restoration, and dual target compilation. Canonical
provider accounting becomes 22,607 source-owned, 16,528 generated patch, 16
alignment, and 124,689 retained official bytes, including 362 cave bytes and
7,020 exact in-place bytes across 275 source-owned functions, five caves, 72
exact in-place leaves, and 201 patch sites. The byte-identical package remains
4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, FIFO, descriptor, interrupt, or MMIO
operation occurred. The earliest retained executable body remains the 570-byte
initializer at `0x0042308E`. Live register-bank, FIFO, descriptor, interrupt,
concurrency, timing, and peripheral qualification is explicitly blocked by the
absence of authorized responsive right-temple hardware and a controller/golden-
capture fixture. Firmware-wide functional completeness is not claimed.
