# Cordio WSF buffer/message source recovery

## Outcome

The G2 stock image now has a closed three-function WSF buffer module and a
closed seven-function WSF message module. Together they account for ten named
functions and 556 authenticated code bytes. Both have host-tested,
production-excluded source candidates; no production overlay or manifest was
changed.

The buffer implementation is the Ambiq FreeRTOS port family. Official
AmbiqSuite R2.4.2 and R2.5.1 contain the same 13,241-byte proprietary source
blob, while the retained G2 path uses the later `third_party\cordio` packaging.
That file is an identity/behavior oracle only and is not redistributed. The
seven message definitions have a better route: their texts exactly match the
Apache-2.0 Packetcraft r19.02 source. The clean message candidate therefore
uses the public source route and does not depend on copying Ambiq's
proprietary-header copy.

## Stock boundaries

The authority is
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, raw load base
`0x00437FE0`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `WsfBufInit` | `[0x00530364,0x00530446)` | 226 | `a12554f5…5605` |
| `WsfBufAlloc` | `[0x00530446,0x005304D4)` | 142 | `307ff7dd…d48` |
| `WsfBufFree` | `[0x005304D4,0x00530512)` | 62 | `6148f827…58f` |
| `WsfMsgDataAlloc` | `[0x004BF990,0x004BF99E)` | 14 | `980bff91…af1` |
| `WsfMsgAlloc` | `[0x004BF99E,0x004BF9B0)` | 18 | `d763f423…ec5` |
| `WsfMsgFree` | `[0x004BF9B0,0x004BF9BA)` | 10 | `52a3c4e9…ead` |
| `WsfMsgSend` | `[0x004BF9BA,0x004BF9DE)` | 36 | `a568f74c…c70` |
| `WsfMsgEnq` | `[0x004BF9DE,0x004BF9EC)` | 14 | `a3de2489…5ed` |
| `WsfMsgDeq` | `[0x004BF9EC,0x004BFA00)` | 20 | `a0a7fa1b…52d` |
| `WsfMsgPeek` | `[0x004BFA00,0x004BFA0E)` | 14 | `f2982c0d…18e` |

The buffer aggregate is 430 bytes with SHA-256 `01bc4ff2…906f`; the message
aggregate is 126 bytes with SHA-256 `31eadd38…3dd`. `WsfBufInit` was absent
from the Ghidra function output but is independently bounded by its sole real
call at `0x004B7F7C`, source-order semantics, and raw Rizin disassembly.
`WsfBufAlloc` and `WsfBufFree` are present in the authenticated Lorelei
corpus. All seven message functions are contiguous and present in source
order.

The fail-closed analyzer scans all halfword-aligned BL encodings, verifies
every expected body and callee relocation, and rejects aligned stored
entry/interior pointers. This intentionally retains real callers in bodies
Ghidra missed, including the OS dispatcher's `WsfMsgFree` and `WsfMsgDeq`
calls. There are no aligned stored pointers into either module and no external
interior ingress.

## Exact G2 pool configuration and SRAM layout

The stack initializer calls:

```text
WsfBufInit(0x2940, 0x2004FA98, 4, 0x200003B0)
```

The existing authenticated IAR scatter decoder recovers the 16 descriptor
bytes at `0x200003B0` as
`100008002000040040000a00e0011400`, SHA-256
`042b678d2537323145f48d4c7e0ae3deb68d58bf8b81a0cb97a4b1aa0b522c2e`.

| Pool | Requested/rounded size | Count | Stock buffer range | Bytes |
|---:|---:|---:|---:|---:|
| 0 | 16 | 8 | `[0x2004FAC8,0x2004FB48)` | 128 |
| 1 | 32 | 4 | `[0x2004FB48,0x2004FBC8)` | 128 |
| 2 | 64 | 10 | `[0x2004FBC8,0x2004FE48)` | 640 |
| 3 | 480 | 20 | `[0x2004FE48,0x200523C8)` | 9,600 |

Four 12-byte internal pool records occupy `[0x2004FA98,0x2004FAC8)`.
Metadata plus buffers consume `0x2930` of the `0x2940` region, leaving 16
bytes. The runtime globals are the pool-memory pointer at `0x20074EEC`, pool
count byte at `0x20075044`, and used-length halfword at `0x20074F4A`.

The stock target ABI is:

- input descriptor: `uint16_t len +0`, `uint8_t count +2`, size 4;
- free block: next pointer `+0`, marker `+4`, size 8;
- internal pool: descriptor `+0`, start pointer `+4`, free pointer `+8`, size
  12;
- internal message: next pointer `+0`, handler byte `+4`, size 8;
- public message payload: internal message address plus eight bytes.

Allocation is ascending first-fit and continues to larger pools when a fitting
pool is empty. Free classifies in descending pool-start order, writes
`0xFAABD00D`, and pushes at the free-list head. The stock assert-disabled
behavior has no surviving range, alignment, null, or double-free guard.

## Configuration and upstream pins

Stock mechanics establish `WSF_BUF_FREE_CHECK=TRUE`,
`WSF_BUF_STATS=FALSE`, `WSF_BUF_STATS_HIST=FALSE`, and `WSF_OS_DIAG=FALSE`.
Assertions and success/info traces are effectively disabled; the allocation
failure warning is retained through the local seven-argument logger seam.

The strongest buffer source-family pin is AmbiqSuite R2.5.1 archive SHA-256
`87b03680…4133`, path
`third_party/cordio/wsf/sources/port/freertos/wsf_buf.c`, source SHA-256
`e13de141…a08`, Git blob `550bcf45275be013547cf49587606b591b1ee5d6`.
R2.4.2 has the identical source blob, so this module alone does not
discriminate the point release. The retained `cordio` path favors R2.5.1-or-
later packaging, and the timer/OS discriminators independently select the
R2.5.1 implementation family. Four buffer stat/diagnostic APIs remain
source-family inventory only; no independent stock body or caller was found,
so they are not included in the 430-byte stock coverage.

For messages, Packetcraft r19.02 commit
`86372d84ef0386d8834ed036e613c8f2ded1ff16`, blob
`9f475dc631ba5001542b07d1098ba5fc52bdc7b8`, supplies the exact seven
Apache-2.0 definitions. r20.05c retains those definitions but adds
`WsfMsgNPeek`; the G2 cluster ends after `WsfMsgPeek`, so the extra API is not
claimed.

## Lorelei matrix and candidate status

Lorelei compiled two source/config variants across 13 pinned ARM GCC profiles:
78 function comparisons and 26 complete closure links in 3.463 seconds. Every
closure linked with zero unresolved symbols. There were zero raw and zero
strict-normalized matches. The best aggregate lane was the stock warning seam
at `-O3`, with 34 bytes of total absolute size difference. Best remaining
per-function gaps are 10 bytes for Init, 10 for Alloc, and two for Free. The
warning seam improves the aggregate gap by 44 bytes over the best no-trace
shape, supporting—but not proving—the recovered logger configuration.

The complete compact artifact is
`research/readiness/wsf-buf/`, 16,946 bytes,
SHA-256 `f961c25e…77e`. Its 21 inner checks authenticate the comparison ledger,
flags, shims, source identities, provider/include closure, and timings. It
contains neither proprietary source nor object/disassembly caches.

The buffer candidate is independently expressed MIT clean-room code;
the message candidate uses the Apache-2.0 public route. Focused tests compile
the buffer/message/queue closure for Cortex-M4 with `-Werror`, validate pool
construction, first-fit fallback, marker transitions, failure handling,
message header hiding, enqueue/dequeue/peek, and the OS dispatcher adapters.
All ten bounded entries are production-routed. Three buffer leaves compile to
582 bytes with five strict relocations; seven message leaves compile to 114
bytes plus 12 alignment bytes with eight strict relocations. The message
allocation/free seams target the maintained buffer leaves. Live allocator,
dispatcher, and controller concurrency remains blocked by unavailable
authorized responsive hardware evidence.

## Reproduce

```sh
python3 tools/analyze_g2_cordio_wsf_buf_msg.py --json
python3 -m unittest -v \
  tests/test_analyze_g2_cordio_wsf_buf_msg.py \
  tests/test_runtime_cordio_wsf_buf_msg_candidate.py \
  tests/test_verify_research_corpus.py
```

`make cordio-wsf-runtime-closure` is the combined software gate. No image was
signed, flashed, or installed.
