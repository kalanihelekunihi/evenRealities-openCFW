# IRQ nesting at wrapper boundaries

Expanded IRQ frame qualification from callback-only nesting to all13 decoded
wrapper instruction boundaries.234 cases (six seeds, nesting depths1..3) pass
with shared stack memory and inherited interrupted register values. The model
now asserts complete architectural register restoration and rejects unreachable
injection points. All17 IRQ tests pass, including four new boundary tests;
the original24-case software and24-case architecture checks still pass.

This is conditional frame evidence, not IRQ admission. The conservative model
injects regardless of actual PSR eligibility and does not establish exception
acceptance timing, instruction atomicity, callback stack bounds or physical
stack capacity. No firmware bytes or package changed; the121-function verified
macOS package remains current. Continue with interrupt timing/stack composition
or remaining source reconstruction; the full source-only goal stays active.
