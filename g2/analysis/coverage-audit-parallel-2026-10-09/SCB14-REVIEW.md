# Independent SCB14 holdout result review

Verified all three predeclared whole-section matches: ReadArrayNoCheck56, WriteArrayNoCheck56 and WriteDefaultArrayNoCheck16. [SCB14-VERIFICATION.json](SCB14-VERIFICATION.json) independently parses retained ELF32 ARM sections, compares wrapper-inclusive locked target bytes, checks lengths/hashes and confirms no selected relocation sections. No match masking or adjustment is needed.

Every consumed file/output hash and reused GCC executable hash matches. Flags, includes and container digest equal the original14.2 MSCLP comparator; all common header hashes agree. SCB-only dependencies are verified at their recorded hashes rather than incorrectly asserted to be MSCLP dependencies. The unchanged C source hash matches the predeclared plan. The official compiler archive provenance was already independently checked in COMPILER14-VERIFICATION; it was reused, not reacquired here.

Correct absolute payload offsets are0x5F38,0x5F8E,0x5FF6, derived as32+flash−0x3300. coordinate-receipt.json explicitly binds result hash and both coordinate systems. Historical offsets omit32-byte wrapper; no historical record was rewritten.

All three planned targets appear in results, with no observed additions/drops or flag changes. ReadArray was already exact under older compilers, so it is a generalization control, not a14.2-only discriminator. Selection was from known attribution candidates, not a random unseen sample. SCB success extends selected-source comparison across a separate translation unit.

Supported combined scope is six selected functions across two PDL translation units, totaling760 distinct selected section bytes (632 MSCLP+128 SCB). This is a comparator total, not newly recovered/admitted/source-complete coverage; prior exact peers and ReadArray must not be recounted as new evidence bytes. No unique producing compiler/revision, complete configuration, all-PDL attribution, whole touch image, physical execution or gate pass follows. Further extrapolation needs independent function/configuration evidence and whole-image accounting.

Only repository evidence was read; additive audit output was written. No builds, downloaded code, source/state/index/device action or denied-path retry occurred.
