# Queue deletion ownership in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`vQueueDelete`. REA confirms stock entry `0x95f70` (30 bytes): validate the queue,
read ownership byte at offset 70, tail-call free only for zero, and return for
all nonzero values. Null arguments retain the logical assertion fault. The
existing queue-provider configuration omits the registry-unregister route,
matching stock.

Verification:

- 2,052 paired native/C leaf cases cover every ownership byte, four masks,
  callback mutations and null arguments. The modeled free boundary receives the
  descriptor with original SP/LR, proving the tail call in the tested C build.
  Static descriptors are not freed; free-boundary changes to descriptor/mask are
  retained. Guards, state, preserved registers and masks agree.
- 8,248 creation/deletion lifecycle cases execute actual static/dynamic creation,
  initialization, reset, lists and deletion. Heap allocation/free and critical
  boundaries are modeled. Valid dynamic objects reach free; static objects do
  not; allocation failures do not invoke deletion on null.
- 216 additional seeded-heap cases explicitly link the native heap candidate and
  execute actual queue deletion, native/C vPortFree and free-list insertion.
  Sizes, left/right coalescing, end-sentinel adjacency, static flags and masks
  agree. Heap state, free counts, list metadata and payload bytes match stock;
  only scheduler suspend/resume are modeled.
- Negative controls reject freeing static objects, skipping dynamic free and
  reading the queue-type byte instead of the ownership byte. All twenty-four
  preexisting function bodies remain byte-unchanged.

The heap probe is deliberately an explicit candidate selection: normal
composition still selects upstream `portable/MemMang/heap_4.c`, while
`r1/src/application/board/native_heap.c` remains excluded. Seeded valid free-list
comparisons do not validate native malloc, cold initialization, corrupted
metadata or the complete allocator binding. Full native malloc/free validation
remains before changing that normal provider selection.

All 573 R1 units compile and compose without failures or duplicate strong symbols.
Application imports fall from 188 to 187, removing only `vQueueDelete`;
bootloader imports remain 34. `make sources-check` and `git diff --check` pass.
Five official qualifier configurations compiled; only two already-covered
BASEPRI copies matched. Recorded C deletion size is 34 bytes versus stock 30,
and remains unqualified.

The unchanged canonical plan builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Private frames and void-return caller-clobbered words/flags are excluded.
Assertions cover mask, fault address, width and value without full exception
state. Heap corruption, double-free, use-after-free and physical concurrency
remain unverified. No G2 gate advances. Source, REA, probe, qualifier and build
hashes are bound in `queue-delete-c-dependency-review.json`.
