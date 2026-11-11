# R1 software-TWI leaf delay dependency closure

The return-only callback and distinct five-NOP callback now participate in
normal composition. The timing-sensitive busy countdown moved to a separate
excluded unit. All three compiled function bodies are unchanged by the split,
and only one source implementation of each function remains. Application
imports fall from 235 to 233, resolving `r1_twi_delay_noop` and
`r1_twi_i2c5_delay_noop`; `r1_twi_delay_busy` remains explicit. No imports or
duplicate strong symbols were added.

The complete leaf bodies match stock exactly: `0x7081C` is the two-byte
`bx lr`, while `0x54AF0` is five NOPs followed by return (12 bytes). All 912
M-class comparisons pass across 114 arguments, four APSR flag patterns and
both functions. Observed r0–r12/SP/LR and flags remain unchanged, there are
no data-memory accesses, and instruction counts are one and six respectively.
These are compiled-body observations, not additional promises of the void C
API. The existing REA leaf review and its unchanged snapshot hash are bound
again; empty decompiler pseudocode alone does not distinguish these bodies.

Leaf instruction identity does not establish calibrated SCL/SDA timing or a
complete software-TWI transaction. The busy implementation retains its
volatile stack countdown and remains excluded because it has not established
stock cycle timing. No timing assumption is relaxed to resolve its import.

The additional split unit brings R1 to 562 compiled units (488 application,
74 bootloader). Both compositions pass, with 233 application and 34
bootloader imports. `make sources-check` passes for both trees. No source-plan
selection, source qualification or workflow gate changed; whole-image byte
identity remains open.

[twi-leaf-closure-review.json](twi-leaf-closure-review.json) binds before/after
source/manifest/build hashes, unchanged busy-body bytes, stock-identical
leaves, prior REA evidence and ignored probes under
`build/goal-r1-twi-leaf-closure/`.
