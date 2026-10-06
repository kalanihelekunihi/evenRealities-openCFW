# P2-15945 independent review

The 192-byte map at 0x5406A4..0x540764 matches original bytes. It forms wrapped bounds, uses signed endpoint comparisons, and selects the maximum for SP+72 (the map’s explicit distinction from preceding minimum selections). It preserves the mutated R10 selection, ordered child calls, fresh stack reads, literal structure word, and VCVT.F32.S32 under architectural FP controls.

This remains a partial raw-candidate reconstruction. Child effects, function-boundary/reachability proof, FP architectural conditions, and physical behavior remain open. No admission, C, or gate change.
