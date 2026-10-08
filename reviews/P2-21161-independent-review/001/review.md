# P2-21161 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480F0C..0x480F8A (126 bytes); instruction and literal-reference outputs match. The unsigned index bound precedes the indexed capability tests. With the first capability bit clear, the configuration field 10..11 is tested before the second capability bit; with it set, field 13..15 accepts only 0, 6, or 1. Validation failures return 5 or 7 without writes. On acceptance, the helper is called with the recorded live arguments and its full result is staged at SP0. The code then performs ordered stores of 115, the full configuration word, and 0 through the same global pointer, followed by MSR PRIMASK from SP0. POP returns the helper result through R1 on success and restores the saved entry slot on validation errors.
