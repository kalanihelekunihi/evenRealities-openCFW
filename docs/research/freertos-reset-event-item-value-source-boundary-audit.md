# FreeRTOS `uxTaskResetEventItemValue` source-boundary audit

## Result

`uxTaskResetEventItemValue` is an unequivocal, production FreeRTOS-Kernel
V10.5.1 source replacement. The bounded shared implementation is derived from commit
`def7d2df2b0506d3d249334974f51e427c17a41c` and preserves the exact released
operation:

1. read and retain the current task's event-list item value;
2. reset an independently evaluated current task's event-list item value to
   `configMAX_PRIORITIES - pxCurrentTCB->uxPriority`; and
3. return the retained value.

The source tranche consists of:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_reset_event_item_value.c` | 2,468 | `4a34efbad2b321bb0cd04fb4378a83c507c546beb858b3533eb7a0134cace7db` |
| `components/shared/freertos/runtime_freertos_reset_event_item_value.h` | 2,074 | `7cbacbed8fba97f13abb0f9bfd19fc285fd27413ace3122ddf1dab0e2ca9da67` |
| `tests/fixtures/runtime_freertos_reset_event_item_value_host.c` | 2,526 | `9451c62a9831e382f3c8555d58bcbe5b5d696f91a193439d063e131f879533df` |

The implementation retains the upstream MIT notice. It is now installed
together with `pvTaskIncrementMutexHeldCount` in the canonical and
`linux-clang` Apollo-main profiles.

## Official body and recovered G2 seams

| Property | Evidence |
|---|---|
| Stock span | `[0x00455ACA,0x00455AE0)` |
| Size | 22 bytes |
| Bytes | `dff89015086880690a680968c96ad1f1380191617047` |
| SHA-256 | `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049` |
| `pxCurrentTCB` word | `0x20074A20` |
| event-list item value | TCB offset `0x18` |
| `uxPriority` | TCB offset `0x2C` |
| `configMAX_PRIORITIES` | 56 |

The first literal load resolves through word `0x0045605C` to
`pxCurrentTCB=0x20074A20`. The body evaluates that volatile word three times
in this exact order:

1. load the TCB used to read and return the old event-list item value;
2. load the TCB whose event-list item value receives the reset value; and
3. load the TCB whose priority is subtracted from 56.

Although scheduler serialization normally leaves all three snapshots equal,
the volatile evaluations are observable C behavior and are retained rather
than coalesced into one pointer read. The host oracle supplies three
independent TCB snapshots and proves the read source, write destination, and
priority source remain separately ordered.

## Caller topology

The stock leaf has one direct `BL` caller:

| Call site | Encoding |
|---|---|
| `0x0047ECCE` | `d6f7fcfe` |

The little-endian caller-address digest is
`13157b371b412ca87ad1f51cb2694c5c7062132d784310e135fa58ff5d0e2116`.
Whole-image scans find no non-linking wide jump, narrow branch, conditional
branch, `CBZ`/`CBNZ`, stored even address, stored Thumb address, or external
transfer to an interior instruction.

## Target leaf

Under the reviewed Apple clang 21 flags, the source produces one
relocation-free, four-byte-aligned 26-byte Thumb function:

```text
44f62021c2f20701086880690a680968c96ac1f1380191617047
```

Its SHA-256 is
`04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6`.
The emitted instruction order matches the stock three-snapshot sequence. The
same bytes are the cross-profile leaf contract for Homebrew clang 22.1.8.

## Production placement and aggregate pins

The canonical overlay contributes two generated alignment bytes at
`[0x007B080E,0x007B0810)`, then places this 26-byte leaf at
`[0x007B0810,0x007B082A)`. The complete 22-byte stock entry receives a
displacement-correct non-linking `B.W` plus NOP fill.

`pvTaskIncrementMutexHeldCount` follows after two more alignment bytes. The
current production aggregate then appends `vTaskSuspendAll` and
`vTaskInternalSetTimeOutState`. Its artifacts are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| canonical overlay | 116,034 | `d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd` |
| canonical Apollo-main component | 3,639,430 | `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc` |
| canonical core-source package | 4,417,884 | `e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7` |
| Linux overlay | 117,882 | `5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326` |
| Linux Apollo-main component | 3,641,278 | `6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163` |
| Linux core-source package | 4,419,732 | `a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4` |

The canonical overlay records 596 functions and 563 replacement sites.
Builder accounting is 116,216 source-owned bytes including 182 in place,
81,708 generated patch-site bytes, 81,890 replaced-stock bytes, and
3,441,474 opaque bytes. The installed application partitions into 116,216
source, 81,708 generated, and 3,441,474 opaque bytes.

The package contains 116,836 source, 83,501 generated, and 4,217,547 opaque
bytes; 200,337 bytes are controlled. Its 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

Linux places this leaf at `[0x007B0F48,0x007B0F62)` and the mutex-held leaf
at `[0x007B0F64,0x007B0F7C)`, with two alignment bytes before each. The
subsequent suspend and timeout leaves occupy `[0x007B0F7C,0x007B0F8C)`
and `[0x007B0F8C,0x007B0F9E)` without padding. The
aggregate Linux pins require the reviewed source-root spelling
`/Users/kalani/Repo/SybilSightABCD` because unrelated TLSF diagnostics embed
absolute `__FILE__`.

## Validation and scope

The focused test authenticates the upstream snapshot and license, local
source pins, official body and literal seam, caller/reference closure, all
three independent volatile current-TCB evaluations, unsigned reset/return
semantics, target ELF section identity, exact code bytes, lack of
relocations, and absence of writable or read-only data sections.

This leaf does not claim ownership of scheduler serialization, list
operations, queue/event-list insertion, other TCB fields, or the complete G2
`FreeRTOSConfig.h`. No hardware was flashed or executed.
