# FreeRTOS queue-message-count accessor source audit

Status: **production promoted and fail-closed for Apple Clang 21.0.0 and
exact-root Linux Clang 22.1.8**.

This audit covers the adjacent official G2 FreeRTOS queue accessors
`uxQueueMessagesWaiting` at `[0x00441E66,0x00441E8A)` and
`uxQueueMessagesWaitingFromISR` at `[0x00441E8A,0x00441EA2)`. Production now
replaces both complete stock entries with generated `B.W` redirects and Thumb
NOP fill, and implements their behavior in two independently compiled,
MIT-licensed source leaves. All work described here was compilation,
packaging, and offline binary analysis. No image was signed or flashed and no
G2 hardware was operated.

## Result

The promotion is approved because the source boundary is complete and small:

- both stock bodies correspond directly to authenticated FreeRTOS-Kernel
  V10.5.1 source;
- the recovered ABI needs only the queue pointer, the volatile message-count
  field at `Queue_t + 0x38`, and three already source-owned providers;
- all six direct stock callers remain unchanged and reach the generated entry
  redirects;
- whole-application ingress analysis found no alternate or interior entry;
- both production objects reproduce exactly under the reviewed Apple and
  Linux compiler profiles; and
- both extracted leaves are relocation-free and byte-identical across the two
  profiles.

The task-context function deliberately enters and exits a critical section
around its volatile count load. The ISR function performs the same asserted
volatile load without entering a critical section or adding an interrupt-
priority assertion. Those are the authenticated upstream and stock-G2
semantics, respectively.

## Authenticated inputs

The official package and installed application are pinned independently:

| Input | Bytes | SHA-256 |
|---|---:|---|
| official OTA package | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| installed application at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |

The source baseline is the official FreeRTOS-Kernel V10.5.1 release:

- unsigned annotated tag object:
  `d7b40dbed508c305c2a32ccf3982045ec9ba8734`;
- peeled commit: `def7d2df2b0506d3d249334974f51e427c17a41c`;
- tree: `7496dfa815c3cea2f45a090c6e92d113f494b930`;
- `queue.c` Git blob: `5c872e0302839d96aab90919788fdc2b0be1c09e`;
- `queue.c`: 125,614 bytes, SHA-256
  `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894`;
- extracted `uxQueueMessagesWaiting` source body: 286 bytes, SHA-256
  `c1bd9900ed75941a9ea7f0b822c3555ec9b16e7f813bd7ddc28c6466e0c1b898`;
  and
- extracted `uxQueueMessagesWaitingFromISR` source body: 243 bytes, SHA-256
  `601fcf52884f23a83aec6a516e2f6b1df7dabd03ac75f7719e568b025f3b1c79`.

The upstream files and both production adaptations retain the FreeRTOS MIT
terms. The recovered G2 layout, fixed provider addresses, caller topology,
and patch placement are compatibility evidence, not claims about upstream
FreeRTOS provenance.

## Stock boundary and semantics

The two functions occupy one adjacent 60-byte official span whose SHA-256 is
`58090071c368481c2778f3fbb6aaff4bcfaeb89d6b416752ff458ef1bbea6efc`.
The individual boundaries are:

| Function | Official span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `uxQueueMessagesWaiting` | `[0x00441E66,0x00441E8A)` | 36 | `4c0cf73877126df740ed1609ef221c63c694ccf47722984a938758e88db42c94` |
| `uxQueueMessagesWaitingFromISR` | `[0x00441E8A,0x00441EA2)` | 24 | `669d2bc894a3f8dd00002713748a6c6a67409355d12893e0a854e06fa45d5dba` |

The boundary is additionally closed by the 192-byte predecessor
`xQueueReceiveFromISR` at `[0x00441DA6,0x00441E66)`, SHA-256
`cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4`,
and the 34-byte successor `vQueueDelete` at
`[0x00441EA2,0x00441EC4)`, SHA-256
`ab55f9fa6eb823935056d4b4030cc10df52bc8b33318abea201e61348a026bc4`.

The task-context stock body asserts its queue argument, calls critical-enter
at `0x004420D0`, loads the volatile word at queue offset `0x38`, calls
critical-exit at `0x004420E8`, and returns the word. The ISR body asserts its
argument and loads the same volatile word directly. Both assertion paths call
the source-owned assertion provider at `0x005FA0A4`; its null path preserves
the observed fail-stop store through `0xFFFFFFFF` and loop.

The exact outgoing stock calls are:

| Call site | Destination | Purpose |
|---|---|---|
| `0x00441E6E` | `0x005FA0A4` | task-context null assertion |
| `0x00441E7C` | `0x004420D0` | critical enter |
| `0x00441E82` | `0x004420E8` | critical exit |
| `0x00441E90` | `0x005FA0A4` | ISR null assertion |

All three destinations were already source-owned before this promotion, so
the leaves introduce no opaque runtime dependency.

## ABI and recovered queue layout

Both entries use the AAPCS32 Thumb ABI. `r0` carries the `QueueHandle_t`, the
return value is the unsigned 32-bit `UBaseType_t` in `r0`, pointers and words
are four bytes, and the target is little-endian Armv7E-M.

The bounded `Queue_t` contract used by the source is:

| Offset | Field |
|---:|---|
| `0x00` | head pointer |
| `0x04` | write pointer |
| `0x08` / `0x0C` | queue/semaphore union |
| `0x10` | send-wait list |
| `0x24` | receive-wait list |
| `0x38` | volatile messages waiting |
| `0x3C` | length |
| `0x40` | item size |
| `0x44` / `0x45` | receive/send locks |
| `0x46` | static-allocation flag |
| `0x48` | queue number |
| `0x4C` | queue type |

The recovered queue size is `0x50` bytes and each list is `0x14` bytes. The
relevant G2 configuration enables static and dynamic allocation, enables
trace, disables queue sets, and enables assertions. The source header uses
compile-time layout checks so a drift in the queue ABI fails the build.

## Caller closure

The task-context accessor retains three direct callers:

| Caller | BL encoding | Wrapper |
|---|---|---|
| `0x00449A2C` | `f8f71bfa` | `osMessageQueueGetCount` |
| `0x00449BE6` | `f8f73ef9` | `osSemaphoreGetCount` |
| `0x00449E5E` | `f8f702f8` | `osMemoryPoolFree` |

Its sorted caller-address digest is
`47610a67315bf7a91b9e9a25d57738f300c6bea9a67b5d5b58413410e67e968f`,
its encoding digest is
`53cc949463fe456c1981a74a08ec6e7a24dcbd8d430a6e4d9b426e250e45c4e7`,
and its address-plus-encoding record digest is
`5ad02d9fb9803dc452b61db553fc7adfe9d92950fa583a57a462cd3dd62f4aa5`.

The ISR accessor likewise retains three direct callers:

| Caller | BL encoding | Wrapper |
|---|---|---|
| `0x00449A24` | `f8f731fa` | `osMessageQueueGetCount` ISR path |
| `0x00449BDE` | `f8f754f9` | `osSemaphoreGetCount` ISR path |
| `0x00449E1C` | `f8f735f8` | `osMemoryPoolFree` ISR path |

Its sorted caller-address digest is
`81d0972b79cf47d89e7839d7faac9bd1e5d3e9e28c764637237ebf4805ee2ff2`,
its encoding digest is
`1a0af63638aadeddc54a2196edfacbefe9074197663187dcfb5014171488cb78`,
and its address-plus-encoding record digest is
`6dd73625f7075ed9bf4f4da2e238945dce5a7a9c5d35275709cd6d6af7bdc7cf`.

Whole-application scans found no other `B.W`, narrow or conditional branch,
`CBZ`/`CBNZ`, aligned even pointer, Thumb pointer, or `MOVW`/`MOVT` followed
by `BX`/`BLX` ingress to either stock interior. The six authenticated direct
callers therefore continue to enter the original addresses and then traverse
the generated redirects.

## Production source and object pins

The production implementation is deliberately split into one translation
unit per replaceable entry:

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_freertos_queue_messages_waiting.h` | 7,042 | `393d1cdd116fd8f71fabebda73a05eb8a520dc5c0e2916ca4197df9a1e4aab0c` |
| `runtime_freertos_queue_messages_waiting.c` | 2,118 | `a5ddb8530031a4510abb894b082c229725f66b3e5f4e1ff72c34137362854a04` |
| `runtime_freertos_queue_messages_waiting_from_isr.c` | 2,067 | `a73ed32264681fadabbe10dce300388bd0f9fa8821334eba2a8b65b0ff327d34` |

With the production flags, including `-fno-ident`, Apple Clang 21.0.0 and
Homebrew Clang 22.1.8 produce the same raw object pins:

| Leaf | Object bytes | Object SHA-256 |
|---|---:|---|
| task-context accessor | 852 | `24c8d8a8311ad6a094b0e92e048b0324320002d9d850441887b05ececbcc0453` |
| ISR accessor | 856 | `a69c13094a7f4afcc65f48e660ccd09293a5409b6ec94f278eab9635c31139a7` |

Each profile was compiled twice. The only allocated payload selected for
production is the named text section. The task leaf is 50 bytes, four-byte
aligned, and hashes to
`fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04`.
The ISR leaf is 34 bytes, four-byte aligned, and hashes to
`38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c`.
Their concatenated 84-byte text hashes to
`8694e95c4afe9a7f0c189dea78d83094df58961bbdc155affbbc25976d4d560f`.

Each object also contains one eight-byte CANTUNWIND `.ARM.exidx` record,
`0000000001000000`, SHA-256
`01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d`.
Its sole `R_ARM_PREL31` association relocation is metadata, not executable
closure data, and is deliberately discarded under the authenticated
CANTUNWIND policy. There are zero text relocations and zero undefined runtime
symbols.

## Placement and patch pins

| Profile | Task leaf | Alignment | ISR leaf |
|---|---|---|---|
| Apple Clang 21.0.0 | `[0x007B2858,0x007B288A)`, offset 124,212 | `[0x007B288A,0x007B288C)`, 2 B | `[0x007B288C,0x007B28AE)`, offset 124,264 |
| exact-root Linux Clang 22.1.8 | `[0x007B2F74,0x007B2FA6)`, offset 126,032 | `[0x007B2FA6,0x007B2FA8)`, 2 B | `[0x007B2FA8,0x007B2FCA)`, offset 126,084 |

The task stock span is replaced by one four-byte `B.W` followed by sixteen
Thumb NOPs. The ISR stock span is replaced by one four-byte `B.W` followed by
ten Thumb NOPs. Exact generated replacement pins are:

| Profile | Stock entry | Replacement SHA-256 | Replacement bytes |
|---|---|---|---|
| Apple | `0x00441E66` | `8b1f7a72f4e021331a04cd81707ea2cfa85712c8cf637ff3f7365c62ab5c54d2` | `70f3f7bc` + 16 x `00bf` |
| Apple | `0x00441E8A` | `bd3b32c736e57005c1cbe65a2725fb66ed5389227686ff7961793f699364e68c` | `70f3ffbc` + 10 x `00bf` |
| Linux | `0x00441E66` | `0dd88ba663317edbf9a515397f3369d4221f25889551189ff70a5b8bb68067d6` | `71f385b8` + 16 x `00bf` |
| Linux | `0x00441E8A` | `2ef6ffe002ec6b197643da1304921bbc422dc9beb124b23343f16bf187e303a1` | `71f38db8` + 10 x `00bf` |

The patch generator rechecks the stock size and SHA-256 before assembly.
After assembly, ingress checks require exactly the two stock-entry branches
to their profile-selected generated leaves and reject ingress to either leaf
interior or the two-byte alignment gap.

## Aggregate production pins

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,298 / `09c6c86c38a88905ea389eb9c2c860d6a2e559f435d225b02bb5bdc313e828d4` | 3,647,694 / `7cc8f0b58808628e930762856ba896f5b3d9bf346fd3a5ec2e50b3a46fb6cba4` | 4,426,148 / `7209ad9da1b65c4e0c988a4af43885dc8ecf8822e26117ef047b6908d316829f` |
| exact-root Linux Clang 22.1.8 | 126,118 / `db4f80dd7caa313de96580ce10050cba2ad07bc0b7495bbc3f122a29bf9dfefa` | 3,649,514 / `45ee630ef534a524d8f8dab01af2c38412f0fa9394e7a94d0ff4f781730465c2` | 4,427,968 / `44a43f3cb4d9e36acb9ab7c1064403a9786f6657f7f6a629dfd639db7e1aacc3` |

The cross-profile overlay config contains 642 functions, 591 patch sites, and
73 relocated leaves. The canonical Apollo-main manifest has 895 exactly
tiled regions:

| Address status | Regions | Bytes |
|---|---:|---:|
| container-only | 1 | 32 |
| generated alignment | 40 | 80 |
| generated source-entry replacement | 577 | 85,626 |
| generated exact load image | 1 | 6 |
| generated exact replacement | 7 | 134 |
| official blob | 177 | 3,437,380 |
| source compiled | 92 | 124,436 |

These categories sum to all 3,647,694 canonical Apollo-main bytes. Exact
whole-package ownership is 125,071 source, 87,776 generated, and 4,213,301
opaque bytes for Apple; Linux is 126,952 source, 87,715 generated, and the
same 4,213,301 opaque bytes. These exact manifest figures are distinct from
the coarser flash-plan view. That view classifies Apple as 125,056 source,
87,639 generated, and 4,213,453 opaque bytes; Linux is 126,957 source,
87,558 generated, and 4,213,453 opaque bytes. Both accounting models sum to
their complete profile-specific package and neither changes the emitted
bytes.

The earlier console-task artifact and ownership tables remain useful
phase-local records. They are not current pins and were not overwritten by
this promotion.

## Qualification gate

The focused production suite verifies authenticated snapshot provenance and
function-body hashes; source/header pins; compile-twice object identity under
both toolchains; exact text, CANTUNWIND, and relocation closure; host behavior
for valid and null handles; critical-section ordering; queue-layout asserts;
stock boundaries, outgoing calls, and caller encodings; full-span patch bytes;
whole-application branch and pointer ingress; candidate exclusion; exact
manifest tiling; and overlay, component, and package identities. The source
promotion is therefore fail-closed at source, object, patch, topology,
ownership, and aggregate-artifact layers.
