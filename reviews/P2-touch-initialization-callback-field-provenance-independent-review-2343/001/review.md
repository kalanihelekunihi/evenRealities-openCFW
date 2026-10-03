# Independent review 2343

**Result:** PASS_SCOPED.

Receipt 97f3038e891a471fd9c2451f8429255ff6867860de541356f72b99db4fc82f1d and all artifact pins match the source hash. The independently run verifier returns PASS; the literal and addressed instruction operands reproduce exactly.

The literal at 0x7284 is 0x00006781. At 0x721A the coordinator stores it at [r3,#0x10] after loading cfg from ctx.word8; at 0x722A it freshly loads [cfg,#0x14], and 0x7232 performs BLX R3 with ctx in R0. Thus these are distinct word offsets (16 versus 20) along the decoded ordinary-pointer path; the installed word16 is not itself the target loaded by that BLX.

The pinned 6780 source pseudocode and independent review hash match the referenced files. Evidence is scoped to the distinction of these fields and the decoded entry, not resolution of the dynamic target.

**Limits:** No dynamic target closure, writer/provenance of cfg.word20, or runtime consumer of word16 is established. Aliasing/mutation could change field relationships; physical interrupt/status behavior remains unresolved. No new executable ownership, caller closure, or canonical admission is claimed; accepted:false.
