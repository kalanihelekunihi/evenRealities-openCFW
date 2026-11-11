# R1 event publisher native-frame fidelity

The publisher at `0x8d8fc` now passes an explicit native frame into its C
control body. The previous automatic C record left its first word
uninitialized. Stock instead passes through the existing word at caller
`SP-44`, within its 48-byte frame. Replacing this with zero would change the
queue record. The new 18-byte entry bridge preserves that frame and supplies
its bytes to C without an indeterminate automatic object.

REA observes the contiguous 202-byte stock body through `0x8d9c5`. Evidence
is bound to locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The queue record starts four bytes into the 24 local bytes, with ID, length
and payload words at frame offsets 8, 12 and 16. Allocation-failure logging
also writes its fifth argument at frame offset zero. Existing bytes and
queue mutations remain visible, including a changed pointer subsequently
released after a failed enqueue. Copies use the existing native memory-move
adapter, matching the stock entry rather than assuming an ISO memcpy call.

[Machine-readable evidence](event-publisher-frame-review.json) records:

- 2,886 paired stock/C direct-entry cases check all 16 queue-record bytes and
  the entire 48-byte native frame after return. Cases cover ID boundaries,
  short and allocated payloads, partial context availability, queue failures,
  stack-field payload aliases, changing log gates, and queue mutations of the
  leading word, thread, payload pointer and length. SP, saved registers,
  masks, heap and payload bytes agree.
- Zeroing the leading word and selecting the wrong record offset are each
  rejected by the comparison harness.
- 192 paired multicast-to-publisher-to-consumer cases pass again with the
  changed publisher. These execute the real C dispatch, publish, enqueue,
  consumer, mutex wrappers, thread/task getters and movement providers.
- All other 574 object hashes, the standalone enqueue body and relocations,
  three context data owners, manifest and composed import sets are unchanged.
  All 575 R1 units compile; imports remain 175 application and 34 bootloader,
  with no failures or duplicate strong symbols. `make sources-check` passes.

All five qualification variants compile, with no exact region selected.
The canonical plan remains unchanged: 3,881 source-built application bytes,
642,279 binary pull-through bytes and 248 resource bytes. The fresh hybrid
application equals stock; source completeness remains false.

The direct-entry probe supplies identical caller-relative frame bytes. It
does not reconstruct every caller's prior stack history. The integration
probe continues to exclude the leading queue word because the upstream C
multicast caller's private frame is not stock-identical. Allocator, queue,
flags, release and logging effects are modeled; physical hardware, actual
scheduling, helper-private frames and MMIO copy semantics are unproven.
Complete source linking and full source byte equality remain outstanding.
G2 workflow gates were not advanced. The goal remains active.
