# Independent review: P2-19193

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x46A450..0x46A4E2` (146 bytes) matches candidate instructions/references. The diagnostic paths capture SP12/SP8 and use distinct status calls for bit1, bit0, and conditional bit2. Selector dispatch uses the fresh low byte at SP12: 68, 69, and 10 call their separate handlers; 72 takes its mode-dependent route; default retains the selector value in R0. The shared epilogue adds 24 and pops the remaining frame without normalizing R0, so the incoming ring-empty child result and the distinct selector results remain path-specific.
