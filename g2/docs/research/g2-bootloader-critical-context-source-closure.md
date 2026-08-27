# G2 bootloader critical-context predicate source closure

Status: software implemented and production-routed; physical validation blocked.

Aggregate package and accounting values below record this historical
checkpoint and are superseded by the gate-acquire closure that follows it.

The complete 46-byte entry `[0x0041602A,0x00416058)` has SHA-256
`e9208bab7b82a1d6f0228d69b2707c5cfadd5cb45b7d24963defe8cabb00b32b`
and 21 authenticated direct callers. It returns one immediately when IPSR is
nonzero; otherwise it calls the retained runtime-state query at `0x00418B56`.
State `1` returns zero without reading masks. Other states return one when
PRIMASK or BASEPRI is nonzero and zero otherwise. Host tests pin this ordering,
including both short-circuit paths.

`runtime_critical_context.c` is a 1,497-byte GPL-3.0-or-later clean-room
implementation using explicit ARM system-register reads. Apple emits a
46-byte leaf at offset 2,930/runtime `0x00434FEA`, with raw SHA-256
`b0872e0e51a3e5cb6e1c00902e393341120ac4924520aeccad730b5dadf024df`
and relocated SHA-256
`b4224673233986ba4f05f216692e29cf60034023573e891c9cdb546e3616f8f0`.
Its sole strict relocation is an `R_ARM_THM_CALL` at offset eight to
`0x00418B56`. Linux preserves the size, raw body, relocation contract, and
profile-adjusted placement. The stock span is exactly replaced by a branch
and 21 Thumb NOPs.

The canonical 2,976-byte overlay hashes to
`3a783c9069608891201daac2ab54e8c987a06de1045283ac41cdec0bade7f8cb`.
The 151,576-byte provider hashes to
`23e8340be2c6dc2c4a9ad560411e161353bb8932484dbede35c578366d2be1e5`
and accounts for 2,969 source, 3,484 patch, eight alignment, and 145,115
retained authenticated bytes. It ends at `0x00435018`, leaving 12,264 bytes
before Apollo main. The Linux provider is 151,568 bytes with SHA-256
`f11dbf10eac176f5def869f48686d8525e7b0861aa01f10839ac5f5a176373cd`.

The canonical unsigned package is 4,733,154 bytes with SHA-256
`31ee8a1d8bc3bd05608ca6c90bd77b94be6d1ddd984f4f4edad8419db41d547d`;
its flash plan is 4,336,291 bytes with SHA-256
`c8e59474f65ab1077736a2774d18c9c23581eee04912e2f96657d1b484b71610`
and 6,246 placed regions. The Linux package is 4,509,156 bytes with SHA-256
`c899ea33aba87d6d7b79146160380160f245e188cc0b721994cb341511e1db8b`;
its plan is 2,308,161 bytes with SHA-256
`82afcbc69a9bbe04a0ef625467fb760e77658b16400eb3d6c5d89e14bae7d0e5`
and 3,319 placed regions. Both retain two unresolved physical-only regions.

The preceding two-byte self-loop has no direct ingress; the two-byte no-op
return has one caller from the later state-transition function. Both remain
authenticated compatibility bytes because neither can contain a long redirect
without overwriting a neighboring complete entry. No signing, hardware access,
or runtime claim was made. Authorized right-temple validation remains blocked.
