# P2-21003 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47EA90..0x47EAF6 (102 bytes), with instruction and reference output matching. The drain loop uses repeated pointer/field loads; after the zero observation, the pointer exchange is ordered as two separate loads and stores. Its POP returns saved R7, not the exchanged pointer. The second entry has a fresh global guard; when initialization runs, it obtains two helper values, writes two globals, overwrites saved SP0 with zero, calls the initialization helper with the explicit fifth argument, stores the full result without checking zero, then always invokes the trailing helper. Return slots are therefore path/callee-write dependent. No external helper contract is inferred.
