# P2-15947 independent review

The 222-byte map at 0x540764..0x540842 matches original bytes. It retains signed comparisons over wrapped values, including R11+1 and R10-1, and the branch-selected updates to SP+64/SP+72 and R10. Child calls, literal 0x5409D8, fresh loads, wrapped transform values, and VCVT.F32.S32 ordering match the disassembly; FP controls remain architectural.

This remains a partial raw-candidate reconstruction. Child effects, function-boundary/reachability proof, FP architectural conditions, and physical behavior remain open. No admission, C, or gate change.
