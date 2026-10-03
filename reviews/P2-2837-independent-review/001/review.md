# Independent review 2837 — current-restore APSR pattern sweep

**Result: PASS_SCOPED.** Source/body and artifact hashes match; the isolated 72-fixture replay passes. The 72-case replay independently supports the final flag claim: final N=0/Z=1, C equals bit20 of the third selected profile word, and V is preserved. Ordered read/write behavior, output registers, high-register/frame/mask preservation also pass.

- Four incoming NZCV patterns are exercised across the listed three index sequences, three profile-word patterns, and two masks; this does not cover all machine states.
- Injected index updates model changing state; real concurrency/peripheral semantics and caller ownership remain unresolved.
- No canonical admission.
