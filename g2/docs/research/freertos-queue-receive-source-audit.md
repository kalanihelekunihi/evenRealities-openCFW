# FreeRTOS task-context queue-receive source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

The complete task-context receive dependency chain is production source-owned
from FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` under MIT.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `xQueueReceive` | `[0x00441B0A,0x00441C44)` | 314 | `f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560` |
| `prvUnlockQueue` | `[0x00441F88,0x00441FF6)` | 110 | `25eb09eeb3f819a998a8d56ebac062fb54fcc5140af8445c5d39c514187b9f7d` |
| `vTaskPlaceOnEventList` | `[0x00455282,0x004552AE)` | 44 | `2821a3c55358d806ed227c81a27746f8d9c35b648182fc9abb647de72ed9025d` |
| `prvAddCurrentTaskToDelayedList` | `[0x00455FA8,0x0045601E)` | 118 | `918fddb6333958607bec10181d39ffee564ca44f4db6cb43ee362cc62ba4f764` |

The closure preserves immediate receive and sender wake, empty/nonblocking
failure, timeout initialization and recheck, scheduler suspension, queue lock
and unlock accounting, finite/overflow/indefinite delayed-list placement,
next-unblock-time maintenance, missed-yield propagation, and post-resume yield.
All fixed calls resolve to existing source-owned queue, list, scheduler,
critical-section, timeout, and yield providers. Recovered RAM seams are
`pxCurrentTCB=0x20074A20`, delayed/overflow list pointers at `0x20074A24/28`,
`xTickCount=0x20074A34`, suspended list `0x20073D4C`, and
`xNextTaskUnblockTime=0x20074A50`.

Selector-isolated strict builds emit Apple leaves of `126`, `54`, `116`, and
`432` bytes at overlay offsets `134428`, `134556`, `134612`, and `134728`.
Linux emits the same sizes at `136304`, `136432`, `136488`, and `136604`.
Hosted tests exercise all three delayed-list routes plus immediate, empty, and
timeout receive paths. No image was signed or flashed.
