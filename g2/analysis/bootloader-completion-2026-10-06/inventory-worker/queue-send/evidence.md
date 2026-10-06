# Queue-put source evidence

Reference firmware: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, load base `0x410000`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

| Stock entry | Range | Size | SHA-256 | Source |
|---|---|---:|---|---|
| `0x419ec0` | `[0x419ec0,0x41a024)` | 356 B | `733caba72cd14778822c37369f845e24980cb22b00050fce331c12a7c9fefd70` | `queue_send.c`: `opencfw_bl_kernel_queue_put_blocking` |
| `0x41a4a6` | `[0x41a4a6,0x41a52c)` | 134 B | `193bc93f695639e0b92e3f1f5f12bf14234b8424aa3273bab02d143cfa43097f` | `queue_send.c`: `opencfw_boot_queue_copy_in` |

The function ABI is four ARM32 arguments: `(queue, message, raw_timeout, mode)`. Queue control words used here are count `+0x38`, capacity `+0x3c`, item size `+0x40`, event-waiter anchor `+0x24`, send-wait list `+0x10`, wait-lock bytes `+0x44/+0x45`; the ring cursors are at `+4`, `+8`, `+0xc`, and base at `+0`. Null queue is fatal. A null message is fatal only for nonzero item size. Mode 2 is admitted only when capacity is exactly 1; modes 0 and 1 accept other capacities. Runtime mode zero with nonzero timeout is fatal.

The first protected check accepts a put when `count < capacity`, or whenever mode is 2. Otherwise timeout zero returns 0. Positive timeout captures the queue timeout state, exits the kernel critical section, suspends the scheduler, initializes unset per-queue lock bytes, checks timeout, and either returns 0 on expiry or adds the current task to the sorted send-wait list. After unlock/resume it retries the protected count test. Successful insertion calls the copy helper, wakes one event waiter at `queue+0x24` if present, reschedules if a waiter was removed, and returns 1.

`0x41a4a6` copies exactly the queue item size. Mode zero copies at the current `+4` cursor then advances it, wrapping to base when it reaches or passes `+8`. Nonzero modes copy at `+0xc`, decrement that cursor, and wrap to `end - item_size`. Mode 2 decrements a nonzero count before the common increment, replacing one slot without changing a full single-entry queue's count. For zero-size items with zero base, the stock helper calls `0x418c1e` on `queue[2]` and clears that word; this special queue-buffer release path remains an explicit lower provider because manager DFU messages have nonzero item size.

The standalone verifier compares 16 fixtures against original instructions. It executes original copy helper `0x41a4a6` and its stock copy routine `0x41568c`; source executes the readable byte-copy loop. It covers append/wrap, front cursor/wrap, mode-2 single-slot replacement, capacity-50 modes 0 and 1, full nonblocking failure, finite timeout expiry, the blocking/list/reschedule boundary, event-waiter wake, and fatal argument/guard paths. Queue wait-list insertion, timeout arithmetic, timer-lock teardown, scheduler/critical-section calls, runtime mode, and event waiter removal are intercepted at exact stock addresses as declared providers; therefore these tests verify call order and queue RAM effects, not autonomous task scheduling or clock rate.

Run `make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/queue-send verify`. The harness uses only local firmware instructions and synthetic queue RAM. It does not access hardware or claim byte-identical build output.
