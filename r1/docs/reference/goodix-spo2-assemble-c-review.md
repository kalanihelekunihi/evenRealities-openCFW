# SpO2 channel assembly and parity in C

The [batch-accumulation review](goodix-spo2-batch-c-review.md) adds actual C window accumulation and averaging, with two-window lifecycles and the real frame pipeline. Incomplete-window status3 is preserved. Twelve later processing stages remain unfinished.

The [numeric-decoder review](goodix-spo2-decode-c-review.md) adds actual C decoding and nominal TIA gain state. Real frame/core/assembler/decoder replays agree with stock; fixed power calls become verified exact constants. Thirteen later processing stages remain unfinished.

`native_spo2_assemble.c` implements the334-byte channel assembler,20-byte integrity check and54-byte encoder. It reuses the canonical C version qualifier and adds no persistent state.

The assembler performs byte-wise integrity checks before packed-bit channel selection. Sentinel writes affect later enable-prefix reads through the live PPG alias. It preserves sequence wrap, metadata order, three-group output offsets, live capacity/buffer reloads and byte-sized record-count wrap. The parity encoder replaces only bit0 and preserves the entire remaining31 bits.

**10,559 stock-versus-C comparisons pass**:

- 8,712 direct cases cover the assembler and both parity helpers with independent popcount/packing oracles, disjoint/aliased buffers,255 channels, wrapped counters and callback mutations.
- 1,847 integrated cases execute the actual native/C core, assembler, integrity helpers, qualifier and polynomial. Numeric decoding, later stages and allocator/clear ports remain modeled.
- Both fixtures execute all408 new native instruction bytes; integration also covers all682 core bytes. Full active FPSCR, saved registers, stack, masks and final public RAM bytes agree. Boundary RAM uses hashes directly and byte snapshots in integration. Twelve compiled defects are rejected; source cannot execute stock.

All **902 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;891 prior nongenerated source/object pairs and source-plan/cache files are unchanged. The assembler import becomes unfinished `r1_goodix_spo2_decode`, leaving91 application/22 bootloader imports.

This does not complete numeric decoding, inference, physical sampling or bootable firmware. Arbitrary private aliases, input faults and physical interrupt timing remain unverified.

[Machine-readable evidence](goodix-spo2-assemble-c-review.json) records exact contracts, addresses, fixtures and hashes.
