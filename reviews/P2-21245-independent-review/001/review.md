# P2-21245 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x48246C..0x4824EE (130 bytes); candidate instruction and literal-reference outputs match. The shared conversion path records live helper arguments and ignores the helper result; the character entry advances and stores the argument byte, while the fallback entry stores the percent marker and conditionally emits the conversion byte under the original full-width comparison. The padding computation reloads stack slots in order and subtracts modulo 2^32; bit-2 and signed-positive checks govern the backward branches. Success preserves live R0; the explicit failure entry sets R0 to FFFFFFFF. ADD SP,196 plus the 36-byte POP releases the 232-byte frame. The downstream targets remain outside this candidate.
