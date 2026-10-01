# Independent review 1975

**Result:** PASS_SCOPED.

- Ran the candidate verifier successfully; it validates authenticated source/package/body mapping, exact 72-byte span, decoder/table geometry, caller-context evidence, fixtures and recorded pins.
- Independently inspected BIH manual semantics and the seven inline halfword branch destinations; unsigned index >= 7 and index 5 return zero, while local writes/calls match the stated cases.
- Confirmed the three caller sites select indices 2, 1 and 6 with the pinned pointer arguments; this is bounded caller evidence only.
- Receipt output hashes were checked against all candidate files.

**Limits:** The three nested callees and external target identity remain unresolved. No caller census, whole-image closure, physical-effect or canonical-admission claim is made.
