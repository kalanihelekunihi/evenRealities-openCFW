# Preserved oversized-length fixture

The first verifier included length0x7fffffff with misalignment. The original did not return within the30,000-instruction cap, producing the STOP assertion failure before any result file was written. The exact initial verifier is preserved here; no PASS coverage was taken from this failed run.

Static arithmetic explains why this is not a one-write test: misalignment addition may cross the signed boundary, but the first subtraction by32 brings the value back to the positive signed range, causing a very long loop. Those inputs were removed from bounded completed-path cases, rather than raising an unbounded emulator cap or claiming immediate return. Source/ELF are unchanged. Accepted comparisons cover practical sizes up to3200, signed nonpositive inputs, and bounded address-wrap cases. Complete huge positive-length execution remains unverified.
