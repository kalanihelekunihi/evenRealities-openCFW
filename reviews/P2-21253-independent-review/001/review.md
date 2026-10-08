# P2-21253 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482590..0x48262C (156 bytes); candidate instructions/references match. The returned digit is narrowed to a byte and adjusted through the recorded branch before storing backward. The next helper call uses the live pair/radix arguments; its full returned pair controls the zero test. The buffer guard is unsigned. The octal prefix path uses separate fresh flag and output-byte reads. Width, pointer, and padding updates preserve the observed ordered stores and signed precision/width branches. The 40-byte POP returns saved slots whose values may have been overwritten at SP0/SP4, so no status-return interpretation is made.
