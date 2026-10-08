# Actual RTOS-free dependency closure

This test closes the allocator cut left by the 260-case `runtime-action-416200`
comparison. That proof covers the release-storage ownership decision and the
ordered free arguments, but records `0x419830` as a controlled call boundary.
Separately, `g2/components/bootloader/thread_creation/verify_heap.py` already
executes the stock allocator/free instructions against the native
`rtos_heap.c` implementation over a valid 81,920-byte synthetic arena. This
worker combines those source and stock pieces in one small fixture.

## Fixture and result

The test independently initializes the heap at `0x2000055c` and performs any
needed stock/native allocations before creating each TCB record. It verifies
the allocation header's high bit for every block that the release function
will free. It does not borrow TCB/stack pointers or allocator snapshots from
an earlier case.

| TCB byte `+0x6d` | Heap-backed pointers | Release action | Result |
|---:|---|---|---|
| 0 | stack `0x20000568`, TCB `0x20000678` | frees stack, then TCB | two allocator frees; all 81,920 arena bytes match stock/source and full free extent returns to `0x13ff0` |
| 1 | TCB `0x20000568`; stack is external static storage `0x20018000` | frees TCB only | one allocator free; complete arena and allocator globals match |
| 2 | external static TCB `0x20018200` and stack `0x20018000` | frees neither | zero allocator frees; allocator globals and arena match |

For each row, stock executes `0x418ae8` and the actual `0x419830` body; source
executes `opencfw_boot_thread_release_storage` and compiled native
`opencfw_bl_rtos_free`. Heap setup and allocation also execute the original
`0x4198a0`/`0x419730` bodies and compiled source counterparts. The full arena,
allocator metadata/globals, relevant TCB/stack bytes, ordered suspend/resume
events and allocation/free counters compare equal. The receipt
`comparison.json` includes per-function original hashes, instruction coverage,
ELF and source input hashes, and every final arena image.

## Limits

The three tested ownership values correspond to 0 = dynamically allocated
stack and TCB, 1 = dynamically allocated TCB with static stack, and 2 = static
stack and TCB. This does not cover malformed flag values, invalid/double free,
allocation exhaustion, concurrent frees, real scheduler exclusion, full
task-delete scheduling or deferred reclamation, hardware behavior, or exact
firmware byte identity. Scheduler suspend/resume are no-op providers and all
heap memory is deterministic Unicorn RAM.
