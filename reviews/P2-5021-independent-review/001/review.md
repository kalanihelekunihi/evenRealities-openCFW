# Independent review 5021/001

**PASS_SCOPED**; `accepted` remains false.

Fresh isolated replay passed all 768 original-code cases: all 256 low-byte selector values across three initial register patterns, with high input bits set. The three output register words, status, path-dependent R1, selected child and arguments, SP, and PC match the candidate assertions. Pinned source, dispatcher-map references, and candidate files verify.

The tested setup uses null configuration, zero source fields, and controlled zero child results. Nonzero child outcomes, nonnull/changing/aliased configuration, hardware behavior, and global completeness remain outside scope.

Candidate receipt SHA-256: `c7e10ccee0a45d6f486b323755ec78d2c7431879f6ec3544ded65b6b33309127`.
