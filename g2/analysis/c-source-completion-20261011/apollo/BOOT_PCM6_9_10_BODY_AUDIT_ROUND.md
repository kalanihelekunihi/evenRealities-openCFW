# Boot PCM22 selector 6, 9 and 10 body audit

Native selectors 6 (`0x428840`), 9 (`0x428ca4`) and 10 (`0x428d90`)
each read the current profile byte and word, although the retained
pseudocode drops those unused extracted values. Direct Thumb loads occur
at `0x428886/0x42888c`, `0x428cec/0x428cf2`, and
`0x428dd8/0x428dde`, respectively. Selected C retains those volatile
reads. All three selected bodies also preserve the timer branch, target
state stores and TON child call. Selectors 6 and 9 perform VDDF MMIO RMW
before TON; selector 10 does not. The corresponding complete body bindings
are in `manual_body_bindings.json`.

No selected source changed in this round. The current coherent target
receipt remains `boot-coplacement-ton-readorder-round/receipt.json`:
`PASS_BOUNDED_LINK`, 373 selected units, 1,010 providers, three ROM imports,
34 callback relocations. The regenerated rooted header-only proof queue is
**161/654**, down from 164; the whole-catalogue queue is **259/903**. These
are attribution leads, not missing C body counts. ROM, indirect roots,
complete data/layout and runtime qualification remain open.
