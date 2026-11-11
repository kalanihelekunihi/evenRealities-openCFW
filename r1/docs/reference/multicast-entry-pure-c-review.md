# R1 multicast dispatcher entry in C

The dispatcher at `0x8b028` now enters ordinary C directly. The previous wrapper only shifted saved input registers into caller-scratch R1/R2/R3 on return. Eight direct transfers were identified, including two tail calls; no identified continuing caller uses those restored values. Indirect and nonstandard external consumers remain outside that proof. The separate opaque callback trampoline and its executable section are unchanged.

REA matches the locked 202-byte stock function. All 202 instruction bytes execute across 6,997 paired comparisons. These cover selector wrapping, nullable roots, short caching, allocation failure, synchronous callbacks, once-per-route publication, live structure mutations and overlapping copies. Another 192 pipeline comparisons execute the actual publisher, enqueue and consumer through successful and failed queues. Six compiled defects are rejected. Providers return through executable BX LR stubs; caller guards, saved integer/FP registers, SP and masks are checked.

The normal build compiles 862 units with 63 application and 22 bootloader imports and no failures or duplicate strong symbols. The other 851 prior nongenerated objects are identical. The final whitespace cleanup produces the same dispatcher object as the tested build. Manifest, source plan and persistent state are unchanged; R1 source checking passes.

Allocator, CMSIS mutex/queue/flags APIs and opaque callbacks are modeled. The publisher still has its separate frame bridge. Caller scratch, private stack placement, uninitialized leading queue word and internal memory-move access widths/order are excluded. Native null-root-after-lock faults remain compared. Physical scheduling, queued-object lifetime, final linking and device boot remain unverified.

See the [machine-readable receipt](multicast-entry-pure-c-review.json) for hashes. Probes and direct-caller scan are under `build/goal-r1-multicast-entry-c/`.
