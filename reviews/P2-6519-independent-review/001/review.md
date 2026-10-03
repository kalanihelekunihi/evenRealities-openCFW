# Independent review 6519

Disposition: **PASS_SCOPED**; `accepted:false`.

Both body hashes and packet-file hashes match the locked image. GNU Thumb decoding confirms the frameless leaf's signed-low-halfword guard and indexed wholeword mask store for nonnegative inputs. The wrapper saves R3–R7/LR in a 24-byte frame, preserves the input in R5, and conditionally performs the two type-4 setup calls only when the input's low byte is 4; their results are ignored.

All inputs then reach the retry path. R6 is initialized to zero; each attempt freshly loads the base and entry handle, calls 42C988 with (handle,2,1), and keeps its result in R4. Zero exits successfully. A nonzero result calls delay 41F9D8(10), increments R6, and repeats until the unsigned-positive counter reaches 1000. Therefore the code makes up to 1000 attempts and, on the all-failure path, also makes 1000 delay calls. It returns zero on success or 4 after exhausting the attempts, then restores the saved registers. The retry bound is unaffected by R4 input because the counter is separate.

No index-bound, hardware timing, callee-purpose, or broader behavior claim is made.

No canonical files or gates changed.
