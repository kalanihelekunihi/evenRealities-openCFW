# Independent review 1827: arc left shift helper independent review 1827

Status: **PASS_SCOPED**. Accepted: **no**.

## Checks

- Candidate verifier passed exact package/record mapping, ELF carrier address, fresh GNU ARC decode, local branch/delay-slot checks and seven arithmetic fixtures.
- Independently checked the 42-byte owned span: BMSK immediate 5 retains count bits 0..5; count zero returns unchanged; counts 1..31 merge low-word carry in the delayed OR slot; counts 32..63 shift the original low word into high and clear low in the delayed slot.
- Fixture edge cases 0,1,31,32,33,63,64 are consistent with modulo-64 count and 32-bit shifts. The two delayed instructions are included in the owned bytes; following NOP and subsequent code are excluded.

## Limits

- No CPU execution, caller/ABI identification, global function boundary, or whole-image ownership is established.
- No canonical admission or C implementation.
