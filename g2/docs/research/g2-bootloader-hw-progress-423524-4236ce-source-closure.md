# G2 bootloader progress-service source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and authenticated bodies

This increment source-closes both executable progress services in
`[0x00423524,0x004236CE)`.

| Function | Range | Bytes | Exact SHA-256 |
|---|---:|---:|---|
| primary progress | `[0x00423524,0x00423608)` | 228 | `be77b63cd268da7b27fcb99a8046654e1e527ed65c8118430e7d540bc0fe46c7` |
| secondary progress | `[0x00423608,0x004236CE)` | 198 | `0c57e8cf946a5c825784001ef88eb8e0a9c94dc820a29b0e9ed9636aebb7996d` |

The maintained source is `runtime_hw_progress_423524.c`, size 8,552, SHA-256
`8e70e23e666da3f20ada7012c14e011e21661f9c502032edd7d2a23bbf133e4d`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce both bodies exactly.
The unrelocated body hashes are
`d6f705b25736c1fb55bb87d2ed2b8d996636fb38e10663fcaa74c3c722020ec5`
and `908d9409e4c9c6aa549ba80b23f9d06c63c259e91f2652567a55635e9701d1b1`.

## Behavioral and link closure

The primary service enters a critical section while active, advances either a
descriptor-backed or FIFO-backed transfer, publishes progress, clears the
active byte at completion, and reports completion or descriptor exhaustion
through the registered callback. Descriptor-backed operation also pumps the
FIFO after a non-aborted pass. The secondary service optionally snapshots the
FIFO, performs the corresponding descriptor or FIFO read, publishes progress,
and applies the same completion/exhaustion callback convention.

Strict relocation contracts pin primary calls to critical entry, descriptor
consume, FIFO write, and FIFO pump, and secondary calls to FIFO snapshot,
critical entry, descriptor read, and FIFO read. Six host tests pin both exact
bodies, callback results, progress mirrors, completion, empty-descriptor
termination, FIFO pump/snapshot behavior, interrupt-token restoration, and
dual target compilation.

Canonical provider accounting becomes 23,329 source-owned, 16,528 generated
patch, 16 alignment, and 123,967 retained official bytes, including 362 cave
bytes and 7,742 exact in-place bytes across 282 source-owned functions, five
caves, 79 exact in-place leaves, and 201 patch sites. The 4,640,329-byte flash
plan has SHA-256
`d9fe2b2028f168a1f3e54a1a26f0783c436173c319c143e0835b9bd5c0e7ca23`
with 6,667 placed and zero unresolved regions. The byte-identical package
remains 4,745,418 bytes
with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, FIFO, descriptor, interrupt, DMA,
callback, SRAM, or MMIO operation occurred. The earliest retained executable
body remains the 570-byte initializer at `0x0042308E`; the next retained
executable after this cluster begins at `0x004236CE`. Live register, FIFO,
descriptor, interrupt, concurrency, DMA, callback, and peripheral behavior is
explicitly blocked by the absence of authorized responsive right-temple
hardware and a controller/golden-capture fixture. Firmware-wide functional
completeness is not claimed.
