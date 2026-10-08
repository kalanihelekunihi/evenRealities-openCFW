# P2-21165 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481022..0x4810B0 (142 bytes); instruction and literal-reference outputs match. Modes 2 and 5 call the helper, stage its full result at SP0, use the fresh indexed word for XOR, store the result, then reload SP0 for MSR PRIMASK. Modes 3 and 4 directly store the computed mask without a prior read. The shared tail returns zero and restores 16 bytes; default selectors reaching it perform no writes or helper call. There is no 224 bound or pointer validation in this routine.
