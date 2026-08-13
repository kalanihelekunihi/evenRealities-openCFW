# Cordio optional ATT server read processor source audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `atts_read.c` object is bounded at
`[0x0056D93C,0x0056E4F8)`, 3,004 bytes, SHA-256
`d54722d4facdc1e58a4636d61041c020ffe6ffd9e68a887fe1b87e7d7abbd89c`.
All seven source definitions link and contribute 2,984 code bytes; their
source-order concatenation hashes to
`8c449cbb036fcc8a2aac443a6263142d3dd7ae6b5bf3175fdf0311ef2b3bf760`.
The final 20 bytes are the owned `attsCb` and UUID literal pool. The two small
functions between the preceding `smp_sc_main.c` object and `0x0056D93C` are
not attributed to this TU.

| function | stock span | bytes | SHA-256 |
|---|---:|---:|---|
| `attsFindUuidInRange` | `[0x56D93C,0x56D9EC)` | 176 | `a87c995a...febb0c` |
| `attsFindServiceGroupEnd` | `[0x56D9EC,0x56DA9E)` | 178 | `4eaf3776...5006fb` |
| `attsProcReadBlobReq` | `[0x56DA9E,0x56DC04)` | 358 | `71188999...35ef8` |
| `attsProcFindTypeReq` | `[0x56DC04,0x56DD9C)` | 408 | `9739daf6...a581f` |
| `attsProcReadTypeReq` | `[0x56DD9C,0x56E0DE)` | 834 | `04c0ee12...bb1d1` |
| `attsProcReadMultReq` | `[0x56E0DE,0x56E26C)` | 398 | `643ba549...08e87` |
| `attsProcReadGroupTypeReq` | `[0x56E26C,0x56E4E4)` | 632 | `d0a197e6...223e1` |

Nine direct BL sites reach the two range helpers. The five processors enter
through initialized methods 3, 4, 6, 7, and 8; none has a direct caller.
Across the seven bodies, 50 decoded direct calls reach the common ATT/ATTS,
message, buffer, comparison, and copy providers. Three additional raw
BL-looking halfwords are the second halves of valid wide `uxtab`
instructions and are explicitly excluded from the call count.

The whole-image stored-value scan finds the five expected odd entries in the
compressed initializer stream and one unaligned accidental byte window at
`0x00643387`. It finds no accepted stored interior pointer. The direct-branch
sweep likewise finds no branch into a strict interior. This TU has no retained
source-path string.

## Dispatch and behavior

The authenticated boot decoder reconstructs these live roots in the 18-entry
`attsProcFcnTbl` at `0x2000045C`:

| method | live processor |
|---:|---|
| 3 | `attsProcFindTypeReq` (`0x0056DC05`) |
| 4 | `attsProcReadTypeReq` (`0x0056DD9D`) |
| 6 | `attsProcReadBlobReq` (`0x0056DA9F`) |
| 7 | `attsProcReadMultReq` (`0x0056E0DF`) |
| 8 | `attsProcReadGroupTypeReq` (`0x0056E26D`) |

`attsFindUuidInRange` walks the handle-sorted group queue and returns the
first matching attribute. `attsFindServiceGroupEnd` finds the next primary or
secondary service and returns the preceding handle. Read-blob validates the
handle, permission, and offset, invokes group/CCC callbacks when configured,
and returns an MTU-bounded suffix. Find-by-type-value returns matching handle
ranges. Read-by-type emits homogeneous handle/value records and defers the
database-hash response through the CSF path when required. Read-multiple
concatenates bounded values. Read-by-group-type accepts the primary-service
group type and returns handle/end-handle/value records.

The fit checks are pinned at three machine-code windows:

- `[0x0056DD2C,0x0056DD38)` for find-by-type-value;
- `[0x0056E034,0x0056E048)` for read-by-type;
- `[0x0056E42E,0x0056E442)` for read-by-group-type.

The latter two explicitly derive the available endpoint by subtracting the
dynamic attribute length before comparing the output pointer. Together the
three windows match the subtraction-safe bounds used by Ambiq's R4.4.1
source to avoid IAR high-optimization service-discovery failures. They are a
strong behavioral-source match, not proof that the later import commit built
the historical image.

`attsCb=0x2006E5F0`; the server CCB main pointer and slot are at `+0x10` and
`+0x25`. The literal tail references primary-service UUID `0x2800`,
secondary-service UUID `0x2801`, database-hash UUID `0x2B2A`, and the local
read-group UUID constants.

## Source lineage

Packetcraft r20.05c is the public lower bound: Git blob
`4e168d052592520878118944adc230e87393ad94`, 26,413 bytes, SHA-256
`371ad472a1b2b2a6d9be876107c590e74f97a113b1d9d40138d24cc2f2a8ca55`.
The linked CSF database-hash branch and r20 server ABI exclude the 25,878-byte
r19/AmbiqSuite 2.x source.

The closest authenticated behavioral oracle is the later official
AmbiqSuite R4.4.1 import at AmbiqAI/neuralSPOT commit
`4264b9309e03064ffad13a0468d5d0c1110c5288`: Git blob
`52a7f290710c12ecba0850175c9bc1fe21f8e0aa`, 26,859 bytes, SHA-256
`b07b3b63a4c6f6bc0c7f1efa11c30f17cef39360c0619db7830f86647a74a425`.
Relative to r20 it changes only the three fit-check spellings described
above. Both files are Apache-2.0. The later import is corroboration and a
reconstruction oracle, not a resolved historical generating commit.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_atts_read.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_read
```

The next table-owned server tranche is `atts_write.c`, which owns the write,
prepare-write, execute-write, and signed-write processors.
