# P2-21219 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481E46..0x481E80 (58 bytes); instruction and literal-reference outputs match. Signed-negative precision sets the budget to 33; nonnegative precision increments it modulo 2^32, and R7 receives then increments that budget. The helper receives the original raw pair, zero pair, and normalized pair. Its returned carry is tested immediately; carry-clear toggles the sign bit of R5. The code then stores the low byte of returned R2 at SP132, adjusts the saved exponent by four, loads SP133 into R6, and uses a signed R7 budget branch to the zero-budget path or digit loop. Helper semantics and later loop behavior remain unresolved.
