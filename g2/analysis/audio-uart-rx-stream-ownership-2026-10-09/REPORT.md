# UART RX staging-to-stream copy boundary

**The logger's RX callback copies staged UART bytes into a FreeRTOS stream, then discards the accepted-byte count.** The outer receive flush resets staging count even if the stream accepted only a prefix. Copied bytes become stream-owned; rejected suffix is not retained by this tested path. This is a recovered contract and controlled pressure result, not measured live data loss.

Eight selected bodies preserve unchanged public FreeRTOS10.5.1 / pinned Apollo510 source text: create/spaces/ISRsend/write-message/write-bytes/bytes-in-buffer/initialize and UART FIFO read. Fixed stock36B ABI/config definitions and bounded copy/fill/mask support are explicit adaptations. Provenance/body hashes and retained licenses are in source-reference.json; no producing-toolchain or complete UART/RTOS attribution.

**564 original-versus-source comparisons PASS**, plus **18 actual channel1 receive/callback compositions PASS**, all bound to the final native ELF receipt. Cases cover stream/message admission, partial writes, wraparound, trigger/waiter paths, constructor size/sentinel geometry, FIFO empty/error/null-destination behavior, plus before-allocator and before-task-notification cuts. Native heap/notification aliases use explicit supplied allocation/task-notification returns in completion fixtures; real scheduler effects are not inferred. A synthetic notifier writes the supplied woken flag and returns, allowing cleanup/BASEPRI restore checks, not task wake closure.

Original instructions execute one at a time, preserving bytes/flags; native addresses are guarded. RX compositions whitelist only actual channel flush/callback plus native code. FIFO byte/status supply and stream pressure are synthetic. No actual vector delivery, peripheral state, DMA or hardware RX. [Results](results.json), [compositions](rx-composition-results.json), [exact receipt](reproduction-receipt.json), [native interfaces](../../components/audio/uart_rx_stream_offline/README.md).

## Concrete recovered facts

- Channel1 RX staging pointer is200B9C20; descriptor20000CFC+8 tracks accumulated bytes. Threshold path requests15bytes and accumulates; timeout path requests16 and invokes callback, then resets count. Both ignore FIFO-read's status but increment by its valid-byte count.
- Callback0x5415E6 (Thumb5415E7), installed by actual logger initializer0x54171C, uses stream handle global**200748BC**. It calls0x57E05E when count>0; the accepted count is discarded. Raw instructions establish this address—do not substitute nearby global addresses from assumptions.
- Generic stream constructor0x57DEEA requests one2085byte allocation for the logger's requested2048 usable bytes:36Bcontrol plus2049Bstorage. Trigger1,stream mode,callbacksNULL. Allocation is not physically run here; source comparisons supply a nonnull fixture allocation and separately cut before it. Actual main heap failure behavior remains in the earlier sealed batch.
- ISR stream-send synchronously copies available bytes and publishes head afterward. Full/partial stream fixtures copy0/2bytes from205 and the outer callback drops205/203byte suffix respectively. Empty stream copies205. Immediate reuse of staging leaves copied stream unchanged.
- Message-buffer source paths add4byte lengths and reject a whole message if insufficient room. They are tested source behavior, not the logger's configured mode.
- Notification is conditional on accepted bytes, trigger level and waiting-receiver pointer. A before-notifier cut proves exact provider call/BASEPRI30 state; synthetic returns validate subsequent receiver-pointer clearing/mask restoration only. The callback's own body has no yield call; full vector scheduling remains unknown.

[Readable flow and ownership table](pseudocode.md). The previously proven [TX batch](../audio-uart-tx-ownership-2026-10-09/REPORT.md) distinguishes borrowed TX source, queue copies, FIFO acceptance and completion flags; those claims are unchanged.

## Remaining actionable work

Actual notification provider0x455DC0 and stream receive0x57E136 can close receiver/task-copy boundaries without assuming task handover. UART power0x58DBB8 and configure0x58E09E have exact pinned source leads; source power retains/restores8registers, checks saved-state validity, and calls clock/peripheral providers. Physical power/baud remains outside offline proof. Channel3 has actual1024byteTX queue and deserves separate routing/ISR/drain analysis. Shared formatter reentrancy still requires meaningful call/preemption evidence; no speculative patch or live race claim.

These static leads are not exhausted or externally blocked. No commits/device writes/shared-state edits. All prior seals,110inputs,fourcheckpoints and staging are preserved.
