# Cordio ATT server write processor source audit

Status date: 2026-08-25
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `atts_write.c` object is bounded at
`[0x005A5D94,0x005A6260)`, 1,228 bytes, SHA-256
`5ff375c13498c4194fda9790e70ee116e8257cfc659c6aa6cfd95f4fc3b34ebc`.
Four linked definitions contribute 1,220 code bytes; their source-order
concatenation hashes to
`77f20f9bedbee5c74d98b4282c874f0bff39d0713e4a11ab64e08c66d417a9f4`.
The eight-byte tail holds `attsCb=0x2006E5F0` and
`pAttCfg=0x200004B4`.

| function | stock span | bytes | SHA-256 |
|---|---:|---:|---|
| `attsExecPrepWrite` | `[0x5A5D94,0x5A5E3A)` | 166 | `f1cc4fe5...d8244` |
| `attsProcWrite` | `[0x5A5E3A,0x5A5FC2)` | 392 | `db8b9b06...e3971` |
| `attsProcPrepWriteReq` | `[0x5A5FC2,0x5A6170)` | 430 | `110a713e...10bed` |
| `attsProcExecWriteReq` | `[0x5A6170,0x5A6258)` | 232 | `90375b68...c8c3c` |

`AttsContinueWriteReq` is the sole source-only definition. The next function
at `0x005A6260` is unrelated; there is no standalone continuation body,
direct caller, stored entry, or source-shaped candidate elsewhere in the
image. Stock can mark a write response pending when a callback returns
`ATT_RSP_PENDING`, but this product does not link the public API that later
completes such a pending response.

The helper has one internal caller. The three processors have no direct
callers and are reached from the initialized method table. Twenty-eight
decoded direct calls leave the TU. One raw BL-like halfword at `0x005A5FE6`
is the second half of a valid wide `uxtab` and is excluded. The whole-image
stored scan finds one exact entry-valued word in the compressed initializer
stream plus three unaligned accidental interior byte windows; none is an
accepted runtime pointer. No direct branch reaches a strict interior. The TU
has no retained source path.

## Dispatch, behavior, and ABI

The authenticated boot decoder reconstructs these live cells in the 18-entry
`attsProcFcnTbl` at `0x2000045C`:

| method | live processor |
|---:|---|
| 9 | `attsProcWrite` (`0x005A5E3B`) |
| 10 | `attsProcWrite` (`0x005A5E3B`) |
| 11 | `attsProcPrepWriteReq` (`0x005A5FC3`) |
| 12 | `attsProcExecWriteReq` (`0x005A6171`) |

Methods 9 and 10 share the write request/command processor. It validates the
handle, permissions, fixed/variable maximum length, and optional group/CCC
callback, then writes the value and responds only for a request. Prepare write
also validates offset and the configured queue limit, allocates a variable
record, and enqueues it. Execute write cancels the queue or validates every
queued record before dequeueing, committing, and freeing each record.

The prepared-write queues begin at `attsCb+0x238`, with one eight-byte WSF
queue per connection. The stock indexes them by the CCB connection ID and
enforces `pAttCfg->numPrepWrites`; this independently matches the EATT-era,
three-connection layout. The server CCB main pointer, connection ID, and slot
are at `+0x10`, `+0x24`, and `+0x25`.

## Source lineage

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import are byte-identical: Git blob
`1b41582c58124a49014317b987f304dd216ce100`, 14,245 bytes, SHA-256
`8c205dcd4162d5b3e30322bb13dbd552568a5aa62ecddabf7f0a69edad17d7b1`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. Stock's per-bearer slot usage
and three-connection prepared-write queues exclude the smaller 13,992-byte
r19/AmbiqSuite 2.x file. The source is Apache-2.0; neither public nor later
import commit is claimed as the resolved historical G2 producer.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_atts_write.py --json
make cordio-atts-write-closure
```

## Production closure

`runtime_cordio_atts_write.c` now owns all four linked entries. Four guarded
redirects replace 1,220 authenticated stock body bytes with 1,644 selector-
isolated Cortex-M55 text bytes plus 12 alignment bytes under 25 strict
relocations. The maintained implementation uses the source-owned WSF buffer
and queue providers, preserves the fixed queue/configuration/CCC callback ABI,
and implements the exact r20 request, command, prepare, execute, cancel,
callback, CCC, error, and pending-response behavior. Host tests exercise those
paths, including validate-before-commit queue handling. All four linked leaves
and the source-only continuation API compile independently for the target.

The current canonical overlay is 340,072 bytes, SHA-256
`849bffe5646022d3beec5ea492dc9c3b2ffabccc4f84a9b0449317d257525834`;
the Apollo component is 3,863,468 bytes, SHA-256
`15fd0568b892d3f4e2de5a994ccc4f46ff2a04bc45d537a322c216b67068eb9d`;
and the deterministic package is 4,641,962 bytes, SHA-256
`82097f8c735fc3ec9d162a1c8379e8b7ea2f8562b0b58eca297b222018e5b94c`.
The flash plan has 4,716 placed, two unresolved evidence-only, five
container-only, and six protected regions. No image was signed, flashed, or
installed.

Live ATT request/command, prepare/execute/cancel, deferred callback completion,
peer interoperability, controller timing, and EM9305 interaction remain
blocked by unavailable authorized responsive G2 and peer capture evidence.
This closes all non-null write methods in the stock 18-entry ATT server table;
it does not declare the wider ATT or G2 firmware functionally complete.
