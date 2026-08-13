# EasyLogger G2 asynchronous event-worker source-candidate audit

Status: production-excluded clean-room candidate. No overlay, firmware
manifest, package, signer, hardware, or flash state is changed.

## Result

The downstream G2 `elog_async_api.c` event worker and initializer are now
bounded as two stock units and recreated as an explicit orchestration
candidate:

| Role | Stock range | Bytes | SHA-256 |
|---|---:|---:|---|
| event worker | `[0x00448E8E,0x00448F3C)` | 174 | `85d2ceaa34ffcbc26f644ad3ca331e5720f9cca5a3b84191cedffda9b019aeec` |
| event/thread initializer | `[0x00448F44,0x00448F78)` | 52 | `fd00bc4276ff3b9a0ebdf1f5b48dac48433f61741a3c169b694aa88642496b81` |

This is G2-local clean-room code, not Armink EasyLogger source. Its value is
to make ownership and ordering explicit; no upstream commit can replace it.

## Recovered contract

The worker emits its start diagnostic and then waits forever on the event
handle at `0x20074570`, mask `0x0F`, CMSIS option `0x02`, and timeout
`0xFFFFFFFF`. Each returned word is dispatched in stock order:

1. bit `0x01`: drain EasyLogger records, then clear `0x01`;
2. bit `0x02`: invoke the database handler, then clear `0x02`;
3. bit `0x08`: invoke the upload handler, then clear `0x08`;
4. bit `0x04`: emit the retained KV diagnostic, invoke seven first-party
   persistence handlers in their stock order, then clear `0x04`.

The initializer creates an unconfigured CMSIS event-flags object. Failure is
diagnosed and no thread is created. Success creates the worker with the exact
36-byte Arm target attribute contract: name `elog_async_handler_thread`,
stack size `0x800`, priority `0x17`, and all other words zero. The thread
creation return is deliberately ignored.

All CMSIS APIs, diagnostics, and first-party handlers remain explicit retained
seams. The helper dispatcher exists only to make one wake deterministic under
host tests; the production-shaped worker loops forever around the same helper.

## Qualification boundary

The host oracle covers all 16 event-bit combinations through representative
combined and isolated words, exact handler and clear ordering, ignored high
error bits, initializer success/failure, event-handle publication, thread
entry/argument, and every thread-attribute field. The focused test also pins
the complete stock caller/pointer topology, literal strings, source artifacts,
target function bodies, undefined seams, and relocations under Apple and Linux
Clang profiles. Apple Clang 21 produces a 3,984-byte object with SHA-256
`31cb546015d03f291c2b8fd33ce5b8f588508d165f2dc34264a3371092c6a18a`;
Linux Clang 22.1.8 produces a 3,964-byte object with SHA-256
`2efc693539aed187c24a7b766dde449130107760c50f59c9ba23dfb031226130`.
All three function bodies and every relocation are identical between profiles.

This candidate closes local semantic opacity in `elog_async_api.c`; production
admission still needs target concurrency/hardware stress and an atomic review
of every retained first-party persistence handler. Image-specific EasyLogger
transport ownership remains separate.

Verification:

```sh
python3 -m unittest -v tests.test_easylogger_async_worker_candidate
```
