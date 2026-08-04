# FreeRTOS `vTaskSuspendAll` source-boundary audit

Status: production-integrated source replacement; current Apple target
`0x007B05F4`, exact-root Linux target `0x007B0D1C`

## Result

Apollo main source-owns the complete FreeRTOS-Kernel V10.5.1
`vTaskSuspendAll` leaf from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. This is exact upstream source
reuse under the MIT license, with focused G2 disassembly limited to the
kernel-global binding, callable boundary, caller topology, and retained
`xTaskResumeAll` coupling.

The bounded source tranche is:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_suspend_all.c` | 2,258 | `792ffc64fab54de686dd36cbb0ea1bf8040a92ac8a105cfeda2d7b45e6986bcf` |
| `components/shared/freertos/runtime_freertos_suspend_all.h` | 1,619 | `bf42ac5b89d64a76889c4fe9f75def51934af2f9fcc51776df495571e4d6ed77` |
| `tests/fixtures/runtime_freertos_suspend_all_host.c` | 4,705 | `292ef9bfd663a9085d3c41a872c1956b5b165ea8e2639872c787751992d01ed3` |

The released operation is one volatile 32-bit read, wrapping unsigned
increment, and volatile store to `uxSchedulerSuspended`, bracketed by the
upstream software- and memory-barrier positions. The recovered G2 barriers
are compiler-ordering barriers and emit no target instruction.

## Official function and scheduler-depth seam

| Property | Evidence |
|---|---|
| Stock span | `[0x00454D7C,0x00454D88)` |
| Size | 12 bytes |
| Bytes | `dff8e8060168491c01607047` |
| SHA-256 | `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2` |
| Literal | `0x00455468` |
| Recovered word | `uxSchedulerSuspended=0x20074A58` |
| Recovered width | 32-bit `UBaseType_t` |

The body performs no assertion, hook, call, condition, or additional state
access. Unsigned wrap is intentional and matches upstream `UBaseType_t` C
semantics. Host tests cover zero, nested nonzero depths, both signed-boundary
values, and wrap from `UINT32_MAX` to zero while proving exactly one read and
one write in barrier/read/write/barrier order.

The official `xTaskResumeAll` body used for compatibility analysis occupies
`[0x00454DCC,0x00454EFE)`, is 306 bytes, and hashes to
`548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09`.
Its decrement seam at `[0x00454DEA,0x00454DF4)` is
`edf771f93068401e3060`: it reads the same `0x20074A58` word, subtracts one,
and stores it. That evidence established compatibility before the scheduler
cluster promotion; the current source-owned `xTaskResumeAll` uses the same RAM
word and nested-depth semantics.

## Caller and entry closure

The complete official image has 13 direct `BL` callers:

| Call sites |
|---|
| `0x00441890`, `0x00441B9A`, `0x00441CC6`, `0x00454B6E` |
| `0x00454F46`, `0x00455622`, `0x00455778`, `0x00456118` |
| `0x0045625E`, `0x0047E892`, `0x0047EC6A`, `0x0047EDB0` |
| `0x0057E1F2` |

The little-endian caller-address digest is
`950b6ce1df6baf8575d53aba4036bdaba836597e31970710984083494511b7de`;
the address-plus-encoding record digest is
`020f8997cabb5201c1bf55b4d8f56ab96bab1cb44cc526f01ffad71d82370254`.
The paired resume function has 21 independently pinned direct callers.
Whole-image scans find no non-linking wide jump, narrow branch, conditional
branch, `CBZ`/`CBNZ`, stored even address, stored Thumb address, or external
transfer into an interior instruction of either reviewed boundary.

Replacing the `vTaskSuspendAll` public entry consequently covers the complete
known caller topology. The production patch does not rewrite call sites and
does not alter the retained return path.

## Target leaf and historical first-production redirects

Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free,
four-byte-aligned 16-byte Thumb leaf:

```text
44f65820c2f207000168013101607047
```

Its SHA-256 is
`0928ce291a4a96b18baf7304bc7f87fb828ac06902619f1f42500e04c73883be`.
The object contains no undefined function, relocation, writable data, or
nonempty read-only data dependency.

The following placements record the original suspend-only production tranche;
later source additions moved the append-only leaf to the current targets in the
status line while retaining the same object bytes and stock replacement.

| Historical profile | Overlay offset | Historical runtime span | Padding | Complete replacement | Replacement SHA-256 |
|---|---:|---|---:|---|---|
| canonical Apple clang | 116,000 | `[0x007B0844,0x007B0854)` | 0 | `5bf362bd00bf00bf00bf00bf` | `9e77eb5f5241f6afed2c388f225dcb8d9e2bb4b39c22905d7ac6f3226f467814` |
| Linux clang | 117,848 | `[0x007B0F7C,0x007B0F8C)` | 0 | `5cf3feb800bf00bf00bf00bf` | `b196eabd0feb93217aecb62e3a8f286f016695a4b6b70830182547fd175f16e5` |

Each replacement is one non-linking `B.W` followed by four Thumb NOPs and
owns all 12 authenticated stock bytes. In the combined production order, the
18-byte `vTaskInternalSetTimeOutState` source leaf immediately follows this
leaf, so neither profile needs intervening alignment.

## Historical manifest ownership and aggregate pins

At the original suspend-only promotion, the official component partition was
split without a gap or overlap:

| Region | File offset | Runtime address | Bytes | Ownership |
|---|---:|---:|---:|---|
| opaque before suspend | 116,632 | `0x00454778` | 1,540 | official blob |
| suspend entry replacement | 118,172 | `0x00454D7C` | 12 | generated redirect/NOP fill |
| opaque after suspend | 118,184 | `0x00454D88` | 374 | official blob |
| appended suspend leaf | 3,639,396 | `0x007B0844` | 16 | source compiled |

The post-function opaque range ends exactly at file offset 118,558 and
runtime address `0x00454EFE`, where the existing tick-getter replacement
begins. The appended leaf ends exactly where the timeout-state source leaf
begins.

The combined suspend/timeout production artifacts at that historical point
were:

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
81,708 generated patch-site bytes, 81,890 replaced-stock bytes, and
3,441,474 opaque base bytes. Package ownership is 116,836 source bytes,
83,501 generated bytes, and 4,217,547 opaque bytes; 200,337 bytes are
controlled.

The 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two deliberately unresolved, and five container-only
regions. The Linux aggregate retains the reviewed source-root spelling
`/Users/kalani/Repo/SybilSightABCD` because unrelated TLSF diagnostics embed
an absolute `__FILE__` path; the suspend leaf itself is byte-identical across
the two reviewed compilers.

## Scope and hardware caveat

This function boundary owns the scheduler-depth increment only; the subsequent
scheduler-cluster tranche separately promoted `xTaskResumeAll` and its direct
dependencies. Neither boundary claims scheduler initialization, task creation,
the complete TCB, tickless behavior, or a full FreeRTOS kernel RAM migration.
All validation is offline source, object, host-oracle, official-image,
topology, manifest, and reproducible-build evidence. No G2 was flashed, reset,
or executed.
