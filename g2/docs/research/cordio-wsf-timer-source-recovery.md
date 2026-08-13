# G2 Cordio/Ambiq FreeRTOS WSF timer recovery

Status: production-excluded source recovery. The official image and the
authenticated 64-shard Ghidra corpus are read only; no overlay, production
manifest, firmware byte, or hardware state changed.

## Result

The retained translation-unit path is
`third_party\cordio\wsf\sources\port\freertos\wsf_timer.c`. Its complete
function cluster is `[0x0052A3FC,0x0052A614)`, 536 bytes, SHA-256
`e410a5b1c5e5d7a475ba75fcefecd99015c4a3e77e2fdec841ec124167cd0458`.
Eleven function boundaries are now named and have clean-room behavioral
source. Ghidra found seven; direct calls recover four missed entries:

| Stock span | Bytes | Recovered identity | State |
|---|---:|---|---|
| `[0x0052A3FC,0x0052A424)` | 40 | `wsfTimerRemove` | Fully bounded and behaviorally recreated |
| `[0x0052A424,0x0052A468)` | 68 | `wsfTimerInsert` | Fully bounded and behaviorally recreated |
| `[0x0052A468,0x0052A474)` | 12 | `WsfTimer_handler` | Fully bounded; behaviorally recreated; callback-pointer closure |
| `[0x0052A474,0x0052A4B8)` | 68 | `WsfTimerInit` | Fully bounded and behaviorally recreated |
| `[0x0052A4B8,0x0052A4C4)` | 12 | `WsfTimerStartSec` | Fully bounded and behaviorally recreated |
| `[0x0052A4C4,0x0052A4D2)` | 14 | `WsfTimerStartMs` | Fully bounded and behaviorally recreated |
| `[0x0052A4D2,0x0052A4E6)` | 20 | `WsfTimerStop` | Fully bounded and behaviorally recreated |
| `[0x0052A4E6,0x0052A51A)` | 52 | `WsfTimerUpdate` | Fully bounded and behaviorally recreated |
| `[0x0052A51A,0x0052A542)` | 40 | `WsfTimerNextExpiration(bool_t *)` | Fully bounded; clean-room candidate and r19.02 semantic oracle |
| `[0x0052A542,0x0052A574)` | 50 | `WsfTimerServiceExpired(wsfTaskId_t)` | Fully bounded; clean-room candidate and r19.02/r20.05 semantic oracle |
| `[0x0052A574,0x0052A614)` | 160 | `WsfTimerUpdateTicks(void)` | Fully bounded; clean-room vendor-port recreation |

The direct callers are exactly `0x004B7F6A`, `0x0052A59A`, `0x0052BA32`,
and `{0x0052B9D4,0x0052BA96}`, respectively. The latter three external calls
are within the coherent dispatcher `[0x0052B9D0,0x0052BAB8)`, 232 bytes,
SHA-256
`49ba08ce0c35eb58c098babd1ad0e4d68c303c67bf8e2543be552511732474d8`.
Across all eleven entries there are exactly 53 direct BL callers. The callback
has no BL ingress and is referenced only by the Thumb pointer `0x0052A469` in
the literal word at `0x0052A61C`. An exhaustive scan found no external B.W or
narrow branches into an entry or function interior and no other stored entry
or interior pointer. This closes the replacement ingress surface, but no
production relocation or placement is claimed.

The previously missed `WsfTimerInit` entry is independently witnessed by the
BL at `0x004B7F6A`. Adding it raises the raw recovery total from seven to eight
functions / 1,104 bytes and the reviewed effective Apollo discovery count
from 7,377 to **7,378**. The immutable Ghidra baseline remains 7,370.

## Source lineage

Official Packetcraft history contains no
`wsf/sources/port/freertos/wsf_timer.c`, but the official
[AmbiqSuite 2.5.1 archive](http://s3.asia.ambiqmicro.com/downloads/AmbiqSuite-R2.5.1.zip)
does. The original September 2020 S3 object is 200,161,418 bytes, SHA-256
`87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133`,
S3 version ID `SZxNfetLb6ZNVkN_tZ76GH00R.h44Mf0`. Its exact retained-path
source is 11,288 bytes, SHA-256
`4d6641c8de197367a6c1561738b389afd164321b879264cd795796c80ab55dd7`,
Git blob `91ae7bb7d9883587822914c2586e95e4d08f165c`. Ambiq's
[2.5.1 release notes](https://contentportal.ambiq.com/documents/20123/388370/Release-Notes-SDK2.5.1.pdf)
identify the Cordio host and FreeRTOS 10.1.1 integration. The source carries a
proprietary ARM license, so OpenCFW records its identity but does not
redistribute it.

This is the selected exact implementation/source family, not merely a
semantic oracle. Function order, APIs, private structure layout, queue
algorithms, timer name, tick conversions, FreeRTOS calls, globals, and
constants all map directly to stock. The official 2.4.2 source differs by one
statement: it lacks `g_ui32LastTime = xTaskGetTickCount()` after successful
timer creation. Stock contains exactly that call/store, excluding unmodified
2.4.2 and selecting 2.5.1-or-later blob `91ae7bb7…`. The two-row authenticated
ledger is `tools/manifests/ambiqsuite-cordio-wsf-timer-provenance.tsv`,
SHA-256 `e5bd4f8800b3e1045ac4f9219adc7fa3281093b47263f72b3305704f508bea9a`.

The same blob is independently present in AmbiqAI's official
[`nsx-ambiq-sdk` commit `9f36432d`](https://github.com/AmbiqAI/nsx-ambiq-sdk/commit/9f36432d875060ca301675131b40452ecf8377ca),
but that 2026 import is corroboration rather than the historical firmware pin.
Retained assertion metadata names line 409 while the archived invocation is
around lines 404–405, so minor local textual/configuration drift remains and
byte-identical original text is not claimed.

`tools/manifests/ambiqsuite-cordio-wsf-timer-function-map.tsv`, SHA-256
`e06c07aeb4766d4c6c4ac0168572f96c21957d2f85365a700f977e57e77e265e`,
maps every stock function span/hash to the official 2.5.1 source line span and
span hash without copying the proprietary source.

Packetcraft [r19.02 commit
`86372d84`](https://github.com/packetcraft-inc/cordio/commit/86372d84ef0386d8834ed036e613c8f2ded1ff16)
contains `wsf/sources/port/baremetal/wsf_timer.c`, Git blob
`d2cced51a06a87f7ca26369b01e4a8b0ec325346`, SHA-256
`1dd5bb6aab28031793227a152686d692b2c04878de4bf6d2d8bef187081a0a4e`.
Its [`WsfTimerNextExpiration(bool_t *)`](https://github.com/packetcraft-inc/cordio/blob/86372d84ef0386d8834ed036e613c8f2ded1ff16/wsf/sources/port/baremetal/wsf_timer.c#L327-L349)
and [`WsfTimerServiceExpired`](https://github.com/packetcraft-inc/cordio/blob/86372d84ef0386d8834ed036e613c8f2ded1ff16/wsf/sources/port/baremetal/wsf_timer.c#L360-L393)
match the stock control flow and API shape.

Packetcraft r20.05 through r20.05c all use one byte-identical bare-metal timer
body: blob `df2c9dd1e94b26e2e989f01dcc82a1cf418b58d2`, SHA-256
`35fd98d54047480071df7c8475a822bceec2f27e13c2960b063991e4100d673b`.
At [r20.05](https://github.com/packetcraft-inc/cordio/commit/eeb34839755da1c19cc85b8795cc863483c16ef0),
the next-expiration API changed to private `wsfTimerNextExpiration(void)`.
The stock bool-pointer form therefore preserves r19.02-era WSF semantics even
though the independently audited G2 ATT/DM bodies require r20.05-or-later.
Packetcraft r19.02 remains a public semantic ancestry oracle; AmbiqSuite 2.5.1
is the stronger exact implementation-family pin for this translation unit.

## Recovered target ABI and memory

The stock `wsfTimer_t` layout is:

| Field | Offset |
|---|---:|
| `pNext` | `+0x00` |
| `ticks` | `+0x04` |
| `msg` | `+0x08` |
| `handlerId` | `+0x0C` |
| `isStarted` | `+0x0D` |
| structure size | `0x10` |

This reverses the public r20.05c header's `msg`/`ticks` order, so that header
cannot be linked against the stock port unchanged. The dispatcher confirms
the result independently by passing `timer + 8` as the message and reading
the handler at `+0x0C`.

The stock port also differs from the public r20.05c conversion macros:
`WsfTimerStartSec` uses low-32-bit `seconds * 100`, and `WsfTimerStartMs` uses
unsigned truncating `milliseconds / 10`; neither adds the public comparator's
extra tick. `WsfTimerInit` always clears the queue, creates a one-shot
FreeRTOS timer named `WSF Timer` with initial period 10 only when its handle is
null, and refreshes the saved RTOS tick only after successful creation.

| Address | Size | Meaning | State |
|---|---:|---|---|
| `0x200741B0` | 8 | `wsfQueue_t` head/tail | Fully decoded |
| `0x20074EF4` | 4 | FreeRTOS timer handle | Fully decoded |
| `0x20074EF8` | 4 | last FreeRTOS tick count | Fully decoded |
| `0x20075045` | 1 | WSF critical-section nesting depth | Fully decoded |
| `[0x0052A614,0x0052A63C)` | 40 | module literal/global/string-pointer table | Fully decoded data |

`WsfTaskLock`/`WsfTaskUnlock` are the eight-byte wrappers at `0x0052B8C8`
and `0x0052B8D0`. They route through `WsfCsEnter`/`WsfCsExit`; first entry
disables interrupts and final exit enables them. These bodies and hashes are
enforced by `tools/analyze_g2_cordio_wsf_timer.py`.

## Clean-room candidate and completeness estimate

The production-excluded files are:

- `components/shared/cordio/runtime_cordio_wsf_timer_candidate.c`, 7,652
  bytes, SHA-256
  `def199a7179981092894a10627a243c121c7cf221fd35b6ecd9423e1cf600223`;
- `components/shared/cordio/runtime_cordio_wsf_timer_candidate.h`, 3,990
  bytes, SHA-256
  `86ff13950babe599ee73e5cb9d6eea133179ee1c0c2c8499205eb5e452b3e0b9`.

The header now imports the shared clean-room WSF queue ABI rather than
redeclaring timer-specific queue prototypes. This is an integration-only ABI
cleanup; the timer implementation object is unchanged.

Host tests cover initialization and failure, callback dispatch, sorted
insertion and reinsertion, removal and stop, second/millisecond conversions,
expiration/update/service behavior, lock/unlock, elapsed-tick conversion,
FreeRTOS command `4`, period scaling, wait value `100`, and the failure seam.
The candidate behaviorally recreates all eleven functions / 536 stock code
bytes. It is not linked, and exact IAR output, original FreeRTOS source text,
the exact logging/assert backend, and final placement remain unresolved.

Estimated timer-module progress is **95–98% semantic/source-family identification**: all 536
code bytes have function boundaries, caller/callee closure, and behavioral
source; all four missed functions have direct-call closure; and the critical
data ABI is known. The remaining 2–5% is exact local text/config drift within
the pinned Ambiq family, IAR build provenance, production
relocation/placement, exact logging/assert integration, and target-output
qualification. Packetcraft
Cordio overall remains **80–85% identified** because the wider HCI/trace,
application, and vendor-port boundaries are still unresolved.

Package ownership is unchanged: 131,755 source, 93,424 generated, and
4,207,731 opaque/cut-forward bytes in the 4,432,910-byte Apple package;
opaque share remains **94.920289%**. Research candidates do not count as
source-owned firmware bytes.

## Lorelei candidate matrix

Lorelei authenticated r19.02 and r20.05, applied only the recovered stock
structure order, and compiled eight Cortex-M55/GCC 13.2.1 rows (`-O2`/`-Os`,
inlining disabled). The full matrix took **0.800405321 seconds** after a
0.417307052-second source fetch. The returned compact artifact hashes to
`59a67b7a29bf00aae45692f2beb745a96e27ca1dcb20c65b5733680d289d63d1`;
its verified result ledger is integrated as
`tools/manifests/readiness-cordio-wsf-timer-matrix.tsv`, SHA-256
`5609187015274a97cb734c6f47106e3fa9f65d05ee0873c10f4eebab60054323`.

| Source/config | Next-expiration | Service-expired | Match verdict |
|---|---:|---:|---|
| r19.02 `-O2` | 48 B | 48 B | No raw or strict-normalized match |
| r19.02 `-Os` | **40 B** | 48 B | Size-exact first body; no raw or strict-normalized match |
| r20.05 `-O2` | 28 B | 48 B | No match; missing bool-output ABI |
| r20.05 `-Os` | 28 B | 48 B | No match; missing bool-output ABI |

Stock sizes are 40 and 50 bytes. The r19.02 `-Os` size equality strengthens
the semantic/ABI discriminator but is not treated as a match. GCC/IAR
instruction selection and literal placement differ; no candidate proves exact
compiler output.

Lorelei then compiled the current eleven-function clean-room candidate across
13 GCC configurations and compared all 143 function/config rows. The complete
matrix took **2.448108512 seconds**. Every row passed `-Wall -Wextra -Werror`;
supplying the 13 explicit provider/global seams produced zero unresolved link
symbols. There were zero raw and zero strict-normalized matches. Bounded
per-function selection reaches exact stock size for 8 of 11 functions, but
size equality is not treated as source/compiler identity. Remaining best size
gaps are `WsfTimerInit` +4 bytes, `WsfTimerServiceExpired` ±2 bytes, and
`WsfTimerUpdateTicks` -12 bytes.

The returned artifact SHA-256 is
`b0c5614157d33fbeddbdfdaa88bcdd6927f58af64ce73cd274de45342c807fa6`;
its full 143-row ledger hashes to
`2da0db026a5235e3d5f61e5d59ea1bd390d0249d41b710f2a0606318a02381f1`.
Tracked compact summaries are
`tools/manifests/readiness-cordio-wsf-timer-current11-config-summary.tsv`
(SHA-256 `8b051054e4f6869eec0298f787f15ee0a8313dfa3ad06a019980a718f82e1345`)
and `tools/manifests/readiness-cordio-wsf-timer-current11-best-size.tsv`
(SHA-256 `f490ebaba0de30c981b3702014e5921b362c8829e05f7832e87af0862bdc0b42`).
The artifact and full ledger are now preserved in the repository-owned Lorelei
return corpus under `research/corpus/`; the former `/var/tmp` return is only a
working copy.
All 13 objects and closure ELFs are byte-identical to the immediately prior
comment-only source revision, independently proving that the provenance
comment changed no emitted code.

## Reproduction

```sh
python3 tools/verify_research_corpus.py \
  --extract /var/tmp/opencfw-research/corpus

OPENCFW_APOLLO_GHIDRA_CORPUS=/var/tmp/opencfw-research/corpus/apollo-main/ghidra.3LC1Dq/full64-j64-auth \
  python3 tools/analyze_g2_cordio_wsf_timer.py \
    --ghidra-corpus "$OPENCFW_APOLLO_GHIDRA_CORPUS" --json

OPENCFW_APOLLO_GHIDRA_CORPUS=/var/tmp/opencfw-research/corpus/apollo-main/ghidra.3LC1Dq/full64-j64-auth \
  python3 -m unittest -v tests.test_analyze_g2_cordio_wsf_timer

python3 tools/verify_ambiqsuite_cordio_wsf_timer_archive.py \
  --archive /path/to/AmbiqSuite-R2.5.1.zip --release 2.5.1 --json
```

No build, signing, flashing, reset, or hardware operation is part of this
audit.
