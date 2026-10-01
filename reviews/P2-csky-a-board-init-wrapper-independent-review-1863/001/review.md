# Independent review 1863 — C-SKY A board-init wrapper

**Result: PASS_SCOPED.** Review 1863 is bound to candidate `csky-a-board-init-wrapper-1852/001`, receipt SHA-256 `e38580ab243c127f6358876bad4a7414846db8b31a5768bdf60d26af7d31e76d`. Candidate verifier passed, including artifact/source pins and installed-tool disassembly replay.

The SRAM body is the exact 20-byte span `[0x28BC,0x28D0)` at conditional runtime coordinates `[0x10025CBC,0x10025CD0)`. The seven decoded instructions agree with the pseudocode. The status call overwrites incoming R0; unsigned `cmphsi r0, 2` followed by `bf` skips the optional helper for 0/1 and calls it for 2 and above. The pinned decoder evidence bounds its modeled result to 0–5.

The XIP base and fetch are conditional. The two authenticated bytes at child `[0x3C74,0x3C76)` decode to `pop r15`; the candidate only describes the possible stack/return consequence if that fragment is fetched. It does not claim live mapping, execution, or ownership outside those two bytes.

Helper `0x100245F0`, hardware/MMIO meaning, physical XIP behavior, and complete image coverage remain unresolved. No canonical admission is made.
