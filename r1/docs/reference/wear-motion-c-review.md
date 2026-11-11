# R1 wear motion coordinator in C

`native_wear_motion.c` supplies motion callback `0x3cd80` and boolean-normalization
helper `0x96a40` as ordinary C. The [review receipt](wear-motion-c-review.json)
binds REA stock bytes, production hashes, differential checks and qualification.

Null payload returns before reading its count. The halfword at offset 180 must
be at least ten; context and supplied length are ignored. The initial mode is
normalized to zero/one before applying module state. Module zero forces mode zero,
module one forces mode two, and other module values consult sleep gate exactly one
to force zero. Otherwise the callback clears a 24-byte statistics argument, invokes
statistics, freshly reads mode to select on/off decision, and invokes that decision.

It then freshly normalizes mode and publishes group 4, length 1 only when the
boolean differs from the initial boolean. Changes between nonzero mode values do
not themselves publish. After multicast, fresh sleep status exactly one and fresh
mode exactly two set the existing latch to one. Other cases leave the latch alone.
The module's callback declaration now uses the established three-word stream ABI;
its object is unchanged. No new RAM ownership is introduced.

The fixture passes 3,352 paired stock/C cases with module/mode/gate boundaries,
null/unaligned packets, halfword count thresholds and high-byte cases, ignored
length, provider mutations between statistics/decision/multicast, boolean helper
full-word inputs and interrupt masks. An initial byte-count defect escaped the
first matrix; adding counts 256/265/266 rejects that defect without changing C.
Seven compiled defects are rejected: byte count, wrong minimum, boolean sleep gate,
raw-mode event comparison, missing multicast, wrong latch mode and stale decision
mode. It compares public state, provider arguments and boolean helper R0, and
checks preserved registers/SP/masks/FPSCR. Both native and C observed provider
frames are 48 bytes. Void callback R0, caller-clobbered registers, APSR and private
stack residue are excluded. Providers remain modeled, and statistics access is
bounded to the explicitly cleared 24-byte argument; broader frame behavior is
not established. Physical/concurrent behavior remains unverified.

All 645 units compile and both relocatable compositions pass without duplicate
strong symbols. All 644 earlier objects are unchanged. The motion callback import
is resolved while statistics, on-decision and off-decision are exposed, leaving
application/bootloader imports at 174/34. Manifest validation passes. Neither body
qualifies as exact. The plan stays at 4,345 source-built bytes. A fresh hybrid
matches the locked application with 641,815 executable pull-through and 248 resource
bytes. Complete source-only linking and byte identity from C remain unfinished.
