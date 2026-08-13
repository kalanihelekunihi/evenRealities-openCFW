# EasyLogger G2 asynchronous consumer source-candidate audit

Status: production-excluded clean-room candidate. No overlay, firmware
manifest, package, signer, hardware, or flash state is changed.

## Result

The remaining bounded record-consumer portion of downstream G2
`elog_async_api.c` is now source-recreated in
`runtime_easylogger_async_consumer_candidate.c/.h`. It closes four stock
entries:

| Role | Stock range | Bytes | SHA-256 |
|---|---:|---:|---|
| primary callback configure | `[0x00448CAC,0x00448CB8)` | 12 | `1180c9bacb221aee63f27640eff748d5c5c520bcacf79741011346d7d2316e34` |
| secondary callback configure | `[0x00448CB8,0x00448CC4)` | 12 | `42b6a860fc6638bac89dee864761d06efe0d53d358f157cf8ebc0ece251482bd` |
| default metadata set | `[0x00448CC4,0x00448CCC)` | 8 | `97ebd76595cc6f18cf192034b671bc1ec2150350a9451f21e21db354baf99fde` |
| record drain | `[0x00448DD2,0x00448E2A)` | 88 | `43ac9598579abc817bc013e3f65ad69639f72f7bf03cbe6ca3bdd8596e5612e7` |

This is G2-local clean-room code, not Armink EasyLogger source. The retained
path `easylogger/src/elog_async_api.c` is absent from authenticated official
history, while upstream `elog_async.c` uses an incompatible byte-ring design.

## Recovered contract

The two configuration entries store an 8-bit enable value and callback pointer
into the two pairs at `0x20073B90`; both return zero. The metadata setter writes
the byte at `0x20004546`.

The drain returns zero without touching the queue when ready byte `0x20074FC0`
is clear. Otherwise it dequeues at most 256 records. For each record it calls
the primary `(payload,length)` callback only when metadata bit zero, the
primary enable byte, and the callback pointer are all nonzero. It always
recycles the record, increments the cumulative processed counter at statistics
offset `+0x00`, and returns the number processed. The secondary callback pair
is configured here but is not consumed by this drain.

The 256-iteration cap is sufficient to empty the 255-record allocatable pool
after event notifications coalesce. The callback deliberately receives no
level; the queue's dummy rotation likewise preserves stock's omission of the
level byte.

## Qualification

The host oracle covers ready gating, callback enable/metadata/null-pointer
gates, exact payload and length delivery, unconditional recycling, cumulative
statistics, empty queues, and the 256-record cap with a 300-record scripted
source. Complete stock caller lists, interior ingress, stored pointers, source
artifacts, target functions, undefined seams, and every relocation are pinned.

Apple Clang 21 produces a 2,996-byte object with SHA-256
`e4b33afe75f57531cb822532de9a5d0ed099f2979d97df065ad6c993c52d6235`.
Linux Clang 22.1.8 independently produces a 2,976-byte object with SHA-256
`2fcbb8785c1fac0dfeb66133cefb9582fcfc32ce9c9eab7a131ce28d971b1e33`.
All four function bodies are identical between the profiles, and the focused
test pins every relocation and undefined seam. The event worker at
`[0x00448E8E,0x00448F3C)` and event/thread initializer at
`[0x00448F44,0x00448F78)` remain separate from this consumer, but are now
closed by the companion worker candidate. They orchestrate CMSIS event flags
and multiple first-party handlers rather than implementing a queue algorithm.

Verification:

```sh
python3 -m unittest -v tests.test_easylogger_async_consumer_candidate
```
