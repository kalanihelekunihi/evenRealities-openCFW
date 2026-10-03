# Independent review 2743

**Result: PASS_SCOPED.** Static verifier decoded 198 original instructions exactly over `0x428E6A–0x4290A2`; source/body/artifact hashes match. The instruction map supports the three-word stack result, conditional wait/service path, publication sequence, gate/auxiliary logic, high/low target manipulation, final secondary call, and unusual R0/R1/R2 return values. This is static-only evidence.

- Dynamic execution is not claimed.
- Changing reads, caller ownership, and physical timing/peripheral effects remain unresolved.
- Private evidence only; no canonical admission.
