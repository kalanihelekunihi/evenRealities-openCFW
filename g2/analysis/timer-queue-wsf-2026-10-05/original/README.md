# Timer-command queue producer evidence

This packet statically authenticates the FreeRTOS queue-send provider used by the WSF event-group ISR timer-command path. It does not emulate queue state or claim that the timer task runs.

`verify.py` checks the locked OTA and decoded image identities against the Ghidra run record; authenticates nine original code bodies against `functions-000.jsonl`; checks call targets, the timer-queue literal and relevant field offsets; and verifies that the local FreeRTOS files match their pinned Git tree blobs. It writes `results.json` and `disassembly.txt`. Re-run with `~/.local/share/opencfw/venv/bin/python g2/analysis/timer-queue-wsf-2026-10-05/original/verify.py`.

The official OTA is `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (SHA256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`). The image begins after its 32-byte preamble and is based at `0x438000` (SHA256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`). The main authenticated provider is `0x441952`, 240 bytes, SHA256 `09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08`.

## Recovered send behavior

`0x441952` checks `uxMessagesWaiting` at queue offset `0x38` against `uxLength` at `0x3c`. For ordinary send-to-back (copy-position argument zero), a full queue returns `0`; available space routes through `0x441ed8`. That helper reads `uxItemSize` at `0x40`, copies from the caller message to `pcWriteTo` at `+0x04` via `0x439be4`, advances and wraps the write pointer using `pcTail` at `+0x08`, then increments the count at `+0x38`.

There is a noteworthy corpus boundary around the memory-copy routine: the Ghidra row for `0x439be4` records 104 instruction bytes in split code ranges, while its authenticated SHA covers the contiguous 166-byte envelope through `0x439c89`. That envelope contains an adjacent Ghidra entry at `0x439c04` and control-flow fallthrough into the bulk-copy sequence. The verifier records the distinction rather than treating the split-range byte count as the hash span.

After copying, the send path inspects signed `cTxLock` at `+0x45`. At `-1` (unlocked), it checks the receive-wait list at `+0x24`; if nonempty it calls `0x455370`, whose authenticated body removes a waiting task from the event list and transitions it toward readiness. If that helper reports a higher-priority task, the sender writes `1` to the optional `pxHigherPriorityTaskWoken` location. The producer does not yield. When the queue is locked, the sender updates the TX lock bookkeeping for later list processing. It returns `1` for a copied message and restores the saved BASEPRI value through `0x5fa0ba` on normal return paths.

The ARM32 queue offsets follow the pinned `QueueDefinition` member sequence and the original loads/stores: `pcHead=+0x00`, `pcWriteTo=+0x04`, queue union `pcTail=+0x08`/`pcReadFrom=+0x0c`, send wait list `+0x10`, receive wait list `+0x24`, message count `+0x38`, length `+0x3c`, item size `+0x40`, `cRxLock=+0x44`, and `cTxLock=+0x45`. `List_t` slots occupy `0x14` bytes each in this layout. Optional trailing fields and exact build configuration are outside this packet.

The adjacent authenticated producer `0x47eb4a` constructs four words (`0xfffffffe`, callback pointer, parameter 1, parameter 2) and calls `0x441952` with the queue handle loaded through the literal at `0x47eb6c` (`0x20074ab0`), message pointer, higher-priority-task-woken pointer, and copy-position zero. In this use the payload is the event-group callback command described in [the event-group packet](../../event-group-wsf-2026-10-05/original/README.md).

## Pinned source and limits

The local source snapshot at `g2/build/foundation/freertos-upstream/` matches FreeRTOS/FreeRTOS-Kernel tree commit `def7d2df2b0506d3d249334974f51e427c17a41c`, version V10.5.1. `queue.c` has SHA256 `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` and Git blob SHA1 `5c872e0302839d96aab90919788fdc2b0be1c09e`; its license is MIT. The corresponding pinned `timers.c` and `event_groups.c` identities are in `results.json`.

Source `xQueueGenericSendFromISR` supports the decoded branches: it does not block when full, copies on success, may remove a blocked receiver when `cTxLock` is unlocked, records a higher-priority wake through the caller pointer, and returns pass/full. The image independently supplies the relevant original call and field evidence. This is source-backed semantic correspondence, not a source compilation or byte-match claim. The exact firmware `FreeRTOSConfig.h` and complete task/scheduler source are not present in this subset. Queue creation success, queue occupancy, actual timer-daemon scheduling, callback execution, and hardware/ISR timing remain unverified. Assert-failure tails intentionally fault and loop; they are recorded as invalid-input boundaries, not tested return behavior.
