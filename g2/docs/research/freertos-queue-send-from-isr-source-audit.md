# FreeRTOS queue-send-from-ISR source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

The generic ISR send path is production source-owned from FreeRTOS-Kernel
V10.5.1 commit `def7d2df2b0506d3d249334974f51e427c17a41c` under MIT.
The admission is a closed dependency unit:

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `xQueueGenericSendFromISR` | `[0x00441952,0x00441A42)` | 240 | `09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08` |
| `prvCopyDataToQueue` | `[0x00441ED8,0x00441F5E)` | 134 | `35c79bf50852c5f61d579981278509aa156ab8e18f57b4b6d6b7a88563682e36` |
| `xTaskPriorityDisinherit` | `[0x0045596E,0x00455A12)` | 164 | `34e2c3a8b02daf3ea3f8d3d382ef3d802d48f4d65ee26fa0353d0faab51c7e93` |

The adapters preserve back/front/overwrite placement, circular-buffer wrap,
full-queue behavior, lock-count saturation, waiter wake, ISR mask/assertion
ordering, mutex-holder validation, mutex-held-count mutation, and ready-list
priority restoration. All fixed calls bind to separately source-owned list,
task-wake, task-count, interrupt-mask, and memory-copy providers.

Apple emits `134 + 124 + 228` source bytes; exact-root Linux emits the same
sizes with independently pinned linked hashes. This closure unlocks the ISR
half of CMSIS `osMessageQueuePut`. No image was signed or flashed.
