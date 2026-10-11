# WSF fixed-pool free candidate

`buffer_free.c` source-defines the full bounded WsfBufFree body at 0x5304d4..0x530512. It reads the stock table-pointer cell 0x20074eec and pool-count byte 0x20075044, walks 12-byte pool descriptors from highest index down, and selects the first pool whose start is at or below the block pointer. For a selected pool it brackets writes with the source-defined WSF critical helpers, writes marker 0xfaabd00d at block+4, sets block->next to the old free head, and makes the block the new free head. A pointer below every pool start leaves state unchanged. `g2_smp_candidate_buffer_free` fits SmpHandler's direct callback signature; `g2_wsf_candidate_buffer_free_word` fits the message-free provider's one-word callback.

The stock routine checks only the selected pool's lower bound. It does not validate upper bounds, alignment, allocation status or double frees. This source preserves that behavior for comparison; it is not a safe general allocator. Source-defined pool allocation, initialized stock table state, concurrency, lifetime and ownership are outside this candidate.

The source links with `g2/components/main/wsf_queue_candidates_20261010/wsf_queue.c` for the actual WSF CPSID/CPSIE nesting helpers. See `g2/analysis/wsf-buffer-candidate-20261010/REPORT.md` for original-byte comparison and limits.
