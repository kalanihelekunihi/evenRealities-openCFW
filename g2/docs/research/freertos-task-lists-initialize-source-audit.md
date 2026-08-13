# FreeRTOS `prvInitialiseTaskLists` production-source audit

Status: **source-integrated; independent GO for the Apollo-main production
replacement**  
Scope: official G2 `2.2.6.10` Apollo-main application only; offline source,
overlay, manifest, package, and reproducible-build qualification with no
signing, flashing, or hardware access

## Decision

The official Apollo-main helper is an exact, complete, source-replaceable
FreeRTOS-Kernel V10.5.1 `prvInitialiseTaskLists` boundary:

| Property | Recovered value |
|---|---|
| Stock span | `[0x0045568C,0x004556E0)` |
| Size | 84 bytes |
| SHA-256 | `db9aad99c9dfd14cb9f2eb453dd86af05b11ed049eacf8771f25a82382894723` |
| Direct callers | one `BL`, at `0x00454A20` |
| External entry/interior branches | none beyond that one entry `BL` |
| Stored entry/interior pointers | none |
| Callable dependency | `vListInitialise` only, at six static call sites |
| Ready lists initialized | 56 |
| Other lists initialized | delayed 1, delayed 2, pending-ready, termination, suspended |
| Final pointer stores | `pxDelayedTaskList=&xDelayedTaskList1`; `pxOverflowDelayedTaskList=&xDelayedTaskList2` |

The recovered body, globals, configuration, caller, and dependency closure are
sufficient for Apollo-main production integration. Production now registers
`open_cfw_freertos_task_lists_initialize` and redirects the complete stock
entry through `replace_freertos_task_lists_initialize`.

The initial candidate was a **NO-GO** because it declared the existing
`open_cfw_freertos_list_initialise` provider with a different structure tag.
The provider defines:

```c
void open_cfw_freertos_list_initialise(
    struct open_cfw_freertos_list_initialise_list *list
);
```

The rejected candidate redeclared the same external identifier with:

```c
void open_cfw_freertos_list_initialise(
    struct open_cfw_freertos_task_lists_list *list
);
```

Those distinct tags made the function types incompatible in C even though both
pointers have the same 32-bit Arm representation. A combined translation-unit
check exposed the conflict and six incompatible-pointer diagnostics that
ordinary non-LTO separate compilation would have hidden.

The production source closes that blocker exactly: its header forward-declares
`struct open_cfw_freertos_list_initialise_list`, declares the provider with
that tag, and each of the six call expressions explicitly converts the
recovered list address through `void *` to that exact provider pointer type.
Independent host and Cortex-M55 combined provider-plus-consumer checks pass
with `-Wall -Wextra -Werror -pedantic -fsyntax-only`. The language contract is
therefore diagnostic-clean and the prior blocker is closed; this audit records
an independent **GO**.

## Authoritative inputs

The reviewed application input is:

| Property | Value |
|---|---|
| Package | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package size | 3,523,396 bytes |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application | 3,523,364 bytes at `0x00438000` |
| Installed SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Helper payload offset | `0x0001D68C` / 120,460 |
| Helper package offset | `0x0001D6AC` / 120,492 |

The comparator is the authenticated official FreeRTOS-Kernel V10.5.1
snapshot:

| Property | Value |
|---|---|
| Annotated tag | `V10.5.1`, unsigned |
| Tag object | `d7b40dbed508c305c2a32ccf3982045ec9ba8734` |
| Peeled commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `tasks.c` size | 223,695 bytes |
| `tasks.c` SHA-256 | `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| `tasks.c` Git blob | `d97085d8736905c1eeb9d9e871c81e5970ee70ed` |
| License | MIT, retained as `third_party/freertos-kernel/LICENSE.md` |
| License SHA-256 | `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1` |

`third_party/freertos-kernel/verify_snapshot.py` passes and authenticates the
tag object, peeled commit, tree, selected blobs, SHA-256 pins, and MIT license.
The unsigned-tag qualification is preserved; no stronger signature claim is
made.

## Complete stock body and boundary

The complete stock bytes are:

```text
38b5002408e0dff82807142101fb04f1084400f0edfc641c382cf4d3
dff89849200000f0e5fcdff89459280000f0e0fc3a4800f0ddfcdff8
880900f0d9fcdff8700900f0d5fcdff87c090460dff87809056031bd
```

Capstone decodes all 84 bytes without residue:

```text
0045568C  38b5       push     {r3, r4, r5, lr}
0045568E  0024       movs     r4, #0
00455690  08e0       b        0x004556A4
00455692  dff82807   ldr.w    r0, [pc, #0x728]
00455696  1421       movs     r1, #0x14
00455698  01fb04f1   mul      r1, r1, r4
0045569C  0844       add      r0, r1
0045569E  00f0edfc   bl       0x0045607C
004556A2  641c       adds     r4, r4, #1
004556A4  382c       cmp      r4, #0x38
004556A6  f4d3       blo      0x00455692
004556A8  dff89849   ldr.w    r4, [pc, #0x998]
004556AC  2000       movs     r0, r4
004556AE  00f0e5fc   bl       0x0045607C
004556B2  dff89459   ldr.w    r5, [pc, #0x994]
004556B6  2800       movs     r0, r5
004556B8  00f0e0fc   bl       0x0045607C
004556BC  3a48       ldr      r0, [pc, #0xE8]
004556BE  00f0ddfc   bl       0x0045607C
004556C2  dff88809   ldr.w    r0, [pc, #0x988]
004556C6  00f0d9fc   bl       0x0045607C
004556CA  dff87009   ldr.w    r0, [pc, #0x970]
004556CE  00f0d5fc   bl       0x0045607C
004556D2  dff87c09   ldr.w    r0, [pc, #0x97C]
004556D6  0460       str      r4, [r0]
004556D8  dff87809   ldr.w    r0, [pc, #0x978]
004556DC  0560       str      r5, [r0]
004556DE  31bd       pop      {r0, r4, r5, pc}
```

The immediately preceding function returns with `bx lr` at `0x0045568A`.
The next function begins with its own `push` at `0x004556E0`. There is no
intervening literal, padding, shared epilogue, or alternate entry. The exact
84-byte body occurs once in the installed application.

## Exact released-source authentication

The released definition begins at byte offset 150,869 of authenticated
`tasks.c`. Taking bytes from its initial `static` through its closing `}` and
excluding the following CRLF gives this exact range:

| Source range | Bytes | SHA-256 |
|---|---:|---|
| `tasks.c[150869:151768]` | 899 | `0908b0fb7a1b43d6d4fa2bd8212ba069ac6a8d4d036b4f973ae7f3baa6dd6e63` |

The following CRLF occupies bytes 151,768 and 151,769; the standard FreeRTOS
separator begins at byte 151,770. This makes the source boundary independent
of line-number rendering.

The released operation is exactly:

1. For priorities zero through `configMAX_PRIORITIES-1`, initialize the
   corresponding ready list.
2. Initialize delayed list 1, delayed list 2, and the pending-ready list.
3. When `INCLUDE_vTaskDelete==1`, initialize the termination-waiting list.
4. When `INCLUDE_vTaskSuspend==1`, initialize the suspended-task list.
5. Point `pxDelayedTaskList` to delayed list 1.
6. Point `pxOverflowDelayedTaskList` to delayed list 2.

The stock loop bound `0x38`, list stride `0x14`, five non-ready calls, and two
final pointer stores match that source without an added or missing operation.

## Fixed RAM mapping and selected configuration

Every PC-relative stock literal was resolved independently:

| Upstream object | Literal address | Recovered RAM address | Stock use |
|---|---:|---:|---|
| `pxReadyTasksLists[56]` | `0x00455DBC` | `0x2006A49C` | loop base, stride `0x14` |
| `xDelayedTaskList1` | `0x00456044` | `0x20073CFC` | initialize; retained in `r4` |
| `xDelayedTaskList2` | `0x00456048` | `0x20073D10` | initialize; retained in `r5` |
| `xPendingReadyList` | `0x004557A8` | `0x20073D24` | initialize |
| `xTasksWaitingTermination` | `0x0045604C` | `0x20073D38` | initialize at `0x004556C6` |
| `xSuspendedTaskList` | `0x0045603C` | `0x20073D4C` | initialize at `0x004556CE` |
| `pxDelayedTaskList` pointer word | `0x00456050` | `0x20074A24` | store `0x20073CFC` |
| `pxOverflowDelayedTaskList` pointer word | `0x00456054` | `0x20074A28` | store `0x20073D10` |

The consecutive special-list addresses differ by exactly `0x14`, matching the
recovered 20-byte `List_t`. In particular, the termination and suspended
call-site identities above correct the reversed labels in the older
`freertos-list-initialise-source-boundary-audit.md`: released source order and
the resolved literals prove that `0x004556C6` is termination and
`0x004556CE` is suspended.

The body closes these build selections:

| Selection | Evidence |
|---|---|
| `configMAX_PRIORITIES=56` | loop comparison against `0x38` |
| `INCLUDE_vTaskDelete=1` | termination-list call is present |
| `INCLUDE_vTaskSuspend=1` | suspended-list call is present |
| `sizeof(List_t)=0x14` | ready-list stride and consecutive globals |
| 32-bit pointers and `UBaseType_t` | target ABI and fixed word writes |
| `configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0` | existing authenticated 20-byte source-owned list ABI |
| 32-bit `TickType_t` and mini end marker | existing source-owned `vListInitialise` ABI |

The helper accepts no argument and returns `void` under the ordinary 32-bit Arm
procedure-call ABI. Its only persistent effects are the 61 list
initializations and two volatile pointer-word stores. It does not touch a TCB,
allocator, scheduler critical section, interrupt mask, assertion, hook,
device register, or hardware peripheral.

## Complete caller and reference topology

The installed application was scanned on every halfword for `BL`, `B.W`,
wide conditional `B<cond>.W`, narrow unconditional/conditional branches, and
`CBZ`/`CBNZ`. It was separately scanned at every byte for stored 32-bit even
or odd/Thumb values canonicalizing to the entry or any interior halfword.

| Reference class | Entry | External interior |
|---|---:|---:|
| `BL` | one | zero |
| unconditional `B.W` | zero | zero |
| conditional `B<cond>.W` | zero | zero |
| narrow `B` / `B<cond>` / `CBZ` / `CBNZ` | zero | zero |
| stored even or odd/Thumb address | zero | zero |

The sole incoming reference is:

| Call site | Encoding | Target | Containing function |
|---:|---|---:|---|
| `0x00454A20` | `00f034fe` | `0x0045568C` | `prvAddNewTaskToReadyList` |

The complete caller is `[0x004549FC,0x00454AAE)`, 178 bytes, SHA-256
`4e765b4faa584167eb8aa1e91ab46fb3383dbfb24ebe4adbd5a4909943706ff4`.
The call is reached only after the caller increments
`uxCurrentNumberOfTasks`, finds `pxCurrentTCB` null, installs the new TCB, and
confirms that the task count is one. That is the pristine first-task
initialization path in `prvAddNewTaskToReadyList`.

The scan proves the direct and stored-address topology present in the image.
As with any static scan, it does not claim to exclude a branch target computed
from arbitrary runtime arithmetic. There is no stored pointer or alternate
direct ingress suggesting such an owner.

## Callable dependency closure

The stock body has exactly six outgoing calls, all to the complete
`vListInitialise` entry:

| Call site | Encoding | Runtime invocations | Argument |
|---:|---|---:|---|
| `0x0045569E` | `00f0edfc` | 56 | each ready list |
| `0x004556AE` | `00f0e5fc` | 1 | delayed list 1 |
| `0x004556B8` | `00f0e0fc` | 1 | delayed list 2 |
| `0x004556BE` | `00f0ddfc` | 1 | pending-ready list |
| `0x004556C6` | `00f0d9fc` | 1 | termination list |
| `0x004556CE` | `00f0d5fc` | 1 | suspended list |

The common target is stock entry `0x0045607C`. Apollo-main already replaces
the complete `[0x0045607C,0x0045609A)` body with a generated redirect to the
MIT-licensed source provider
`open_cfw_freertos_list_initialise`. Its current source is
`components/apollo_main/core_overlay/runtime_freertos_list_initialise.c`,
4,860 bytes with source hash
`a77b7c99f2cd092b80caae0c247cae708ba52a4cd89f723274ddc93fc2442733`.

Production binds all six calls directly to
`open_cfw_freertos_list_initialise`; it does not retain calls through absolute
stock address `0x0045607C`. The permitted undefined-symbol/relocation set is
therefore exactly one symbol name, repeated at six reviewed call relocations:

```text
open_cfw_freertos_list_initialise
```

No stock function, assertion, port helper, libc function, allocator, or device
callback is part of the callable closure. The eight fixed RAM bindings above
remain explicit G2 compatibility seams rather than upstream provenance.

## Apollo-main-only boundary

The exact 84 Apollo-main bytes do not occur in the official bootloader, but
that absence must not be misread as absence of the upstream behavior. The
bootloader contains its own separately compiled semantic homolog:

| Property | Bootloader value |
|---|---|
| Image | raw `ota_s200_bootloader.bin` at `0x00410000` |
| Image size / SHA-256 | 148,599 / `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |
| Helper span | `[0x00418A44,0x00418A98)` |
| Size / SHA-256 | 84 / `6712e4325fcca28edae347791f093619ffaf9f9f6257b7379a1cec7c3a172cf2` |
| Direct caller | `BL` at `0x00417E7C`, encoding `00f0e2fd` |
| `vListInitialise` target | stock bootloader entry `0x0041B53C` |

It also uses 56 ready lists and the same five optional lists, but its RAM map
is distinct: ready-list base `0x20024870`, special lists
`0x20026F34...0x20026F84`, and selector words `0x20027138` and
`0x2002713C`. The bootloader's `vListInitialise` is not the Apollo-main
source-owned provider.

Therefore this decision is **GO only for the Apollo-main component**. Do not
register the candidate in the bootloader overlay, do not add a bootloader patch
site, and do not reuse Apollo-main RAM addresses in boot. A boot promotion
would need its own provider closure, focused test, artifact pins, and manifest
review.

## Production integration and reproducible pins

The reviewed production source is
`components/shared/freertos/runtime_freertos_task_lists_initialize.c`, 3,529
bytes with SHA-256
`58773452256b0f44647040085bbcc7a896a1cbd3efd0c5c4b4de3ddfe1a9e857`.
Its 5,886-byte header hashes to
`6fe827f6d2659a784e8b3e22fa096162dfd4003146c0425222efc92c63baef9e`.
Both retain the FreeRTOS MIT notice and bind the exact authenticated
`tasks.c[150869:151768]` operation to the recovered Apollo-main RAM map.

Apple Clang 21.0.0 and exact-root Homebrew Clang 22.1.8 emit the same 88-byte
unrelocated text:

```text
b0b54af29c450024c2f206056019fff7feff1434b4f58c6ff8d143f6fc44c
2f207042046fff7feff04f114052846fff7feff04f12800fff7feff04f13c00
fff7feff04f15000fff7feff44f62420c2f2070004604560b0bd
```

Its SHA-256 is
`6710533445c9aac3904152a43147d0e9ba9bec7eff8e7c5c6b72007c4c301fdb`.
The strict relocation contract is exactly six `R_ARM_THM_CALL` relocations at
text offsets 14, 36, 46, 54, 62, and 70, each targeting
`open_cfw_freertos_list_initialise`; there is no other executable relocation
or undefined runtime dependency.

| Profile | Source leaf | Relocated SHA-256 | Full stock replacement |
|---|---|---|---|
| Apple Clang 21.0.0 | `[0x007B28E8,0x007B2940)`, overlay offset 124,356 | `22d2909d84e02d0216a71168fdac379a576317c22dd5de6f527fb595c4668b52` | `5df32cb9` + forty NOPs; `fbd0478701f559ab96a24b759970640ffd17f30f20b36f7cb61e0e4173bf98dd` |
| exact-root Linux Clang 22.1.8 | `[0x007B3004,0x007B305C)`, overlay offset 126,176 | `dd4a36cadf6346d513ec039724a2a58309f443d31aad4e50858c5a64d95c04f6` | `5df3babc` + forty NOPs; `52fb57ebe49286360f1258cb2855a3b95abee1ed0a247e0cd3a3d6f6fc7d5e33` |

No alignment region precedes the leaf in either profile. The Apple relocation
resolves all six calls to the source-owned list initializer at `0x007AEA2C`.
The sole stock caller at `0x00454A20` remains unchanged and enters the
generated redirect.

| Profile | Overlay | Apollo-main component | Core-source package | Flash plan |
|---|---|---|---|---|
| Apple Clang 21.0.0 | 124,444 / `34c6d23ea9e1c3f01440222e44fe2af38121a02309b61efb2b15a806e0e77158` | 3,647,840 / `fd4625c32ee413abe058ffabc6a719be7af0af3d0096ce4f06b8535f01463b8b` | 4,426,294 / `188702b9f1b8c52e3ea46f33765bd9555395dd3ada0aa1233503930b0e594c97` | 690,488 / `630a0252bdd89d3f4256c7f74d8c473c11271ba2601ed33ce28433ea341fc046` |
| exact-root Linux Clang 22.1.8 | 126,264 / `62d8e21bec02a7505a39296f2e474e703b6a3989c252c6cda3fda43e12e7d236` | 3,649,660 / `5a098690012093defe0573e7f5c4cfb20ae79f77ff3aa88ce6adda3279c73764` | 4,428,114 / `0c446de88f84b8b81049b54efc94e0c40b411bfc9b2c8655cbf5b762bb846068` | 581,929 / `a13a7ffc624804bcc91484bf601e775cd14d081ca840715753af27fef2a633ad` |

The config census is 645 functions, 594 patch sites, and 76 relocated leaves.
The canonical 904-region Apple component manifest tiles all 3,647,840 bytes:
container 1/32; alignment 41/82; source-entry replacement 580/85,770; exact
load 1/6; exact replacement 7/134; official 179/3,437,236; and source compiled
95/124,580. Exact canonical package ownership is 125,215 source bytes
(2.828890%), 87,922 generated bytes (1.986357%), and 4,213,157 opaque bytes
(95.184753%) out of 4,426,294.

The coarser Apple flash-plan view is 125,200 source, 87,785 generated, and
4,213,309 opaque bytes, with 960 placed, two unresolved, and five
container-only records. Linux's corresponding view is 127,105 / 87,700 /
4,213,309 bytes, with 815 placed, two unresolved, and five container-only
records. These plan-envelope values do not replace exact canonical manifest
ownership. Canonical builder accounting is 124,626 source-owned bytes
(including 182 in-place), 85,946 generated patch-site bytes, 32 generated
wrapper bytes, and 3,437,236 opaque base bytes.

All ten original promotion gates are satisfied: the MIT and source pins,
compile-time ABI/configuration guards, eight fixed RAM bindings, exact
provider tag and explicit casts, one-symbol dependency closure, list and
selector behavior checks, full 84-byte redirect, unchanged sole caller,
independent Apple/Linux pins, and Apollo-main-only scope. The distinct
bootloader homolog remains untouched.

## Validation performed

Offline analysis and production qualification performed for this audit:

- authenticated the official package and installed application hashes;
- recomputed the stock body, neighbor, caller, boot-homolog, and upstream
  source-range hashes;
- decoded the complete main and boot bodies with Capstone;
- resolved every PC-relative main literal to its RAM value;
- decoded every outgoing main call and the sole incoming caller;
- scanned the complete application for wide, wide-conditional, narrow, and
  stored-address entry/interior references;
- authenticated the complete FreeRTOS snapshot with its offline verifier;
- reproduced the rejected candidate/provider conflict, then independently
  verified the exact-tag/explicit-cast correction on host and Cortex-M55;
- inspected the common 88-byte text and exact six-relocation closure;
- verified both profile placements, complete generated replacements, artifact
  pins, manifest tiling, and flash-plan classifications; and
- confirmed that registration and patching are Apollo-main-only.

All compilation, assembly, packaging, and analysis were offline. No firmware
was signed or flashed and no G2 hardware was operated.
