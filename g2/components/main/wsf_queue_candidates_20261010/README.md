# WSF message dequeue and critical section candidate

`wsf_queue.c` source-defines WsfCsEnter 0x52b8a4..0x52b8b6, WsfCsExit 0x52b8b6..0x52b8c8, WsfQueueDeq 0x538c4a..0x538c6e, WsfMsgDeq 0x4bf9ec..0x4bfa00, and WsfMsgFree 0x4bf9b0..0x4bf9ba. The SMP callback names match `g2_smp_providers` signatures. The critical functions use the stock WSF nesting byte at 0x20075045 and explicit ARM `cpsid i` / `cpsie i`; they are distinct from FreeRTOS critical functions. The queue is two 32-bit head/tail words. Message headers carry next at +0 and handler ID at +4; payload begins at +8.

The message-free wrapper passes hidden header address (message minus eight) through `g2_wsf_free_provider.buffer_free`. This lowest WsfBufFree provider is deliberately supplied by the integrator; source in this directory does not recycle pool memory. The SMP handler's shared context must be adapted to provide that callback without changing its other provider contracts. The callback is not a working allocator stub.

See `g2/analysis/wsf-queue-candidate-20261010/REPORT.md` for exact original/source comparisons and remaining ownership boundaries.
