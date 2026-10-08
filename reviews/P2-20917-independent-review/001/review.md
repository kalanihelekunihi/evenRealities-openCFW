# P2-20917 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the locked image for the 72-byte span 0x47DA78..0x47DAC0. Candidate and fresh instruction JSON, pseudocode, and references match; the decoded instructions tile the span exactly.

The routine allocates 32 bytes in two pushes and uses SP+20 as the pointer to the first saved argument words. A null entry and a zero computed capacity bypass work. Capacity is computed with wrapping subtraction `4499 - index`, with no unsigned-underflow rejection. A second independent index load forms the buffer address for the 44B76C call; the result is tested with signed `BLT` against 1, then compared unsigned to capacity for the index update. The successful update branches use separate fresh index loads and wrapping additions. The shared terminator path performs yet another fresh index read and byte-zero store, with no separately recovered bounds check. The initial null/capacity-zero routes skip it.

The epilogue pops the saved R3 slot into R0, then loads saved LR into PC while advancing SP by 16; it therefore returns saved entry R3, not the formatter result. Helper memory effects remain unresolved. Candidate status stays partial/unaccepted; no source or gate files changed.
