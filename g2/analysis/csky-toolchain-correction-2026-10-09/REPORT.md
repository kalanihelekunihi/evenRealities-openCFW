# Additive C-SKY opcode/ABI qualification

No historical packet is modified. Official vendor assembler source now confirms
the descriptor's exact instruction fields: at0x1020590A, MULA.32.L operands
r13,r0,r23 reproduce wordFAE0844D; at0x1020592A, BNEZAD r18 with signed
halfword displacement-17 reproduces E832FFEF and target0x10205908.
`verify.py` checks actual child bytes against vendor-pinned operand definitions.
This is static encoding verification, not original-instruction execution.

The assembler's CK804 feature mask includes both required revision features.
That supports CK804 eligibility; it does not identify the physical core.
The authenticated NationalChip SDK requests CK804EF despite its CK803-named
runtime directory. A directory name therefore cannot identify the CPU.

The vendor GCC target header at1e9b70447a8417f5c692370de4533e43d754e8fa
explicitly corrects the published V2 ABI's eight-byte stack statement and sets
STACK_BOUNDARY32bits, four bytes. Prior packets accurately retained the manual
text, but their unconditional eight-byte compiler requirement is superseded
by this qualified compiler-source evidence. The descriptor leaves SP unchanged;
its caller saves three32bitregisters, consistent with four-byte alignment.
Neither fact authenticates this modern compiler as the producing compiler.

The earlier manufacturer-origin positive BNEZAD formula and local decoder's
nonzero discrepancy remain separately recorded. Opcode/feature tables do not
prove execution semantics. The fixed positive8..0 loop still has the same
result under both documented models; broader negative/zero behavior remains
architecture-specific. Source hashes, exact bytes and operand checks are in
results.json. Physical target configuration, exact producer and coordinator
adoption remain open; no campaign counters or records were changed.
