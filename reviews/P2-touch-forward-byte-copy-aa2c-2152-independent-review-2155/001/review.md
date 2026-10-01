# Independent review 2155: Forward byte copy at 0xAA2C

**Result: PASS_SCOPED.** Candidate `analysis/touch-forward-byte-copy-aa2c-2152/001` remains unaccepted.

Independent Thumb decode confirms the exact 18-byte body [0xAA2C,0xAA3E): index starts at zero, source byte load and destination byte store occur in increasing index order until R2, then incoming R0 is returned. R1/R2 and saved R4/SP are restored/preserved as described.

The isolated 70-case replay matches byte for byte and compares the whole mapped allocation plus ordered stores across zero/boundary lengths, identical buffers, overlaps in both directions, and separate buffers. It demonstrates forward-copy overlap propagation for the tested mapped addresses.

Limit: Only mapped ranges and tested lengths are covered; address wrap, faults and malformed memory are unresolved.
Limit: No canonical admission or C implementation.
