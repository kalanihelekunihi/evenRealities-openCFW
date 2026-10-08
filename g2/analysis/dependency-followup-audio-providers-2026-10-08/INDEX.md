# Audio lifetime and provider successors — 2026-10-08

This additive index preserves earlier sealed reports. Use successor evidence where older fixtures/entry boundaries are superseded. Offline C models are not production firmware or a complete source build.

| New batch | Source / functions | New validation | Remaining boundary |
| --- | --- | --- | --- |
| [Timer auxiliary and sizing](../audio-timer-aux-lifetime-closure-2026-10-08/REPORT.md) | `audio/timer_aux_lifetime_offline/aux.c`: delete0x44953E, adapter0x449398, due-single-shot0x47E88C/0x47E83A, minimum-block arithmetic0x456110 | 50 lifecycle +38 size cases | Synthetic command/expiry/reuse interleaving; actual user callback body stops before entry |
| [Encoder setup](../audio-encoder-setup-closure-2026-10-08/REPORT.md) | `audio/encoder_setup_offline/setup.c,h`: reset0x57A926, setup0x59123A/0x591374, selectors0x590D3C/0x590D74 | 181 cases including3 authenticated configs | Encode body/memory lifetime and full workspace requirements |
| [I2S stop](../audio-i2s-stop-closure-2026-10-08/REPORT.md) | `audio/i2s_stop_offline/stop.c`:0x590C62, selected matching-source0x58FDBC | 1,296 cases | Passive MMIO; source-changing branches outside selected helper |
| [Last-client release](../audio-i2s-clock-release-closure-2026-10-08/REPORT.md) | `audio/i2s_clock_release_offline/clock.c`:0x4C4016,0x4D391E | 88 cases | Power command register is not physical completion |
| [File close](../audio-file-close-closure-2026-10-08/REPORT.md) | `audio/file_close_offline/close.c`:0x4745F4, actual backend/mutex/TLSF peers | 48 cases | Dirty flush/media state and failures; heap-lock error logger before entry |
| [Delayed block](../audio-delayed-block-closure-2026-10-08/REPORT.md) | `audio/delayed_block_offline/block.c`:0x455FA8 | 96 cases | Caller protection, tick expiration and completed blocked call |
| [PendSV context](../audio-pendsv-closure-2026-10-08/REPORT.md) | `audio/pendsv_offline/context.c`:0x5FA0C8, selected ready selector0x4551B4 | 32 cases, integer+FP | Before BX EXC_RETURN; no hardware entry/return or live schedule |

**Allocator correction:** `malloc(680)` minimum block is696, `malloc(8)` minimum24. Prior688-byte queue cleanup block was constructed; it did not establish actual allocation outcome. Do not edit/reinterpret the older sealed fixture as a stock allocator test.

**Earlier retained findings:** dispatcher initialization is proven at0x20003FBC; event8 is an exit acknowledgment emitted before cleanup, not proof of completed teardown. [Initializer](../audio-dispatch-initializer-closure-2026-10-08/REPORT.md), [stop ordering](../audio-stop-handshake-closure-2026-10-08/REPORT.md), [task configuration](../audio-task-configuration-closure-2026-10-08/REPORT.md), [control callbacks](../audio-control-callbacks-closure-2026-10-08/REPORT.md), [diagnostic deinit](../audio-diagnostic-deinit-closure-2026-10-08/REPORT.md), [timer command drain](../audio-timer-commands-closure-2026-10-08/REPORT.md), [pending-ready resume](../audio-pending-resume-closure-2026-10-08/REPORT.md).

Provenance hashes include code and associated literal/table/vector ranges. A table/vector mechanically decoded in a disassembly export is data, not claimed executable coverage. The PendSV vector range0x438038..0x43803C is the pointer0x5FA0C9.

Available next source leads remain: broader I2S power/uninitialize0x590648/0x5900CE, tick processing0x45504C, actual timer-daemon command-vs-expiry loop. Mounted file/cache/block contents are required to validate dirty-close I/O without supplying fake storage results. A real scheduler/device trace would be needed to establish actual concurrent callback reuse and physical shutdown reachability. These are specific limits; no global source-exhaustion claim is made.
