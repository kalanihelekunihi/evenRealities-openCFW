# CMSIS-FreeRTOS timer-constructor source-candidate audit

Status: production-integrated and dual-toolchain replayed  
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: private `TimerCallback` and public `osTimerNew`

## Result

The linked CMSIS-FreeRTOS timer constructor is source-closable with its private
callback over providers that OpenCFW already owns. The selected oracle is Arm
CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; the exact `cmsis_os2.c` blob was
first introduced by `13acfbef7be85119fc6bc56832c455d4547d92c7`.

| Routine | Stock span | Bytes | SHA-256 | External callers |
|---|---|---:|---|---:|
| private `TimerCallback` | `[0x00449398,0x004493B0)` | 24 | `bf6d5f543d1e89b912b7a2f6d108791ef9158d4e206ec00c42ea7187d166d5ab` | callback-only |
| `osTimerNew` | `[0x004493B0,0x00449498)` | 232 | `164802e5b4bea4aaeef33a296bf4641ad47579367fc04accb3d62b04a0cc8146` | 12 |

Only `osTimerNew` needs a stock redirect. The source constructor stores the
source-owned callback address in every newly created timer, so the adjacent
private stock callback becomes unreachable from the admitted path without
overwriting useful authenticated evidence.

## ABI and behavior closure

- The recovered G2 `StaticTimer_t` threshold is 44 bytes.
- A control block of at least 52 bytes stores the 8-byte callback record at
  `cb_mem + 44`; smaller valid static control blocks allocate the record.
- Dynamically allocated callback records are tagged in bit zero of the timer
  context and are untagged by the callback and timer-delete wrapper.
- The constructor rejects ISR calls, null application callbacks, and mixed
  `cb_mem`/`cb_size` states; it frees only dynamically allocated records on
  creation failure.
- Timer type is interpreted through its low byte: zero is one-shot and every
  nonzero low byte is periodic.

Every fixed executable edge is source-owned: private `IRQ_Context`, heap_4
allocate/free, static and dynamic timer construction, and timer context lookup.
The constructor therefore introduces no TCB-field dependency, queue seam, WSF
hook, or opaque callback ABI.

## Qualification pins

`runtime_cmsis_timer_new.c` is pinned at 5,023 bytes / SHA-256
`a090ccbb1938c7ff475b25ebd424fbaa480bace78a232814ab0124eba17c2684`.
The host fixture is pinned at 3,103 bytes / SHA-256
`11e3b4d3a91f1937dd36d786f83af28e8787910e26c76434d69587c1b0015c52`.
Behavior tests cover rejection paths, allocation failure, static and dynamic
construction, callback invocation, record tagging, and selective cleanup.

The freestanding Thumb-2 target bodies are:

| Routine | Bytes | Unrelocated SHA-256 |
|---|---:|---|
| private callback | 24 | `18011968869555744b904c0083ef7e1f3af44522a0d795c0518902ea3969e1ba` |
| constructor | 212 | `76ab027748ff511b9e88b65ce73cd289c95a29c634cccf1698cbe8c1df67874e` |

| Toolchain | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple clang 21 | `132792` / `0d9ac12a972d158d82f74b864ce08db808e64d49df05826bf5676633c582d2c1` | `3656188` / `1f0508840b0654ffdf535f022a96294e179f3c67cc79a0c3acd3305a3b4fc3ab` | `4434682` / `69a00a465ab4ac3d7bccde4afcd607797b82fa1e2b679f26ee67addcb6d2fe47` |
| Homebrew clang 22.1.8 | `134672` / `1d158250bc2c9c4239926999a57cdb7a52df9ea5dc599f15ea1f91700f28e436` | `3658068` / `f6100c444a32ad9f3d597200a40cc673035578ea0f89c6da4b2c458daba36ae9` | `4436562` / `50f976944895ad5a3c4d1a39e67d390532fc1f6ec5421b0afa7ba914725c7766` |

Both profiles were recorded once and replayed through ordinary fail-closed
component and package builds. The Linux compiler emits a 224-byte constructor
instead of Apple clang's 212-byte body; both retain the same nine relocation
edges and behavior contract. No signing, flashing, reset, boot, or hardware
operation was performed.

## Reproduction

```sh
make -C openCFW cmsis-freertos-timer-new
```
