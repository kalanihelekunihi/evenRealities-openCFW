# FreeRTOS `prvGetDisinheritPriorityAfterTimeout` candidate audit

Status: reviewed production-linked source leaf for official G2 package
`2.2.6.10`

Scope: Apollo-main authenticated upstream reuse, focused disassembly, hosted
behavioral validation, and atomic production linkage with its only caller. No
signing, flashing, or hardware change.

## Result

The complete official helper at `[0x00441EC4,0x00441ED8)` is unequivocally
FreeRTOS-Kernel V10.5.1
`prvGetDisinheritPriorityAfterTimeout`. Its 20-byte body is the released
operation instantiated with the recovered G2 queue/list ABI:

| Parameter | Recovered value |
|---|---|
| `UBaseType_t` | unsigned 32-bit |
| `configUSE_MUTEXES` | `1` |
| `configMAX_PRIORITIES` | `56` |
| `tskIDLE_PRIORITY` | `0` |
| `Queue_t::xTasksWaitingToReceive` | `Queue_t + 0x24` |
| `List_t::uxNumberOfItems` | list `+0`, therefore queue `+0x24` |
| `List_t::xListEnd.pxNext` / head pointer | list `+0x0C`, therefore queue `+0x30` |
| `List_t` | 20 bytes, four-byte aligned |
| `ListItem_t` | 20 bytes, four-byte aligned; item value at `+0` |
| `MiniListItem_t` | 12 bytes, four-byte aligned |

The implementation in
`components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c`
is a bounded adaptation of the exact authenticated upstream helper. Focused
disassembly supplies only the target configuration and structure offsets; it
does not reconstruct a private algorithm. It is now linked as the sole source
dependency of the production `xQueueSemaphoreTake` replacement. The exact
stock helper bytes remain in place but are unreachable and therefore do not
need a second redirect.

## Authenticated source and admitted files

The source comparator is the retained FreeRTOS-Kernel V10.5.1 snapshot:

| Property | Value |
|---|---|
| Tag / release | `V10.5.1` |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `queue.c` bytes | 125,614 |
| `queue.c` SHA-256 | `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` |
| License | MIT |

`third_party/freertos-kernel/verify_snapshot.py` authenticates the annotated
tag, peeled commit, tree, retained Git objects, and license before the focused
test accepts the comparator.

The bounded candidate and host oracle are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c` | 2,620 | `37a4ea5a258befb3b607bf5b0c3e6f28b60ed11279b98e13910e0a125519db3a` |
| `components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.h` | 4,456 | `cd97393461faefa962b91b286977226e1e7c3f1e3dc5a5167c415d5e33c5bd1f` |
| `tests/fixtures/runtime_freertos_queue_get_disinherit_priority_after_timeout_candidate_host.c` | 3,214 | `720ca6753e4b92e05313fa0d2911c218bc55e0b4cd06757237d83a9c447b9ce6` |

The implementation retains the upstream FreeRTOS copyright and MIT notice.

## Official identity and complete boundary

The authoritative package is:

| Property | Value |
|---|---|
| File | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | 3,523,396 |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application bytes | 3,523,364 |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Runtime base | `0x00438000` |

The complete helper is:

| Property | Value |
|---|---|
| Span | `[0x00441EC4,0x00441ED8)` |
| Size | 20 bytes |
| SHA-256 | `21721e8f80852df9a1d4f0f23db76d3144a4c8c04a81606dccee5b3ff132819c` |
| Entry ABI | `r0=const Queue_t *` |
| Return ABI | `r0=UBaseType_t` |

Exact bytes:

```text
416a 0029 04d0 006b 0068 d0f13800 00e0 0020 7047
```

The selected span owns its entry, both internal branches, the empty-list path,
and the sole return. It imports no literal-pool word, call target, RAM global,
or relocation. Its immediate independently bounded neighbors are:

| Range | Identity | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00441EA2,0x00441EC4)` | source-replaced `vQueueDelete` stock entry | 34 | `ab55f9fa6eb823935056d4b4030cc10df52bc8b33318abea201e61348a026bc4` |
| `[0x00441EC4,0x00441ED8)` | selected helper | 20 | `21721e8f80852df9a1d4f0f23db76d3144a4c8c04a81606dccee5b3ff132819c` |
| `[0x00441ED8,0x00441F5E)` | `prvCopyDataToQueue` | 134 | `35c79bf50852c5f61d579981278509aa156ab8e18f57b4b6d6b7a88563682e36` |

## One-to-one released-source proof

The released operation has only two paths:

1. If the receive-wait list is nonempty, return
   `configMAX_PRIORITIES - head->xItemValue` using unsigned arithmetic.
2. Otherwise return `tskIDLE_PRIORITY`.

Every stock instruction has one released-source role:

| Official operation | Released-source role |
|---|---|
| `LDR r1,[r0,#0x24]` | `listCURRENT_LIST_LENGTH(&queue->xTasksWaitingToReceive)` |
| `CMP r1,#0; BEQ 0x00441ED4` | select nonempty versus empty path |
| `LDR r0,[r0,#0x30]` | load `xListEnd.pxNext`, the head entry |
| `LDR r0,[r0,#0]` | `listGET_ITEM_VALUE_OF_HEAD_ENTRY` |
| `RSB.W r0,r0,#56` | `configMAX_PRIORITIES - xItemValue`, proving 56 |
| `B 0x00441ED6` | join the two result paths |
| `MOVS r0,#0` | `tskIDLE_PRIORITY`, proving zero |
| `BX lr` | return the `UBaseType_t` result |

The direct queue offsets also resolve the target list layout. A 20-byte
`List_t` begins at queue `+0x24`; its four-byte count and index precede the
12-byte mini end item. The mini item's `pxNext` is therefore at list `+0x0C`,
or queue `+0x30`, and points to a 20-byte `ListItem_t` whose first word is the
item value. Compile-time assertions in the candidate header pin all of these
widths and offsets.

The stock body contains no call, PC-relative load, fixed address, or external
branch. Its only two branches are internal:

| Branch | Target | Role |
|---|---|---|
| `0x00441EC8` | `0x00441ED4` | empty list |
| `0x00441ED2` | `0x00441ED6` | join before return |

This closes the helper's executable and data dependencies at its argument and
return ABI.

## Caller and reachability closure

The official application contains exactly one direct call:

| Call site | Encoding | Containing routine |
|---|---|---|
| `0x00441D90` | `00f098f8` | `xQueueSemaphoreTake` |

The complete caller span `[0x00441C44,0x00441DA6)` is 354 bytes with SHA-256
`4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c`.
The ordered little-endian caller-address digest is
`25ca43d09e0faba36b1006f32225b564051e8eef631986dbdd473da20700ec1d`;
the address-plus-encoding digest is
`95c27cb70bd833d0db95c2934751679b9b3357f598b8782c324277d24f3dcc0b`.

Whole-image scans at every halfword find:

- that one `BL` to the public entry;
- no `B.W`, narrow branch, conditional branch, `CBZ`, or `CBNZ` from outside
  the helper to its entry or any interior instruction; and
- no external direct branch to an interior instruction.

A byte-granularity scan for every even and Thumb-form value into the complete
20-byte range finds no stored entry or interior pointer, aligned or unaligned,
in the official installed application. The official direct call therefore
closes its known entry and interior-reference topology.

The production source replacement resolves its sole `R_ARM_THM_CALL` directly
to the appended project-prefixed helper. Whole-image scans of the assembled
Apple artifact find no external wide or narrow branch and no stored even or
Thumb-form pointer into `[0x00441EC4,0x00441ED8)`. This closes the original
one-caller topology without patching an entry that no executable path reaches.

## Hosted upstream-oracle equivalence

The host fixture compiles the candidate beside a separately named copy of the
pristine V10.5.1 operation. The candidate side uses the recovered queue offsets
through host-only access overrides; the oracle side uses logical upstream
`Queue_t`, `List_t`, and list macros. Both are invoked independently.

Focused cases cover:

- empty lists with head values `0` and `UINT32_MAX`; the fixture installs a
  null head for this path, proving the candidate does not dereference it;
- one and multiple waiting items;
- valid encoded item values mapping to priorities 56, 55, 1, and 0;
- values 57 and `UINT32_MAX`, proving exact unsigned subtraction rather than a
  clamp or signed reinterpretation; and
- count values `2` and `UINT32_MAX`, proving that only zero/nonzero matters.

The candidate and upstream oracle return exactly the same 32-bit result in all
cases.

## Isolated Apple and Linux target objects

The candidate was compiled twice on each reviewed profile with the normal
freestanding Thumb-2 leaf flags. Both compilers produce the same function:

| Profile | Reviewed compiler | Bytes | Alignment | Function SHA-256 |
|---|---|---:|---:|---|
| `apple-clang` | Apple clang 21.0.0 (`clang-2100.3.27.1`) | 18 | 4 | `fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519` |
| `linux-clang` | Homebrew clang 22.1.8 | 18 | 4 | `fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519` |

Exact emitted function bytes for both profiles:

```text
416a00290fbf0020006b0068c0f138007047
```

The compilers use an `IT`-selected zero result instead of the stock branch,
which reduces the isolated source function from 20 to 18 bytes without
changing the released operation.

Both objects have:

- exactly one executable section,
  `.text.open_cfw_freertos_queue_get_disinherit_priority_after_timeout`;
- one global default-visibility `STT_FUNC` symbol spanning all 18 bytes;
- no undefined symbol;
- no writable allocated state;
- no source text relocation; and
- only the anonymous offset-zero type-42 unwind-index metadata relocation,
  which does not target the function section.

Two successive builds per profile produce identical function bytes.

## Production integration proof

The helper is ordered immediately before the semaphore-take source leaf, has
no relocation, and is the target of that leaf's sole `R_ARM_THM_CALL`.
Apple places it at overlay offset 120,708 / runtime `0x007B1AA8`; exact-root
Linux places it at offset 122,564. Both emit the same 18 bytes and SHA-256
`fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519`.
The core-source manifest exposes it as an appended `source_compiled` leaf.
The original stock 20-byte helper remains classified as official opaque data,
with exact bytes pinned, because the assembled topology proves it unreachable.

## Validation

Apple-clang:

```sh
python3 -m unittest -v \
  openCFW/tests/test_freertos_queue_get_disinherit_priority_after_timeout_candidate.py
```

Result: 6 tests passed.

Reviewed Linux/Homebrew clang container:

```sh
docker exec -w /Users/kalani/Repo/SybilSightABCD/openCFW \
  -e OPENCFW_CLANG=/home/linuxbrew/.linuxbrew/bin/clang \
  -e OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
  opencfw-linux-llvm \
  python3 -m unittest -v \
    tests/test_freertos_queue_get_disinherit_priority_after_timeout_candidate.py
```

Result: the same 6 tests passed, including exact target bytes and atomic
production registration.

## Promotion result

The helper and its only stock caller were promoted atomically. No stock helper
redirect or opaque-region split was emitted because exhaustive assembled-image
branch and pointer scans prove that the stock body has no remaining caller.
Apple and exact-root Linux overlay, component, and package pins are recorded in
the semaphore-take audit. This remains a software build result only: no
signing, flashing, or hardware operation was performed.
