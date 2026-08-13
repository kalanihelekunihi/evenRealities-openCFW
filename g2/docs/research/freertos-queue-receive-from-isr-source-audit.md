# FreeRTOS ISR queue-receive source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

The complete retained read-side ISR queue closure is production source-owned.
The source baseline is FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`; the adapted upstream unit is
`queue.c` under the MIT license. CMSIS `xSemaphoreTakeFromISR` is a macro alias
of `xQueueReceiveFromISR`, so this one provider closes both the queue-receive
and ISR semaphore-take dependency without creating a fictitious second
function.

| Stock function | Stock span | Bytes | SHA-256 |
|---|---:|---:|---|
| `xQueueReceiveFromISR` | `[0x00441DA6,0x00441E66)` | 192 | `cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4` |
| `prvCopyDataFromQueue` | `[0x00441F5E,0x00441F88)` | 42 | `d788663fd093a939ebf3f23edb08bf534bda42f1c31a181b9e7f20347db229cc` |

The public stock entry has three relevant CMSIS callers: `osSemaphoreAcquire`
at `0x0044997C`, `osMessageQueueGet` at `0x00449B6A`, and
`osMemoryPoolAlloc` at `0x00449D6A`. This immediately unlocked the first and
third wrappers and removed one major blocker from the second.

## Recovered behavior and dependency boundary

The adapters preserve queue-null and buffer assertions, interrupt masking,
message decrement, read-pointer advance and wrap, semaphore/null-buffer mode,
receive-lock saturation against task count, optional waiter removal and wake,
trace hooks, and failure tracing. The private copy helper retains only the
standard memory-copy seam. The ISR provider calls the separately source-owned
event-list removal leaf and the new private copy leaf; no unidentified fixed
callee remains.

Seven focused tests pin source/fixture hashes, both stock spans, unrelocated
target bytes and relocations, data/semaphore paths, lock saturation, waiter
wake behavior, assertions, and canonical Apple/Linux placement.

## Reproducible artifacts

| Profile | Copy leaf | Receive leaf | Overlay | Component | Package |
|---|---:|---:|---:|---:|---:|
| Apple Clang 21 | 34 B at `133048` | 208 B at `133084` | `133794` | `3657190` | `4435684` |
| Linux Clang 22.1.8 | 32 B at `134924` | 208 B at `134956` | `135670` | `3659066` | `4437560` |

The final package SHAs are
`57023a757db5c037fe1c0a63cf8ace615c1dc32a5f4152893e0db00cbe7ae185`
and `7504a643f6acbcfb8fd41742aa22eaa95f31888c1626e526995cacf4fd760981`
for Apple and Linux respectively. No image was signed or flashed.

## Next shortcut

`osMessageQueueGet` still has a task-side dependency on `xQueueReceive` and
its event-list/unlock closure. The newly source-owned ISR half means future
work can isolate that task-side seam rather than re-auditing the whole CMSIS
wrapper.
