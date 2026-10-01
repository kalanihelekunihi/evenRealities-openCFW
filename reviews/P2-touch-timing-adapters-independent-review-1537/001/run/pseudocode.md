# Touch timing adapters

5FA4 is the exact 22-byte body [5FA4,5FBA). Inputs are value, multiplier and divisor. If divisor is zero, return 0xFFFFFFFF without calling division. Otherwise multiply value by multiplier modulo 2^32, call A6C0 with that product and divisor, and return its quotient. The eight-byte frame is restored. All 64 fixtures execute the original division helper where applicable and compare the unsigned quotient, including overflow and large divisors.

A324 is the exact 14-byte body [A324,A332). Read a byte from literal address 0x20000870 (literal at A334), multiply the full incoming R0 by it modulo 2^32, and call 4480 with the product. Return its incidental R0 and restore the eight-byte frame. The machine body itself does not narrow the input to uint16, despite the historical upstream signature label. Twenty fixtures validate the full input width, frequency byte, wrapped product and helper result with 4480 controlled. The delay loop's separate recovery remains relevant; physical elapsed time is not established here.

These are private pseudocode evidence only. No canonical admission, whole-corpus freeze or C implementation is claimed.
