# Independent review 2231

**Result:** PASS_SCOPED.

The candidate source hash and `[0x68EC,0x6928)` body hash match the receipt; the receipt’s four artifact hashes also match. Independently decoded Thumb/M-class instructions agree with the listing: the two `56A4` calls receive `(0, context)` and `(1, context)`, followed by `8FD0(registerbase, context+36, 2, *(root+8 pointer+4))`. Its result is saved across the unconditional `685C(context)` call. The tail returns zero for a zero loader status and 64 otherwise, restoring the saved registers and stack.

An isolated replay regenerated all 16 fixture rows. The only intercepted calls are the two `56A4` entries; original `8FD0`, `685C`, `6608`, `A324`, and `4480` execute. Assertions cover child arguments/order, loader status mapping, the unconditional `685C` call on success and failure, `config+113` clearing, preserved registers/SP, and the 315 original `A324(1)` calls for clear status bit 0. The register-write ledger is captured, but the candidate does not assert every captured write against the constructed expected ledger; I therefore do not treat the complete combined write sequence as independently verified.

**Limits:** Loader configuration, factory/status RAM, and peripheral status are modeled. This establishes bounded software control flow and the asserted state, not physical MMIO or timing behavior, actual `56A4` effects, aliasing, or concurrency. No canonical admission is made.
