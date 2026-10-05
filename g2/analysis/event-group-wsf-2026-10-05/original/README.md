# WSF FreeRTOS event-group handoff

This bounded packet follows the actual FreeRTOS event-group object used by WSF, through task-context set/wait and the deferred interrupt path. Its final reproducible outputs are [results-final.json](results-final.json) and [disassembly-final.txt](disassembly-final.txt); rerun `~/.local/share/opencfw/venv/bin/python g2/analysis/event-group-wsf-2026-10-05/original/verify.py` from the repository root. The verifier passes 17 authenticated function bodies, the 8-byte callback interval, direct-call sequences, literal values, and pinned-source identities.

The bytes are from the official `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`); the decoded main image begins at `0x438000` after the 32-byte preamble and hashes to `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Function hashes and extents are checked against the authenticated Ghidra `RUN.json` and `functions-000.jsonl` under `g2/research/corpus/apollo-main/ghidra/open-2026-09-29`.

## Handle and object layout

The cell at `0x20074ef0` is an `EventGroupHandle_t`, not a FreeRTOS task handle. `WsfOsInit` at `0x52b9b2` calls `0x47ebd8` when that cell is zero and stores the returned pointer there. The allocator call requests `0x20` bytes, clears the first word, initializes a list at `group+4`, and clears a metadata byte at `group+0x1c`. The layout matches the pinned `EventGroup_t`: the event bit word is at offset 0 and `List_t xTasksWaitingForBits` begins at offset 4. In its 32-bit list, the sentinel `xListEnd` starts at `group+0x0c`; the first-item pointer used for traversal is at `group+0x10`.

The dispatcher at `0x52b9d0` calls WaitBits with exact arguments `(handle, 1, clearOnExit=1, waitForAll=0, timeout=0xffffffff)`. It waits for any requested bit, then clears it on exit. The requested mask is one bit, so the any/all condition would coincide, but the recovered ABI flag is `waitForAll=0`. `WsfSetOsSpecificEvent` at `0x52b8d8` sets bit 1 (mask `1`) through the task-context set-bits body at `0x47ed76`, or the ISR API thunk at `0x47ee4a`. The same provider functions are used by the CMSIS `osEventFlagsNew`, `osEventFlagsSet`, and `osEventFlagsWait` wrappers at `0x449590`, `0x4495e4`, and `0x44969c`.

## Waiter and set-bit behavior

The authenticated `0x47ed76` body corresponds to `xEventGroupSetBits`. It ORs bits into the group, suspends scheduling, and walks the waiter list from its head to the `xListEnd` sentinel. Each task's event-list item value holds the requested bits plus control bits in the upper byte. The implementation tests any-bit waits or all-bit waits according to flag `0x04000000`; matches are removed through `vTaskRemoveFromUnorderedEventList` at `0x45547c`, with the current event bits plus unblock marker `0x02000000`. Requested bits from matched clear-on-exit waiters are accumulated and cleared after the scan, so one waiter does not consume the bits before other matching waiters are checked. The provider resumes scheduling and returns the resulting group bits.

The authenticated `0x47ebf8` body corresponds to `xEventGroupWaitBits`. It tests current bits first. If they do not satisfy the request and the timeout is nonzero, it stores the wait mask and flags in the task event-list item and places it on the list at `group+4` through `vTaskPlaceOnUnorderedEventList` at `0x4552ae`. It suspends and resumes scheduler state around the shared-list operations. The binary uses the 32-bit FreeRTOS event-bit control layout: clear-on-exit `0x01000000`, unblock-due-to-set `0x02000000`, wait-for-all `0x04000000`, control mask `0xff000000`. These wait/set bodies operate on an event-group waiter list and call task event-list/scheduler helpers; they do not call direct task-notification APIs.

## Interrupt set-bits path

The ISR thunk at `0x47ee4a` loads the Thumb callback pointer `0x47ee1f` (code starts at `0x47ee1e`) and forwards the event-group pointer, bit mask, and `higherPriorityTaskWoken` pointer to `0x47eb4a`. That provider writes a 16-byte command record on its stack: `0xfffffffe`, callback pointer, event-group pointer, and bit mask. It then calls queue-send boundary `0x441952` with the message, the original higher-priority-woken pointer, and final argument zero.

The timer queue handle is loaded through literal word `0x47eb6c`, whose value is `0x20074ab0`; the code then dereferences that global cell. The adjacent word at `0x47eb70` is `0x20074ab4` and is not the literal used by this load. Callback pointer literal `0x47ee5c` contains `0x47ee1f`. The callback body at `0x47ee1e` invokes task-context set-bits at `0x47ed76` with the saved group and bits. Therefore an ISR set request is queued for callback execution; this code path does not mutate the group by directly calling task-context `xEventGroupSetBits` from the interrupt.

The pinned FreeRTOS `timers.c` confirms the queue-command structure: `xTimerPendFunctionCallFromISR` fills a callback command and calls `xQueueSendFromISR(xTimerQueue, ...)`; timer-daemon command processing invokes the queued callback for negative command IDs. Pinned `event_groups.c` implements that callback by calling `xEventGroupSetBits(group, bits)`. This is semantic source correspondence, not a compiler-byte match.

## Pinned source and limits

The cached `event_groups.c` and `timers.c` match Git blob IDs in FreeRTOS Kernel tree `def7d2df2b0506d3d249334974f51e427c17a41c`; their headers identify FreeRTOS Kernel V10.5.1 and SPDX MIT. Their SHA-256 values and pinned blob IDs are recorded in `results.json`.

The local upstream subset does not include `tasks.c`, `queue.c`, or the exact `FreeRTOSConfig.h`. This packet therefore bounds task-list and queue providers at their authenticated call sites and uses the pinned event-group/timer source only for their stated contracts. Queue-full behavior, timer-queue initialization at any particular interrupt, daemon scheduling, and scheduler/ISR execution were not tested. No byte-identical source build is claimed.

The first `results.json` records the wait-all flag incorrectly as enabled, and `results-corrected.json` predates the final argument-byte assertion. Use only the `*-final` outputs; the call-site bytes load `r3=0` before the WaitBits call.
