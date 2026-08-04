# FreeRTOS `xTaskCheckForTimeOut` production qualification and candidate audit

Status: production source replacement for official G2 package `2.2.6.10`;
the isolated pre-promotion candidate evidence is retained below

Scope: Apollo-main application only; authenticated upstream reuse, focused
disassembly, isolated compilation, hosted behavioral validation, production
overlay and manifest integration, and Apple/Linux package qualification. No
signing, flashing, reset, boot, or hardware execution.

## Result

The official routine at `[0x00455566,0x004555E6)` is unequivocally the
FreeRTOS-Kernel V10.5.1 `xTaskCheckForTimeOut` implementation. Its complete
128-byte body instantiates the released function with these recovered G2
parameters:

| Parameter or seam | Recovered value |
|---|---|
| `BaseType_t` | signed 32-bit |
| `TickType_t` | unsigned 32-bit |
| `TimeOut_t` | 8 bytes, 4-aligned; signed overflow at `+0`, tick at `+4` |
| `INCLUDE_vTaskSuspend` | `1` |
| `portMAX_DELAY` | `UINT32_MAX` |
| `INCLUDE_xTaskAbortDelay` | `0` |
| `xTickCount` | volatile word at `0x20074A34` |
| `xNumOfOverflows` | volatile signed word at `0x20074A48` |
| assertion interrupt mask | `0x005FA0A4` |
| enter critical | `0x004420D0` |
| internal timeout snapshot | `0x00455556` |
| exit critical | `0x004420E8` |

The resulting source is an adaptation of pristine authenticated upstream
logic, not a reconstructed private algorithm. Focused disassembly is used
only to resolve the feature gates, types, RAM bindings, and port providers.
All fixed providers and RAM reads are named through overridable macros for
host validation.

The candidate was promoted after this closure was reviewed. The production
`overlay.json` now selects the source path and function, replaces the complete
stock entry, and pins profile-specific compiled bytes and aggregate outputs.
The canonical manifest classifies the 128-byte stock span as generated
replacement, then records two alignment bytes and the 136-byte source leaf.

## Authenticated source and admitted production files

The source comparator is the authenticated FreeRTOS-Kernel V10.5.1 snapshot:

| Property | Value |
|---|---|
| Tag / release | `V10.5.1` |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `tasks.c` bytes | 223,695 |
| `tasks.c` SHA-256 | `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| `tasks.c` Git blob | `d97085d8736905c1eeb9d9e871c81e5970ee70ed` |
| License | MIT |

`third_party/freertos-kernel/verify_snapshot.py` authenticates the annotated
tag, peeled commit, tree, retained Git blobs, and license before the focused
test accepts the comparator.

The bounded production source and retained candidate-history host oracle are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_task_check_for_timeout.c` | 3,506 | `d0d84996ae7ab897cf53655962e86574577b98bf367df52c9ae8ac076a8dc89e` |
| `components/shared/freertos/runtime_freertos_task_check_for_timeout.h` | 5,152 | `a4704e71126df108833878ee3ddcf51a744f4b02cae9519a4d03fe308f0abcbc` |
| `tests/fixtures/runtime_freertos_task_check_for_timeout_candidate_host.c` | 9,295 | `00612017a9632e9c5fe1427c0b6a57d090371072ff54c31fc377605fb95d303a` |

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

The complete official function is:

| Property | Value |
|---|---|
| Span | `[0x00455566,0x004555E6)` |
| Size | 128 bytes |
| SHA-256 | `83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c` |
| Entry ABI | `r0=TimeOut_t *`, `r1=TickType_t *` |
| Return ABI | `r0=BaseType_t`, `pdFALSE` or `pdTRUE` |

Exact bytes:

```text
38b505000c00002d06d1a4f198fd00205ff0ff310860fee7
002c06d1a4f18ffd00205ff0ff310860fee7ecf79efd8548
00686968411a226812f1010f01d100251ae0dff84c251268
2b689a4206d06a68904203d30125002020600de020688142
07d22068411a21602800fff7c1ff002502e0002020600125
ecf783fd280032bd
```

The selected span owns the push and pop, every return path, all conditional
and loop branches, and all five calls. It owns no external literal-pool bytes:
the two PC-relative loads point to already shared pool words at `0x004557AC`
and `0x00455AF8`.

Its immediate neighbors are independently bounded source-replacement seams:

| Range | Identity | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00455556,0x00455566)` | `vTaskInternalSetTimeOutState` | 16 | `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` |
| `[0x00455566,0x004555E6)` | selected `xTaskCheckForTimeOut` | 128 | `83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c` |
| `[0x004555E6,0x004555F0)` | `vTaskMissedYield` | 10 | `8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d` |

The two neighbors are already source-owned production leaves. This candidate
does not overlap or alter either boundary.

## One-to-one released-source proof

The complete released operation, with comments omitted, is structurally:

```c
BaseType_t xTaskCheckForTimeOut( TimeOut_t * const pxTimeOut,
                                 TickType_t * const pxTicksToWait )
{
    BaseType_t xReturn;

    configASSERT( pxTimeOut );
    configASSERT( pxTicksToWait );
    taskENTER_CRITICAL();
    {
        const TickType_t xConstTickCount = xTickCount;
        const TickType_t xElapsedTime =
            xConstTickCount - pxTimeOut->xTimeOnEntering;

        if( *pxTicksToWait == portMAX_DELAY )
        {
            xReturn = pdFALSE;
        }
        else if( ( xNumOfOverflows != pxTimeOut->xOverflowCount ) &&
                 ( xConstTickCount >= pxTimeOut->xTimeOnEntering ) )
        {
            xReturn = pdTRUE;
            *pxTicksToWait = 0;
        }
        else if( xElapsedTime < *pxTicksToWait )
        {
            *pxTicksToWait -= xElapsedTime;
            vTaskInternalSetTimeOutState( pxTimeOut );
            xReturn = pdFALSE;
        }
        else
        {
            *pxTicksToWait = 0;
            xReturn = pdTRUE;
        }
    }
    taskEXIT_CRITICAL();
    return xReturn;
}
```

This is the exact V10.5.1 path after applying the two recovered feature
gates. The binary correspondence is complete:

| Official operation | Released-source role |
|---|---|
| save `r0`/`r1`; test both for null | the two `configASSERT` calls |
| two failure sequences call `0x005FA0A4`, store zero through `-1`, loop | recovered G2 `configASSERT` expansion |
| `BL 0x004420D0` | `taskENTER_CRITICAL()` |
| load `0x20074A34`; subtract field `+4` | tick snapshot and unsigned elapsed time |
| load `*pxTicksToWait`; `CMN #1` | compare a 32-bit tick value with `UINT32_MAX` |
| return false immediately on equality | `INCLUDE_vTaskSuspend=1` indefinite-wait path |
| load `0x20074A48`; compare field `+0`; unsigned compare against field `+4` | full-wrap timeout test |
| write zero and return true | full-wrap timeout result |
| unsigned elapsed/remaining comparison and subtraction | partial-wait path |
| `BL 0x00455556`; return false | refresh the internal timeout snapshot |
| otherwise write zero and return true | ordinary timeout path |
| `BL 0x004420E8`; return `r5` | exit critical and return `BaseType_t` |

No official instruction lacks an upstream role, and no operation in the
selected released-source path is missing from the stock body.

## Focused configuration recovery

The maximum-delay path is positive evidence, not an assumption. At
`0x0045559C` the stock function loads the 32-bit wait value and executes
`CMN.W r2,#1`; equality therefore means exactly `0xFFFFFFFF`. It returns
false without reading `xNumOfOverflows`. That path is compiled only when
`INCLUDE_vTaskSuspend == 1`, proving both the feature gate and
`portMAX_DELAY=UINT32_MAX` for the 32-bit tick type.

Conversely, the V10.5.1 `INCLUDE_xTaskAbortDelay == 1` block would read
`pxCurrentTCB->ucDelayAborted`, clear it, and return true before the suspend
test. No current-TCB load, byte access, clear, or equivalent conditional
exists. The stock function moves directly from elapsed-time calculation to
the maximum-delay test, proving `INCLUDE_xTaskAbortDelay=0` for this build.

The tick load at `0x00455594` resolves through literal `0x004557AC` to
`0x20074A34`. The overflow load at `0x004555A8` resolves through literal
`0x00455AF8` to `0x20074A48`. Loads from `TimeOut_t +0` and `+4`, together
with the source-owned internal snapshot leaf, prove the signed overflow and
unsigned tick field layout. Unsigned `BLO`/`BHS` comparisons prove unsigned
tick arithmetic.

## Callers, callees, and reachability closure

The installed application contains exactly three direct calls to the public
entry:

| Call site | Encoding | Containing released routine |
|---|---|---|
| `0x004418C0` | `13f051fe` | `xQueueGenericSend` |
| `0x00441BCA` | `13f0ccfc` | `xQueueReceive` |
| `0x00441CF6` | `13f036fc` | `xQueueSemaphoreTake` |

The ordered little-endian caller-address digest is
`0c3f5a6499ff9a73584f0a759a51260c0b12462b4835fa683874bb7bcc909b20`.
The ordered address-plus-encoding digest is
`41fb83aa91102630a8a0c5d7b88ac1cd640f50870712a3edec21326571a9954e`.

The three complete containing spans remain independently pinned:

| Span | Bytes | SHA-256 |
|---|---:|---|
| `[0x004417EE,0x00441952)` | 356 | `d8a463345ca0e7754eb0808ebf3a725a3ca66541b6e85220b6d5459166aac11d` |
| `[0x00441B0A,0x00441C44)` | 314 | `f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560` |
| `[0x00441C44,0x00441DA6)` | 354 | `4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c` |

The five outgoing calls are exact:

| Call site | Target | Role |
|---|---|---|
| `0x00455570` | `0x005FA0A4` | first assertion interrupt mask |
| `0x00455582` | `0x005FA0A4` | second assertion interrupt mask |
| `0x00455590` | `0x004420D0` | enter critical |
| `0x004555D0` | `0x00455556` | internal timeout snapshot |
| `0x004555DE` | `0x004420E8` | exit critical |

Whole-image scans at every halfword find no external `B.W`, narrow branch,
conditional branch, `CBZ`, or `CBNZ` to the entry or any interior
instruction. The eleven narrow branches in the body are all internal and
remain within the selected span. A scan at every application byte offset for
every even and Thumb-form value into `[0x00455566,0x004555E6)` finds no stored
entry or interior pointer, aligned or unaligned. The three direct `BL` calls
therefore close the known executable and stored-reference graph.

## Hosted source/oracle equivalence

The host fixture compiles the candidate beside a separately named copy of the
pristine V10.5.1 operation instantiated with the recovered feature gates.
Each side receives independent globals and timeout objects. The harness
records assertions, critical entry/exit, tick and overflow reads, and the
internal snapshot provider, then compares the complete result state and event
trace.

Focused cases cover:

- indefinite `UINT32_MAX` waits, including proof that overflow state is not
  read and the internal snapshot is not called;
- a changed overflow count after the current tick has passed the saved tick;
- partial waits and snapshot refresh;
- elapsed time equal to and greater than the remaining wait;
- unsigned tick wrap without a complete extra overflow cycle; and
- signed overflow-count extremes with 32-bit unsigned tick arithmetic.

The candidate and oracle agree on the return value, both `TimeOut_t` fields,
remaining ticks, and the full provider event order for every case.

## Isolated Apple and Linux target objects

The candidate was compiled twice per reviewed profile with the same
freestanding Thumb-2 flags used for overlay leaves. Both compilers emit one
four-byte-aligned 136-byte function section and no text relocation:

| Profile | Reviewed compiler | Bytes | Alignment | Function SHA-256 |
|---|---|---:|---:|---|
| `apple-clang` | Apple clang 21.0.0 (`clang-2100.3.27.1`) | 136 | 4 | `33f0782fa8af468bccf78b558cc010a9f7a89f30c7c76abced9a799feb6a93f5` |
| `linux-clang` | Homebrew clang 22.1.8 | 136 | 4 | `486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c` |

Both objects have:

- exactly one executable section,
  `.text.open_cfw_freertos_task_check_for_timeout`;
- one global default-visibility `STT_FUNC` symbol spanning all 136 bytes;
- no undefined symbol;
- no writable allocated state or source `.data`/`.rodata` section;
- no relocation targeting the function section; and
- only the expected anonymous offset-zero type-42 section relocation in
  `.rel.ARM.exidx.text.open_cfw_freertos_task_check_for_timeout`.

The profile byte difference is reviewed compiler scheduling, not a semantic
or ABI difference. Apple clang uses separate `LDR` operations for the two
`TimeOut_t` fields; Homebrew clang uses one `LDRD`. Both materialize the same
fixed providers and RAM base, implement the same branch graph, and have the
same size and alignment. The focused module pins the complete function bytes
for both profiles and validates the active profile fail-closed.

## Retained pre-promotion validation history

`tests/test_freertos_task_check_for_timeout_candidate.py` passes six focused
tests under Apple clang 21 and the same six under the reviewed Homebrew clang
22.1.8 Docker profile. It authenticates upstream and official inputs, pins
the local source, proves call/reference closure, compares hosted behavior,
checks both profile byte records, and now asserts production inclusion and
aggregate pins. References to “candidate” in the fixture and test filename
preserve the audit trail from the isolated stage; they do not denote current
deployment status.

## Production placement, manifest, and package qualification

The production leaf has no relocation or retained data. Apple adds alignment
`[0x007B143E,0x007B1440)` and places the source at
`[0x007B1440,0x007B14C8)`; Linux adds alignment
`[0x007B1B92,0x007B1B94)` and places it at
`[0x007B1B94,0x007B1C1C)`. The stock span is a generated entry redirect and
NOP fill in both profiles.

| Artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Overlay | 119,204 / `4b3071e64d0e183efbb59788c94dca8ae01fba6d952aecbb9682893844171a79` | 121,080 / `75054c31d8ca3e50659443c470f11a604fb715db430e08b3ad4c468042282324` |
| Apollo-main component | 3,642,600 / `eaa59756edb47e85be46959cb2242200f51bc4a3acaea1fc4365ee1f6a59e152` | 3,644,476 / `29c48306a2f8fab7b87af6c90b38786e4ee36d19f9eb68122614df4b355472ce` |
| Apollo-main component report | 1,012,249 / `eafa53f354ac87a7e432e1aa675fe93dbb77548178b9d4f8c16881d2705aabbd` | 1,029,223 / `f978bdbda751dc21252d213c717b6df344ae5fce482c1bddacc8b7fc130db9ad` |
| Core-source package | 4,421,054 / `4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37` | 4,422,930 / `22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab` |
| Flash plan | 632,134 / `98b8c544328ac3cecaa00c1bc15f4fb7958b9c26e2b0433852864eeec66cd86a` | 563,135 / `7128a3311f0a0ded53394dbf49a1a1f71d5d559b891aba080cd41de2c5cf9066` |
| Package report | 2,322 / `61013f4dd6a8811fdbc275a744125e0b30694398b9e80da72d678a33c9dc6179` | 2,322 / `b00099ecb6b6dc5e9c49dd046cf59c2bfb30220f653b4214308cfd72b22eef06` |
| `SHA256SUMS` | 118,243 / `5adb3bfd414cc0e65d2db8ef5193ae31e35e7f4b452d04a4768fccf98c771085` | 105,648 / `463541d197174f263bd0bd86e0be733ac7797d755b3752b207381161cf5da78b` |

The canonical manifest has 821 Apollo-main and 884 whole-package regions,
with 877 placed, two unresolved, and five container-only. Apple records 609
effective functions and 573 patches; raw configuration and Linux record 613
functions and 577 patches. Canonical component accounting is 119,386 source,
83,074 generated patch, 83,256 replaced-stock, 3,440,108 opaque, and 32
wrapper bytes. Canonical package accounting is 119,996 source, 84,877
generated, and 4,216,181 opaque bytes. Linux component accounting is 121,262
source, 83,240 generated patch, 83,422 replaced-stock, 3,439,942 opaque, and
32 wrapper bytes; its package owns 121,917 source, 84,832 generated, and
4,216,181 opaque bytes.

No device was connected, signed, flashed, reset, booted, or executed. All
evidence is offline.
