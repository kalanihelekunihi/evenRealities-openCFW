# Independent review: P2-19177

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x46A18C..0x46A1DE` (82 bytes) matches candidate instructions and references. The frame saves the original R0 in R6; the first child result is stored through the global pointer, and subsequent global words are freshly loaded. The two later arithmetic paths perform wrapping 32-bit subtraction before signed division by 2, with child calls in the recorded order and live argument registers. Signed division matters for negative odd differences; no arithmetic-shift substitute or geometric contract is inferred.
