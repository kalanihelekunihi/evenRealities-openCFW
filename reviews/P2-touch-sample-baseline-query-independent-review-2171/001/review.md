# Independent review 2171: sample baseline query

**Result: PASS_SCOPED.** Candidate `analysis/touch-sample-baseline-query-4fee-2168/001` remains unaccepted.

The exact main and two leaf spans match the source. The main preserves the zero helper’s status, uses unsigned full-width threshold comparisons, clears or increments the counter byte as decoded, and takes the reset leaf when the counter reaches its limit. The blending path gates on the header byte and first threshold, then calls the original weighted arithmetic leaf and stores its result across baseline and fraction fields. R4-R7/SP restore.

The isolated 5,184-fixture replay passed and matched frozen JSON; independent Thumb decoding and all source/artifact hashes passed. The test matrix gives both threshold parameters the same value, so divergence between offsets 26 and 28 remains untested. Physical meaning, aliasing and concurrency remain open.
