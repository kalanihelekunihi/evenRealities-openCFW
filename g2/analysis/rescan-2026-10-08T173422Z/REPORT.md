# OpenCFW rescan — 2026-10-08 17:34 UTC

Compared with the preceding [16:32 scan](../rescan-2026-10-08T163250Z/REPORT.md), the same `g2/components` inventory (`.c`, `.h`, `.S`) grew **576 → 587 files: 11 added, none modified or removed**. **532 files are in the Git index, 55 are untracked, and zero are ignored.** These counts include public scaffolds and superseded implementations; they do not measure whole-firmware source completeness.

## New work and recorded validation

| Added component | Recorded validation | New understanding and boundary |
| --- | --- | --- |
| `audio/startup_unpack_offline/unpack.c` | Original/C/Python agreement over 17,752 initialized bytes | Authenticated startup record establishes eight initial dispatcher rows at `0x20003FBC`; not runtime mutation coverage. |
| `case/local_commands_offline/local.c` | 240 PASS | Bounded local-command provider reconstruction; see its report for child boundaries. |
| `audio/queue_delete_offline/delete.c` | 64 PASS | Actual allocator free/coalescing for constructed queue blocks; no live waiter cleanup or producer quiescence. |
| `audio/stop_handshake_offline/stop.c` | 72 PASS | Stop flag fanout and manager event acknowledgment ordering; no physical DMA completion. |
| `audio/task_configuration_offline/config.c` | 3 PASS | Stock audio task priority 47, 8,192-byte static stack, and 50×12-byte queue setup; allocation originally stopped at the 680-byte request. |
| `audio/control_callbacks_offline/control.c` | 576 PASS | Role/variant-specific I2S/PDM stop branches; hardware-provider entry boundaries remain. |
| `audio/diagnostic_deinit_offline/deinit.c` | 64 PASS | Disable message can be queued before owner validation; file-close and encoder setup children stop at entry. |
| `audio/timer_commands_offline/timer.c,h` | 32 PASS | Stop/delete commands copy 16-byte messages; timer-object deletion occurs in the daemon, with separate static/dynamic ownership. |
| `audio/pending_resume_offline/resume.c` | 84 PASS | Pending-ready tasks move into priority ready lists when suspension ends; stops before yielding/context switching. |
| `audio/timer_aux_lifetime_offline/aux.c` | **Unsealed work in progress:** 50 PASS lifecycle comparisons, 38 PASS allocator comparisons | Dynamic callback auxiliary storage is released after successful delete enqueue, before daemon deletion; late-due/reuse behavior is synthetic, not a demonstrated hardware failure. |

The previously unsealed notification-wait batch now has a manifest and report. Its 768 recorded cases, including 120 blocking-entry boundaries, are existing coverage, not newly rerun results.

## Material corrections and implications

The stop-handshake successor establishes that exit sets manager event **8 before timer/queue cleanup**. This acknowledges the audio exit path reaching that point; it does **not** establish complete resource destruction, DMA quiescence or safe producer shutdown. The earlier report's interpretation of the event as only a request is superseded by [this report](../audio-stop-handshake-closure-2026-10-08/REPORT.md); sealed historical files remain preserved.

The startup decoder now proves the initial audio dispatch table, resolving the prior scan's open initialization question. Audio notification values, received markers, pending-ready lists, and actual context switching remain distinct states. The resume batch advances list ownership understanding, without modeling a completed scheduler switch.

The **unsealed** timer/allocator batch records a further sizing correction: actual `0x456110` arithmetic requires a minimum **696-byte block for a 680-byte payload**, and **24 bytes for an 8-byte callback auxiliary payload**. This is allocator overhead/alignment, not a change to the payload sizes. Earlier cleanup fixtures used a constructed 688-byte queue block and did not execute allocation of the 680-byte request; those fixtures are not proof of the stock allocation size. Larger whole-block allocations can occur when a small remainder is not split. Inspect [allocator results](../audio-timer-aux-lifetime-closure-2026-10-08/allocator-size-results.json) and [source](../../components/audio/timer_aux_lifetime_offline/aux.c); the batch still lacks a final report/seal.

These findings improve prerequisites for owned-buffer and shutdown designs. They do not yet justify a firmware patch: hardware-stop providers, file-close/encoder children, blocking paths and real scheduling remain bounded dependencies.

## Preservation and visibility

All **1,010 sealed entries**, **110 audit inputs**, and **four candidate checkpoints** match their recorded hashes. This is 106 additional sealed entries since the preceding scan. HEAD remains `36ff5930a4e832156f9ee3111e83480756ebef37`. This scan read hashes and existing results; it did not rerun behavioral tests, generators or firmware, or change existing source/index/campaign state.

`git check-ignore -v --no-index` matches none of the 587 sources. `.gitignore:15:build/` still hides `g2/build/probe.elf`. No nested component ignore, `.git/info/exclude`, or configured global excludes file was found; one worktree is registered. **Gitignore does not explain missing source in this inventory.** Committed-only views omit the 55 untracked files.

This is bounded reconstructed source and firmware understanding, not a complete source-built or byte-identical bundle. PASS counts are author-recorded results with synthetic state and explicit execution boundaries; this rescan independently checked preservation, not behavioral correctness.

## Navigation

- [Exact delta, hashes, Git status and checkpoints](snapshot.json)
- [Startup decoding](../audio-dispatch-initializer-closure-2026-10-08/REPORT.md), [case local commands](../case-local-commands-closure-2026-10-08/REPORT.md)
- [Queue deletion](../audio-queue-delete-closure-2026-10-08/REPORT.md), [stop handshake](../audio-stop-handshake-closure-2026-10-08/REPORT.md), [task configuration](../audio-task-configuration-closure-2026-10-08/REPORT.md)
- [Control callbacks](../audio-control-callbacks-closure-2026-10-08/REPORT.md), [diagnostic teardown](../audio-diagnostic-deinit-closure-2026-10-08/REPORT.md)
- [Timer commands](../audio-timer-commands-closure-2026-10-08/REPORT.md), [pending resume](../audio-pending-resume-closure-2026-10-08/REPORT.md), [notification wait](../audio-notification-wait-closure-2026-10-08/REPORT.md)
- [Unsealed timer lifecycle results](../audio-timer-aux-lifetime-closure-2026-10-08/results.json), [allocator results](../audio-timer-aux-lifetime-closure-2026-10-08/allocator-size-results.json)
