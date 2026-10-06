# P2-15941 independent review

The 152-byte map at 0x54055A..0x5405F2 exactly matches the pinned image. It writes wrapped bounds from the current frame, preserves signed comparison behavior on the endpoint, and uses ordered 0x540024/0x450BCC/0x450F28 gates. On the transform path it computes wrapped differences and performs VCVT.F32.S32 conversions under architectural rounding/status controls, with child effects left unresolved.

This remains a partial raw-candidate reconstruction. Child effects, function-boundary/reachability proof, FP architectural conditions, and physical behavior remain open. No admission, C, or gate change.
