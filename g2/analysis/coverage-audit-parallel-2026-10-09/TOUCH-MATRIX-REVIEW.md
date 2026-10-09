# Independent final touch compiler matrix review

Decision: reported bounded compiler comparisons are supported. No new exact Configure attribution or unique producer identification is justified. [TOUCH-MATRIX-VERIFICATION.json](TOUCH-MATRIX-VERIFICATION.json) supplies independent repository-only checks; no compiler/container/test was rerun.

All three vendor archive hashes, GCC executable hashes, recorded consumed input hashes and four output hashes per candidate match current files. Independently parsed little-endian ELF32 ARM objects have the expected named sections. Full-byte comparisons against the fixed official target controls reproduce Configure differences 173/125/125 for 10.3/11.3/12.2, Capture exact for all, ConfigureScan 30 differences for 10.3 and exact for 11.3/12.2. All selected lengths match target lengths, and no nonempty REL/RELA section targets them. No masking or relocation normalization was used.

The unchanged source SHA is verified via the authenticated repository copy at `tools/pdl-input/drivers/source/cy_msclp.c`. Consumed header hashes match receipt files; read-only input mounts are documented in the owner script. This verifies final input identity, not an independently observed continuous before/after history. Compiler-specific standard/newlib headers legitimately differ across releases. The prior 13.3 24-byte difference is inherited from the sealed original receipt and was not rerun or re-created here.

## Conclusions allowed by this matrix

Under this exact public PDL/header/device/flag environment none of 10.3, 11.3 or 12.2 produces exact Configure. 10.3 also fails ConfigureScan, so is inconsistent with reproducing all three unchanged-source target bodies in this environment. 11.3 and 12.2 preserve both exact peers, but fail Configure. 13.3 is the closer selected comparator by byte difference; closeness is not producing-toolchain attribution. Other flags, different translation-unit definitions, source revision or private modification remain possible. No generated cycfg, complete configuration, SDK checkout identity, source completeness or whole-image equality follows.

## Exact remaining discriminator

The next discriminator should bind the prior 13.3 mismatch's exact instruction/control-flow window to the unchanged Configure preprocessed source, rather than use a generic SDK/version sweep. Configure begins at source line 298; its register-array loops are at lines 347 and 353. Determine which loop/condition actually accounts for the 24 byte positions by recording original/compiled disassembly and branch targets at the corresponding offset. Do not assume both loops or generated cycfg are responsible merely because they exist.

Compare that loop's effective declarations and macros in saved `.i`: index width/signedness, register-pointer volatility, config pointer/member layout, MSCLP_CSW_GLOBAL_FUNC_NR and MSCLP_SENSE_MODE_NR, device/IP definitions and any conditional compilation. Normalize only line markers/path metadata for source comparison, never opcode bytes for exact attribution. If those effective inputs are unchanged, inspect genuinely different already-present PDL source revisions for the specific loop ordering/termination; compile only a distinct evidenced alternative. An arbitrary rewritten loop or instruction ordering can demonstrate compatibility but cannot prove original public-source provenance.

## Receipt improvements before campaign admission

The matrix script authenticates source but does not assert full target SHA before slicing; this independent audit uses the previously fixed target controls, so local comparison correctness is supported. Add explicit full target identity and slice hashes to an immutable adoption receipt. Preserve actual command/exit logs and failure history (including initial mount error); the script makes argv reconstructable and check_output enforces successful exits but results do not independently log every argv/exit code. Bind archived source copy/header provenance and independent review before canonical promotion. These are durable receipt improvements, not a reason to rerun successful comparisons.

Review writes only additive audit files. No source, index, state, Git, Docker, firmware, device or denied-path action was performed.
