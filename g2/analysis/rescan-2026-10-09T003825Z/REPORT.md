# OpenCFW change scan — 2026-10-09 00:38 UTC

Compared with the previous 23:51 scan, component C/header/assembly inventory grew **671 → 684: 13 added, 0 modified, 0 removed**. **654 indexed, 30 untracked**. Git check-ignore matches **0** component source paths. These counts measure artifacts, not firmware completeness.

New source paths:

- `g2/components/audio/early_pcm_dispatch_offline/dispatch.c`
- `g2/components/audio/early_pcm_dispatch_offline/dispatch.h`
- `g2/components/audio/queue_cmsis_offline/blocking.c`
- `g2/components/audio/queue_cmsis_offline/cmsis.c`
- `g2/components/audio/queue_cmsis_offline/compat.h`
- `g2/components/audio/queue_cmsis_offline/queue.c`
- `g2/components/audio/queue_cmsis_offline/queue.h`
- `g2/components/audio/timer_wake_providers_offline/port.c`
- `g2/components/audio/timer_wake_providers_offline/sorted.c`
- `g2/components/audio/timer_wake_providers_offline/unlock.c`
- `g2/components/audio/timer_wake_providers_offline/unlock.h`
- `g2/components/audio/watchdog_callback_offline/watchdog.c`
- `g2/components/audio/watchdog_callback_offline/watchdog.h`

## Substantive changes

Timer wake-provider and watchdog callback batches add native queue-unlock, event wake, interrupt-mask/list helpers and watchdog message/control handling. Their sealed evidence qualifies timer handover at the port-yield boundary; it does not establish a live hardware lifetime fault.

The newer queue/CMSIS batch records **1,345 PASS comparisons** plus **504 timeout-provider comparisons**. It recovers generic queue send/receive and CMSIS context/status routing, timeout capture/check and event-placement providers. Positive-wait fixtures stop at task yield rather than fabricate resumption. Instruction-stepped original execution is used because continuous Unicorn has a documented Thumb IT-state discrepancy.

The newer early-PCM dispatch batch records **442 PASS comparisons** and **748 initializer/composition comparisons**. Buck control changes three override bits; it does not prove physical power/readiness. Callback dispatch uses known bodies with an explicit unmapped suspend-child boundary. The 748 count includes **608 reused initializer cases**; initializer source was already recovered and is not new closure.

Those latest two batches remain **unsealed and without final reports** at scan time. Their PASS files are author-recorded evidence, not independently reviewed completion. Exact receipt/hash consistency and all discovered batches are in the snapshot. No tests were rerun for this scan.

## Preservation and limits

Checked **2188 dictionary-form manifest entries**, **110 audit inputs**, and **4 checkpoints**: **0 manifest mismatches**, **0 audit mismatches**; all checkpoints match: **True**. Index unchanged during scan: **True**. HEAD: `36337d9b39ff36d318b0531f2968ca7e0554a7b1`.

New source is visible to Git; untracked files are omitted by committed-only views. Ignore rules hide build products and decompiler databases, rather than these component sources. The whole-corpus freeze, source-complete and byte-identical firmware gates remain unestablished. Synthetic MMIO, exception/scheduling limits and missing physical/runtime inputs still constrain these bounded reconstructions.

Only this report and snapshot were added. [Exact source delta, receipts and preservation evidence](snapshot.json).
