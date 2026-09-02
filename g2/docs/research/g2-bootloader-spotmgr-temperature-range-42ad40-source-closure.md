# G2 bootloader SPOT-manager temperature range source closure

The hard-float leaf at `0x0042AD40` classifies temperatures into four valid
ranges bounded by -273, -20, 0, 50, and 1000 degrees, returning the out-of-range
class for invalid, infinite, or NaN input. Both reviewed compilers reproduce
the exact 120-byte body, which is also an exact Apollo-main match at
`0x005A0A70`. Host tests cover every boundary and non-finite class. Hardware
temperature validation is blocked by unavailable physical evidence.
