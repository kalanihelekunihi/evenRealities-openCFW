# CMSIS-FreeRTOS thread-termination source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

`osThreadTerminate` and its complete FreeRTOS task-state/deletion dependency
chain are production source-owned. The three kernel bodies are bounded
adaptations of FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` under MIT. The wrapper is a
bounded adaptation of CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `osThreadTerminate` | `[0x004491FE,0x00449238)` | 58 | `d89f27dd18cbf97e9e82e793f812b6354b85d56f125220edb8cec9ae6993adc2` |
| `vTaskDelete` | `[0x00454AAE,0x00454B4C)` | 158 | `fed4eb28935bf7034f3f1893518e7de056995a5083d42863ab007e9e74de2597` |
| `eTaskGetState` | `[0x00454B88,0x00454C12)` | 138 | `e4781094cbfded3f125a131f0d793cc67b47af6db0f879036d0ca6afc1056bfc` |
| `prvDeleteTCB` | `[0x00455836,0x00455876)` | 64 | `86f7fc5725fe0fbbe85c07f68669981bad154cd58163427a6ead8106538e2a12` |

The recovered G2 configuration uses one task notification, dynamic and static
allocation, task deletion, task suspension, and the 112-byte vendor TCB. The
adapters preserve state classification across current, ready, delayed,
overflow-delayed, suspended, notification-wait, termination, and detached
tasks. Deletion preserves state/event removal, task-number updates,
non-current immediate cleanup, current-task cleanup deferral, termination-list
insertion, next-unblock reset, scheduler assertions, and rescheduling. Private
cleanup preserves allocation-status values 0/1/2 and stack/TCB free policy at
TCB offsets `+0x30` and `+0x6D`.

All fixed calls bind to separately source-owned critical-section, list,
heap_4, unblock-time, yield, and IRQ providers. Hosted tests exercise every
state class, all allocation modes, current/non-current deletion, the suspended
scheduler assertion, and CMSIS ISR/parameter/resource/success returns.

Apple Clang 21 emits 142/58/152/52-byte leaves at offsets
`135656/135800/135860/136012`. Homebrew Clang 22.1.8 emits the same sizes at
`137536/137680/137740/137892`. The canonical Apple component/package are
`3659460` / `8e967533d693ddfc2b9cc99af198a16c69d1c5464dc66e4aa92f93698ec46108`
and `4437954` / `b88c871be7ff8cbeba54cf56c5e5d82f4c8a46e5840ec0fc0730b854f3c29f5b`.
The exact-root Linux component/package are
`3661340` / `a8cb1c45e88956d6048860feb14931e263c5973a4c178b8182d00c9ecd3a7b5b`
and `4439834` / `fa866c7ec9f3c88571bbbad26753f4a29d7601668e4952adb3e09467f057ec86`.

This is the 33rd of 38 linked public CMSIS APIs. The remaining five are
`osKernelInitialize`, `osKernelStart`, `osThreadNew`, `osThreadFlagsSet`, and
`osThreadFlagsWait`. No image was signed or flashed.
