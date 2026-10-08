# OpenCFW rescan — 2026-10-08 16:32 UTC

Compared with the preceding 15:22 UTC scan, the same `g2/components` inventory (`.c`, `.h`, `.S`) grew **562 → 576 files**: **14 added, none modified or removed**. All additions are C/header files. **532 are in the Git index, 44 are untracked, zero are ignored.** Counts include public-source scaffolds and superseded implementations; they are not a count of complete firmware functions.

## New source and evidence

| Component additions | Recorded validation | Meaning and limits |
| --- | --- | --- |
| `case/deferred_event_offline/deferred.c,h` | 1,936 PASS | Actual queue-copy and ISR deferred-event producer paths; reconstructed queue prefix and 16-byte callback message. No daemon scheduling proof. |
| `case/deferred_consumer_offline/consumer.c,h` | 189 PASS | Actual dequeue/indirect event callback in coherent synthetic queues. Selected negative-command messages, empty wait lists; no live scheduling proof. |
| `case/event_waiters_offline/waiters.c`, `case/event_waiter_interfaces/event_abi.h` | 384 PASS; successor multiwaiter batch 3,456 PASS | Actual task unblock/list movement, event snapshot and accumulated clear masks. Multiple matching waiters receive the same pre-clear snapshot. Synthetic coherent TCB/list state. |
| `case/frame_dispatch_offline/dispatch.c,h` | 1,230 PASS | Polling clears event 8 before dispatch; legacy DE decoding and binary routing. Command children are entry boundaries, not executed handlers. |
| `case/binary_forward_offline/forward.c` | 2,160 PASS | Nonlocal commands excluding command 3D. Validates selected lengths and posts event before copying shared payload; no demonstrated concurrency failure. |
| `audio/thread_flags_offline/flags.c` | 1,440 PASS | Real notification providers; setter ORs then queries full value. Setting zero still marks notification received. Nonwaiting fixtures. |
| `audio/notification_wake_offline/wake.c,h` | 864 PASS | Actual delayed/ready or pending-ready list transitions. Suspended scheduler leaves state item delayed while event item becomes pending-ready. Resume/switch execution excluded. |
| `audio/exit_cleanup_offline/exit.c` | 20 PASS | Selected logger-disabled exit prefix. Initial event request is not proof of DMA quiescence. Real synthetic ISR errors are ignored before handles clear; hardware reachability unproven. |
| `audio/notification_wait_offline/wait.c` | **Unsealed work in progress**, 768 PASS recorded, including 120 blocking entry boundaries | Positive blocking cases stop before kernel block entry. Pending timeout/scheduler completion is not tested; no final report or seal yet. |

The previously unsealed frame callback and event wrapper now have deliverable manifests. Their old 4,830 parser and 336 modeled-wrapper cases are not newly executed coverage. A separate new queue-version batch records 120 stock/public V10.4.3 agreements and 54 differences against selected V10.5.1 behavior under explicit task-count scaffolding; this is scoped version discrimination, not proof of the entire SDK/kernel release.

## Practical findings

Case binary forwarding accepts mode 0 with an 8-bit length field, and nonzero mode with a little-endian 16-bit length field. The selected branch posts flag 0x20 or 0x400 **before** copying all accepted bytes into shared buffer `0x200001B4`; it still copies when the actual null-event wrapper rejects the event. This identifies ordering and ownership questions for subsequent app/CFW analysis, without establishing a runtime race. Local destination 2, command 3D, trailer validation and live scheduling remain outside this batch.

Audio notifications expose a clearer distinction between notification value, notification-received marker, and actual task readiness. Scheduler suspension can defer readiness despite received flags. Cleanup begins by requesting an event; successful producer shutdown or acknowledgment has not been demonstrated. Queue/timer destruction and producer quiescence therefore remain prerequisites for any safe owned-buffer design.

**Address correction:** use dispatcher table `0x20003FBC`, proven by locked literal at `0x53CEB4`, as documented in [notification wake successor](../audio-notification-wake-closure-2026-10-08/REPORT.md). Earlier sealed audio reports containing `0x20073FBC` are superseded on this point and remain preserved. Initialized table contents and startup mapping are still unresolved.

## Preservation and Git visibility

All **904 sealed manifest entries**, **110 audit inputs**, and **four candidate checkpoints** match their recorded hashes. HEAD is unchanged at `36ff5930a4e832156f9ee3111e83480756ebef37`. Scan read existing reports/results; it did not run tests, generators, firmware or hardware operations, and did not change the Git index or existing source files.

`git check-ignore -v --no-index` reports no matching ignore rule for any of the 576 inventoried sources. `.gitignore:15:build/` still hides `g2/build/probe.elf`. No nested component ignore file, `.git/info/exclude` or configured global excludes file was found; one worktree is registered. **Ignored build artifacts do not explain missing source in this scope.** Untracked offline modules explain why committed-file views show less work than the working directory.

This is progress in bounded reconstructed source and firmware understanding, not a complete source-built or byte-identical firmware bundle. PASS counts are existing author-recorded results, with their fixture and boundary limitations; this scan is not an independent behavior rerun. There is no global source-exhaustion conclusion.

## Navigation

- [Exact inventory delta, hashes, Git visibility and preservation](snapshot.json)
- [Deferred producer](../case-deferred-event-closure-2026-10-08/REPORT.md), [consumer](../case-deferred-consumer-closure-2026-10-08/REPORT.md)
- [Waiters](../case-event-waiters-closure-2026-10-08/REPORT.md), [multiple waiters](../case-multiwaiter-closure-2026-10-08/REPORT.md), [queue version evidence](../case-queue-version-closure-2026-10-08/REPORT.md)
- [Frame dispatch](../case-frame-dispatch-closure-2026-10-08/REPORT.md), [binary forwarding](../case-binary-forward-closure-2026-10-08/REPORT.md)
- [Audio flag setter](../audio-thread-flags-closure-2026-10-08/REPORT.md), [waiting-task wake and address correction](../audio-notification-wake-closure-2026-10-08/REPORT.md), [exit cleanup](../audio-exit-cleanup-closure-2026-10-08/REPORT.md)
- [Unsealed wait source](../../components/audio/notification_wait_offline/wait.c), [unsealed recorded results](../audio-notification-wait-closure-2026-10-08/results.json)
