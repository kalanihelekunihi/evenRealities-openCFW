# Configuration validator with original range chain

Original 6384 now executes original 6352, 6330 and 6270 when a negative signed row byte requires range-factor calculation. Original 6262 also executes on the low-flag-bits-equal-one path. The 216 fixtures check exact remaining helper calls, row writes, status and stack restoration. Record percentage byte +135 is initialized to zero in these fixtures: controlled unsigned A6C0(0,100) returns zero, the range bucket becomes zero, and 6352 returns 128. The later factor helper reads that newly stored byte with bit 7 cleared.

623C and 6294 remain controlled. Division is controlled; the broader percentage/shift contracts are exercised separately by 1421. Mixed-row mode/width behavior is covered by 1415. Physical meaning and pointer validity remain unresolved. No canonical admission or C implementation.
