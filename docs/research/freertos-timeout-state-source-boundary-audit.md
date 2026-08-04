# FreeRTOS `vTaskInternalSetTimeOutState` source-boundary audit

## Result

Apollo main now source-owns the complete FreeRTOS-Kernel V10.5.1
`vTaskInternalSetTimeOutState` leaf from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The released operation is
unequivocal: copy volatile `xNumOfOverflows` to `TimeOut_t.xOverflowCount`,
then copy volatile `xTickCount` to `TimeOut_t.xTimeOnEntering`, without
entering a critical section. Focused disassembly supplies only the G2 RAM
addresses and the `TimeOut_t` layout.

The admitted source boundary is:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_timeout_state.c` | 2,253 | `2d37be0e7fa2410afbe717475a80d2fb474ebf715fd030702870ffd47277c1f2` |
| `components/shared/freertos/runtime_freertos_timeout_state.h` | 2,660 | `120b28c4e56db6d62183f35ff8891eba3719fb54cdbb3cebe5b5813e6402df61` |
| `tests/fixtures/runtime_freertos_timeout_state_host.c` | 3,858 | `e8c8ad88ea48f733074696a457b2884538ef17d6ffb2d75d45211cdee1e288ae` |

The implementation retains the upstream MIT notice. The authenticated
223,695-byte `third_party/freertos-kernel/tasks.c` snapshot hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.

## Official body and recovered G2 seams

| Property | Evidence |
|---|---|
| Stock span | `[0x00455556,0x00455566)` |
| Size | 16 bytes |
| Bytes | `dff8a015096801609349096841607047` |
| SHA-256 | `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` |
| `xNumOfOverflows` | volatile signed 32-bit word at `0x20074A48` |
| `xTickCount` | volatile unsigned 32-bit word at `0x20074A34` |
| `TimeOut_t.xOverflowCount` | signed 32-bit field at offset `+0x00` |
| `TimeOut_t.xTimeOnEntering` | unsigned 32-bit field at offset `+0x04` |
| `TimeOut_t` ABI | size 8, alignment 4 |

The first PC-relative load uses literal word `0x00455AF8` to recover
`xNumOfOverflows=0x20074A48`. The second uses literal word `0x004557AC` to
recover `xTickCount=0x20074A34`. The stock body reads and stores the overflow
count before it reads and stores the tick count. The source and host oracle
preserve and observe that four-event order rather than treating the two
volatile snapshots as interchangeable.

The complete preceding `vTaskRemoveFromUnorderedEventList` routine is
`[0x0045547C,0x00455556)`, 218 bytes with SHA-256
`aa14475cf28218296c4fd829c02080fc017a5fe137f476de47e747f1e920e33b`.
The following `xTaskCheckForTimeOut` routine occupies
`[0x00455566,0x004555E6)`, 128 bytes with SHA-256
`83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c`.
The replacement therefore owns neither neighboring function. Authenticated
`tasks.c` places `vTaskSetTimeOutState` between unordered-event removal and
the internal leaf, but the stock bodies abut the internal leaf with no room
for that public wrapper. Its three queue call sites invoke the internal leaf
directly, so `vTaskSetTimeOutState` was dead-stripped from this image.

## Caller and reference closure

The stock leaf has four direct `BL` callers:

| Call site | Encoding | Containing routine |
|---|---|---|
| `0x00441886` | `13f066fe` | `xQueueGenericSend` |
| `0x00441B90` | `13f0e1fc` | `xQueueReceive` |
| `0x00441CBC` | `13f04bfc` | `xQueueSemaphoreTake` |
| `0x004555D0` | `fff7c1ff` | `xTaskCheckForTimeOut` |

The little-endian caller-address digest is
`00c5a45e0818672f879e7c38ad544eb321184a295f3adb0fee7eb708a3483feb`.
Whole-image scans find no non-linking wide jump, narrow branch, conditional
branch, `CBZ`/`CBNZ`, stored even address, stored Thumb address, or external
transfer to an interior instruction.

The four containing spans are also pinned; the fourth is the complete
`xTaskCheckForTimeOut` body:

| Span | Bytes | SHA-256 |
|---|---:|---|
| `[0x004417EE,0x00441952)` | 356 | `d8a463345ca0e7754eb0808ebf3a725a3ca66541b6e85220b6d5459166aac11d` |
| `[0x00441B0A,0x00441C44)` | 314 | `f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560` |
| `[0x00441C44,0x00441DA6)` | 354 | `4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c` |
| `[0x00455566,0x004555E6)` | 128 | `83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c` |

## Target leaf and production redirect

Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free,
four-byte-aligned 18-byte Thumb leaf:

```text
44f63421c2f207014a690260096841607047
```

Its SHA-256 is
`8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a`.
It contains no writable or read-only data section and no unresolved symbol.

The combined production tranche appends `vTaskSuspendAll` first and this
leaf second. Canonical placement is `[0x007B0854,0x007B0866)`, immediately
after suspend at `[0x007B0844,0x007B0854)` with no padding. The complete
stock entry is replaced by `5bf37db9` plus six Thumb NOPs; the resulting
16-byte redirect hashes to
`9a3d52415c08bbb7183da3a27692a50ea63395bfb064efb6cb5cef0676fd360e`.

Linux placement is `[0x007B0F8C,0x007B0F9E)`, immediately after suspend at
`[0x007B0F7C,0x007B0F8C)`. Its displacement-correct redirect is
`5bf319bd` plus six Thumb NOPs and hashes to
`a38a009107947011169a5c48332ed7a7d4a6f28f125522bddeb0ef7d6c2b465a`.

The core-source manifest classifies the stock seam as 1,566 opaque bytes at
`0x00454F38`, the 16-byte generated redirect at `0x00455556`, and 128 opaque
bytes at `0x00455566`. The canonical appended source region begins at
component file offset 3,639,412 and runtime address `0x007B0854`.

## Combined production artifacts

| Profile / artifact | Bytes | SHA-256 |
|---|---:|---|
| canonical overlay | 116,034 | `d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd` |
| canonical Apollo-main component | 3,639,430 | `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc` |
| canonical core-source package | 4,417,884 | `e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7` |
| Linux overlay | 117,882 | `5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326` |
| Linux Apollo-main component | 3,641,278 | `6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163` |
| Linux core-source package | 4,419,732 | `a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4` |

The canonical overlay records 596 functions and 563 replacement sites.
Builder accounting is 116,216 source-owned bytes including 182 in place,
81,708 generated patch bytes, 81,890 replaced-stock bytes, and 3,441,474
opaque bytes. The installed Apollo application partitions into 116,216
source, 81,708 generated, and 3,441,474 opaque bytes.

The package contains 116,836 source bytes (2.644614%), 83,501 generated
bytes (1.890068%), and 4,217,547 opaque bytes (95.465318%); 200,337 bytes
(4.534682%) are controlled. Its 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

Aggregate Linux reproduction retains the reviewed source-root spelling
`/Users/kalani/Repo/SybilSightABCD` because unrelated TLSF diagnostics embed
absolute `__FILE__`. Both new FreeRTOS leaves themselves are byte-identical
across the reviewed compilers.

## Validation and scope

The focused test authenticates the upstream snapshot and exact released
body, local source pins, official bytes and both literal seams, caller and
reference closure, the signed-overflow and unsigned-tick ABI, volatile
read/store ordering, target ELF identity, exact code bytes, and absence of
relocations or retained data.

At this historical milestone the boundary did not claim
`vTaskRemoveFromUnorderedEventList`, `xTaskCheckForTimeOut`, tick-overflow
update policy, queue blocking logic, complete scheduler serialization, or the
complete G2 `FreeRTOSConfig.h`. The adjacent `xTaskCheckForTimeOut` boundary
has since been independently promoted as described below. There is no retained
`vTaskSetTimeOutState` body to claim. All validation remains offline; no
hardware was flashed or executed.

## Current adjacent timeout-check production boundary

The complete following `xTaskCheckForTimeOut` span is now independently
source-owned through a 128-byte generated redirect/NOP replacement and a
136-byte relocation-free V10.5.1 source leaf. The promotion closes this
internal snapshot leaf's only remaining opaque caller while preserving the
same fixed timeout-state ABI and volatile tick/overflow providers.

Apple places two alignment bytes at `[0x007B143E,0x007B1440)` and the leaf at
`[0x007B1440,0x007B14C8)`; Linux places them at
`[0x007B1B92,0x007B1B94)` and `[0x007B1B94,0x007B1C1C)`. The canonical
package is 4,421,054 bytes with SHA-256
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`;
the qualified Linux package is 4,422,930 bytes with SHA-256
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
The current manifest records 877 placed, two unresolved, and five
container-only regions. This follow-on qualification is offline; no G2 was
connected, signed, flashed, reset, booted, or executed.
