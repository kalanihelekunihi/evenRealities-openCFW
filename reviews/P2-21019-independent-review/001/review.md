# P2-21019 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47ED76..0x47EE26 (176 bytes); instruction/reference outputs match candidate. The 24-byte-frame body guards null object and nonzero high-byte mask, reads the head and sentinel independently, and preserves the OR-before-loop order. Each node preloads its next pointer before helper calls. Bit 26 selects equality of masked flags (including zero-mask equality) versus nonzero intersection; bit 24 accumulates matching masks, and the helper receives the node plus flags with bit 25 set. Aggregate clear occurs after traversal, followed by a fresh object-word return read. The wrapper returns saved R7, discarding that inner result. No cycle or external helper semantics are inferred.
