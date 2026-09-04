# G2 legal/regulatory UI recovery

`legal_regulatory.c` closes as one 234-byte event handler plus a 194-byte
content/literal pool, for 428 physical bytes at `[0x005BF7B8,0x005BF964)`.
The next function is the already audited EasyLogger async-sink callback, not
part of this object. Two stored references and one direct call enter compiler-
shared diagnostic tails at `0x005BF880`/`0x005BF88C`; these multi-entry tails
are explicitly pinned rather than misclassified as separate functions.

The handler owns the complete regional legal-string table and startup,
scroll, and exit dispatch. Its 15 calls resolve to ten admitted EasyLogger,
one admitted LVGL scroll primitive at selected commit `344c7c3…`, two bounded
IAR memory primitives, and two first-party page/animation providers. No opaque
third-party body or new version discriminator remains.

The event handler is now production-routed to
`components/apollo_main/core_overlay/legal_regulatory.c`. The clean-room C
implementation preserves event 2 page construction, the active-root write to
the recovered animation slot at `0x200014D0`, the 250-unit entry animation,
and event 3/action 1 signed animated scrolling through the active root at
`0x200746A4`. Events 4, 5, unknown events, non-scroll actions, and null scroll
payloads return zero without a functional side effect; stock diagnostic output
is deliberately omitted.

Independent Apple and Linux canonical pairs reproduce one 78-byte leaf with
three strict call relocations. The final fixed-size component routes the full
234-byte stock handler entry to that leaf, while the 194-byte content/literal
pool remains retained. The analyzer authenticates the source/header, compiler
receipts, both final components, effective relocated text, semantic manifest,
package, and zero-unresolved flash plan. Host tests cover startup, signed
scrolling, no-op event policy, null input, and freestanding Cortex-M55 compile.

The software gap for this handler is closed. On-device qualification remains
**blocked by unavailable physical evidence**: an authorized G2 display/input
trace is required to prove legal-page creation, 250-unit animation, signed
animated scrolling, retained regional content rendering, and exit behavior.
No hardware operation was performed.
