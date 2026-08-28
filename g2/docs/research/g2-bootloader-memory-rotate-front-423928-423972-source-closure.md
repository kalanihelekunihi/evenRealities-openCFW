# G2 bootloader rotate-to-front source closure

## Scope and authenticated body

This increment source-closes the 74-byte rotate-to-front helper at
`[0x00423928,0x00423972)`, exact SHA-256
`6e7615d2123f9cf87dcb9d1823cfe5613687eaae88ce8b5f88664c205d012e09`.
The maintained source is `runtime_memory_rotate_front_423928.c`, size 2,290,
SHA-256 `a8d25e818c8335d81ed196185dc0cbec5741c32fdd2fef27557258ebbeff38fc`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce the body exactly; its
unrelocated SHA-256 is
`b7107041f6cea9cb80739b31660fb1389f2011c8648a66c747f9c3f03f88f459`.

## Behavioral and link closure

The helper moves the width-byte element at the supplied last-element pointer
to the front and shifts the intervening span right. It processes widths in
bounded chunks of at most 128 bytes, preserving the original-width address
calculation across successive chunks. Two strict calls bind the authenticated
copy primitive at `0x0041568C`; one strict call binds the overlap-safe move
primitive at `0x004276BC`.

Four host tests pin the stock body and its 80-byte successor, zero and
first-element no-op behavior, small and threshold widths, multi-chunk widths,
untouched suffixes, and dual target compilation. The multi-chunk test also
guards the original-width calculation that differs from remaining length.

Canonical provider accounting becomes 23,919 source-owned, 16,528 generated
patch, 16 alignment, and 123,377 retained official bytes, including 362 cave
bytes and 8,332 exact in-place bytes across 289 source-owned functions, five
caves, 86 exact in-place leaves, and 201 patch sites. The 4,647,450-byte flash
plan has SHA-256
`99cd47d54664ac5e270fe43e987776719fb3753f53ca435fadd7e6d0fb83d0f3`
with 6,677 placed and zero unresolved regions. The byte-identical package
remains 4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, SRAM, or MMIO operation occurred.
This helper is software-only and has complete offline behavioral and exact
binary evidence. Firmware-wide completeness is not claimed: the earliest
retained executable body remains the 570-byte initializer at `0x0042308E`, and
the next sequential retained executable is the 80-byte comparison/exchange
wrapper at `0x00423972`. Hardware-dependent qualification remains explicitly
blocked by unavailable authorized responsive right-temple evidence.
