# Calibration completion at 6980

The 58-byte body [6980,69BA) is followed by alignment and two literals. Resolve peripheral through descriptor/configuration pointers. Original A6C0 divides configuration word0 by literal1000000. Call5FA4(originalR0,quotient,5), retaining its countdown. Repeatedly read peripheral word100: stop when bit8 is set, or countdown is zero; otherwise decrement and repeat. Always write cleanup literalC1011111 to that register and read it back. Return remaining countdown, preserving zero even if ready arrives on the final check. Restore16-byte frame.

The72 original-instruction fixtures check exact budget+1 maximum reads, immediate/delayed/absent readiness, real division, exact5FA4 arguments, cleanup and frame. 5FA4 is controlled and readiness reads are explicitly modeled. Physical timing/register semantics remain unresolved. No canonical admission or C implementation.
