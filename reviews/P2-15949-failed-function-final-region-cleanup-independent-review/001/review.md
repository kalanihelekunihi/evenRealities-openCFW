# P2-15949 independent review

The authoritative 002 packet exactly maps 386 bytes at 0x540842..0x5409C4. Its branch references target 0x5408EA and 0x5409BE, consistent with instruction decoding; the early exits from 0x5400F8 and 0x5401FC in the preceding fragments enter the shared cleanup while preserving child return context. The cleanup retains separate child return values/arguments, a 3-byte copy into SP, a subsequent whole-word load whose fourth byte is not presumed zero, fresh alpha reads, and final epilogue arithmetic: add 188 to the local-frame SP then pop nine words (R4-R11 and PC), skipping saved entry R3 and restoring the 224-byte frame. The final normal R0 derives from the 0x44F758 child; R9/R11 mutations remain local and saved entry registers restore.

This remains a partial raw-candidate reconstruction. Child effects, function-boundary/reachability proof, FP architectural conditions, and physical behavior remain open. No admission, C, or gate change.
