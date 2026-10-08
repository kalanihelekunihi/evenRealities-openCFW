# P2-21149 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480BC2..0x480C56 (148 bytes); instruction and literal-reference outputs match. Mode 5 preserves full helper errors and validates a fresh selector word; on accepted nonnull input it uses a second fresh selector read to construct the output word. Null input follows the separate 0x4000 configuration path. Mode 6 stores both word updates before its helper call, and full helper failures are returned without rollback. Default selectors return 6 without the mode writes or helper call. The common POP returns the SP0 slot in R1; successful mode 5 writes that slot, while other paths retain its prior contents absent alias effects.
