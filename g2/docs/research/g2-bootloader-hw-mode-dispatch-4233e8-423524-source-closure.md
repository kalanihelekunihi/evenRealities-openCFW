# G2 bootloader mode-dispatch source closure

## Scope and authenticated bodies

This increment source-closes every executable body in the mode-dispatch cluster
`[0x004233E8,0x00423524)`. The 20 bytes at `[0x00423430,0x00423444)` are
authenticated literal/register-base data rather than executable software.

| Function | Range | Bytes | Exact SHA-256 |
|---|---:|---:|---|
| four-mode dispatcher | `[0x004233E8,0x00423430)` | 72 | `55aca3e5c488f1f76de2b7d38129b7dbae64a1a97c9de9b466aef93788f7721d` |
| mode-zero wait | `[0x00423444,0x0042348E)` | 74 | `274da3564e8944b5355109d064af8bc74a1c69be2fa349865db47fe99ec4326e` |
| mode-one wait | `[0x0042348E,0x004234D8)` | 74 | `dbeaa29a43e7f7c9e92a611782d56c41adea8d11fca90f6921f4b70bbcb5cd72` |
| mode-two start | `[0x004234D8,0x004234FA)` | 34 | `67cc585ebb380f6e1f1c49d0855a82d0fe92f8d1f54bd3ddb466d0ad903a9eb5` |
| mode-three start | `[0x004234FA,0x00423524)` | 42 | `5b3f8d6b0e2f9010d42bfc9ef5fe5e9ba65e5791c7d0f2081e042eccfece1412` |

Maintained sources are `runtime_hw_mode_dispatch_4233e8.c`, size 5,807,
SHA-256 `d951a70f8366b68f5e37e9cc5c5787abd6f60c4ccb5159631f882d13d27e765e`,
and `runtime_hw_mode_wait_423444.c`, size 4,828, SHA-256
`1cf478d8e7e4dfd76a80b012b0100a3338dd549ac9c563cd94148cc46945b134`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce all five bodies exactly.

## Behavioral and link closure

The dispatcher masks the caller type word to 25 bits, requires
`0x01EA9E06`, reads mode byte `+0x34`, routes modes zero through three, returns
one for an unknown mode, and two for a null or mismatched context. The start
helpers clear a caller status word when present, call their independent primary
or secondary configuration latch, and progress only after a successful latch.
The wait wrappers propagate start failures, poll active bytes `+0x119` and
`+0x11A`, progress and delay by 1,000 units, allow `0xFFFFFFFF` infinite
timeouts, and clear the active byte with result four at a finite timeout.

Ten host tests across the two modules pin authenticated bodies/literals,
validation and all dispatch routes, independent latch/progress behavior, start
failure propagation, successful completion, finite timeout clearing, delay
arguments, and dual target compilation. Strict relocation contracts cover 14
calls. Canonical provider accounting becomes 22,903 source-owned, 16,528
generated patch, 16 alignment, and 124,393 retained official bytes, including
362 cave bytes and 7,316 exact in-place bytes across 280 source-owned functions,
five caves, 77 exact in-place leaves, and 201 patch sites. The byte-identical
package remains 4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

## Qualification boundary

No signing, flashing, reset, boot, device, FIFO, descriptor, interrupt, delay,
or MMIO operation occurred. The earliest retained executable body remains the
570-byte initializer at `0x0042308E`; the next retained executable after this
cluster begins at `0x00423524`. Live register, timer, interrupt, concurrency and
peripheral qualification is explicitly blocked by the absence of authorized
responsive right-temple hardware and a controller/golden-capture fixture.
Firmware-wide functional completeness is not claimed.
