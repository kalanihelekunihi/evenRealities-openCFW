# Queue-buffer release / inherited-priority source evidence

Reference: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, base `0x410000`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

| Stock entry | Range | Size | SHA-256 | Candidate |
|---|---|---:|---|---|
| `0x418c1e` | `[0x418c1e,0x418cc2)` | 164 B | `fe2434d8fb55b1ad847fc00d8feca98c8133fb2b473a4860b3d6d03c0eebf890` | `queue_buffer_release.c`: `opencfw_boot_queue_buffer_release` |

The ABI is `uint32_t opencfw_boot_queue_buffer_release(uint32_t *current_thread)`. Null returns 0 without state changes. A nonnull pointer that differs from `*(uint32_t *)0x20027134`, or a zero reference count at TCB `+0x64`, takes the mask-interrupts / invalid-store / loop fatal path. Otherwise the helper decrements the count. It returns 0 without moving the task if effective priority at `+0x2c` already equals base priority at `+0x60`, or if references remain. Only the final inherited-priority release returns 1: it unlinks the ready node at `TCB+4`, restores effective priority from base, writes `56 - base_priority` at TCB `+0x18`, raises global ready-highest `0x2002714c` if necessary, and inserts the task in the ready list at `0x20024870 + 20*base_priority`.

`verify_queue_buffer_release.py` compares seven original/source fixtures over 160 distinct instruction bytes in the helper body. It covers null/no mutation, same priority, a remaining inherited reference, final restoration when the global highest priority is already higher or must be raised, and both fatal guards. The linked-list unlink is an explicit synthetic callback at stock `0x41b5a8` for the isolated comparison; the parent integration can link the separately recovered `opencfw_boot_list_unlink` implementation. TCB/list/global RAM is synthetic. The fixture does not model mutex acquisition or actual task preemption.

Run `make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/queue-buffer-release verify` with Unicorn JIT enabled. No device is accessed and no byte-identity claim is made.
