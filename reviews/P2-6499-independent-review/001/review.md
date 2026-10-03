# Independent review 6499

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and FF84..FFF2 source span match the locked image. GNU Thumb decoding confirms that modes 6, 7, and 9 enter the shared mask path: save PRIMASK through 41B8EC into `[SP]`, then for second-argument byte 1 OR `1 << mode` into the word at the common literal address, for byte 0 clear that bit, and for other values skip the write. A fresh load of that word is reduced to a boolean for child 4303BC with R0=134; the child result is ignored, and the saved PRIMASK is restored before the shared branch.

Mode 8 separately converts the second argument to a byte boolean and calls 4303BC with R0=146, then joins the common epilogue. The epilogue `POP {R0,R4,R5,PC}` means R0 comes from the entry's saved R3 slot, except where the mask path overwrote `[SP]` with the saved PRIMASK. This also supersedes child/default R0 values on the paths that join here.

The report describes only these local paths; it does not establish hardware purpose or external child semantics.

No canonical files or gates changed.
