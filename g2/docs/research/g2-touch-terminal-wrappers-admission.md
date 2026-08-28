# G2 touch terminal wrapper admission (batch 20)

Batch 20 admits the final evidence-closed wrapper family: `0x1368`, `0x25F8`,
`0x2972`, and `0x297A`, totaling 72 shipped instruction bytes. The MIT source
preserves the effect-free passthrough, exact `0xFFFFFBFF` state mask, descending
object reset order `2,1,0`, and conditional `(0,5,value)` provider call.

The reset dependency is already admitted MIT source. The `0x38D4` CapSense body
remains an injected, fail-closed Infineon EULA provider; it is neither copied nor
executed in host tests. Canonical bodies, direct calls, host behavior, and
Cortex-M0+ symbol closure are pinned. No resident table, MMIO, hardware action,
or production route is admitted.

The concrete source/implementation gap falls from 47 functions / 4,550 bytes
to 43 / 4,478 bytes; application contracts fall from 35 to 31 and the twelve
existing external/unavailable functions remain. This is the terminal source
admission before exhaustive whole-payload frontier classification. Hardware
validation remains blocked by unavailable physical evidence.
