# R1 ordered startup suspension barrier in C

`runtime/native_task_barrier.c` supplies stock `0x46dcc`. It visits nine workers in stock order and reloads each current handle immediately before requesting suspension. It never skips a null handle, stops on a handshake outcome, or collects handle snapshots ahead of callbacks. The configuration is queried only after the first six requests; only full-word value 0x55 selects factory mode.

| Ordinal | Stock handle cell | Existing C owner |
| --- | --- | --- |
| 0 | 0x200066e0 | r1_event_storage.thread |
| 1 | 0x20006638 | r1_battery_thread_handle |
| 2 | 0x20006598 | r1_bae8_rx_thread |
| 3 | 0x200065c4 | r1_tx_channel1.thread |
| 10 | 0x200065e8 | r1_tx_shared.thread |
| 7 | 0x20006694 | r1_event_sensor.thread |
| 5 / 6 | 0x20006610 / 0x200066b8 | r1_event_system.thread / r1_factory_rx_thread |
| 9 | 0x2000666c | r1_touch_task_thread_handle |
| 4 | 0x20006570 | r1_protocol_service_thread |

The common 16-byte event/transmit prefixes now live in `board/native_task_contexts.h`, with compile-time size/thread-offset assertions. Three existing consumers use that shared declaration instead of repeating it. All three compiled objects and their public strong symbols are identical, confirming this interface extraction does not alter their runtime code or data. The barrier owns no handles or writable state. Volatile qualified views preserve live reads of existing context fields; scalar owners already have volatile declarations.

REA binds the 152-byte routine/literal window to the locked image. Verification passes 240 stock/C ordered-call pairs with full-word configuration and handle values, null forwarding, late configuration changes, handle replacement after each callback, failure results, masks and poisoned stacks. The expected ordinal sequence is 0/1/2/3/10/7/(5 or 6)/9/4. An additional 54 comparisons execute the actual C and stock handshake bodies, varying acknowledgement masks, error words, live shared-event-handle changes and logging gates. Notification/wait/logging leaves remain modeled; the handshake's existing raw wait-all timeout 0x5000 is retained without inventing a wall-clock conversion.

Six compiled defects are rejected: wrong transmit ordinal, truncating configuration before comparison, selecting the wrong factory worker, dropping the final worker, wrong touch ordinal and caching the touch handle before earlier callbacks. The normal probe passes after mutation testing. Ordinary void C API behavior is verified; incidental caller-saved result registers and private frames are outside the contract.

The normal open-toolchain build compiles 822 units (740 application, 82 bootloader), retaining 69 application imports with no new failures or duplicate strong symbols. This fills a startup dependency of the still-open manager implementation. Of 821 prior units, 819 object hashes match and two generated boot objects differ with build paths. Source changes in existing files are limited to shared type declarations. No G2 source or qualification selection changes. Thread construction, final application linking, manager wiring and device boot remain open.

Reproduction inputs: [task-barrier-c-review.json](task-barrier-c-review.json).
