# Independent review 2345

**Result:** REVISE_PROSE.

Receipt 7d271051cbfd207820e1182ab2de7269088ed055868ecd05db81ad88c5e299ad and source hash match; the pinned body is [0x4C7C,0x4CBE), and all candidate artifact hashes recompute. Isolated replay passes all 12 original-instruction cases.

The prefix caches cfg from ctx+8, clears bytes116/117 and words0/4/12/8, ORs 6 into byte35 of each of three 60-byte parameter records, clears cfg.word28, and at 0x4CBC stores R2=0 to cfg.word20. All tested preexisting callback values become zero and each parameter flag is updated as asserted.

Correction required: LDR at 0x4CB6 is [PC,#0xF0]. Thumb PC alignment yields literal address 0x4DA8, whose source word is 0x0000028F. The prose instead names 0x4DAC. The replay write ledger shows cfg+44 receives 655 (0x28F), confirming the decoded literal value. The stored value is therefore pinned, but the stated literal location is wrong.

**Limits:** Execution intentionally stops at 0x4CBE; later initializer writes and persistence are not covered. This demonstrates a writer to cfg.word20 but not that it remains zero before the coordinator's later dynamic call; caller closure, aliasing and dynamic-target resolution remain open. No physical behavior or canonical admission is claimed; accepted:false. The report recommends a prose-only correction in a new candidate packet, preserving this frozen one.
