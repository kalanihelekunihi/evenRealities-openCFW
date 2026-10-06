# P2-15943 independent review

The 178-byte map at 0x5405F2..0x5406A4 tiles the source exactly. It retains signed bounds comparison and fresh loads, then follows the clip/init path and uses literal word 0x5409D8 as a data value. Wrapped coordinate differences are converted via VCVT.F32.S32; architectural FP controls and child effects remain unresolved.

This remains a partial raw-candidate reconstruction. Child effects, function-boundary/reachability proof, FP architectural conditions, and physical behavior remain open. No admission, C, or gate change.
