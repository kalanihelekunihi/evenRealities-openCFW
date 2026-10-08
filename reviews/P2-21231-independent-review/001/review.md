# P2-21231 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4820BC..0x482112 (86 bytes); instruction and literal-reference outputs match. The routine reads a fresh separator byte from the pointer at returned R0+36 without a null guard. Nonpositive retained count uses SXTH and falls back to ADR 0x4826F8; positive count keeps full R6. Conversion `f` increments the full exponent and branches to fixed layout. Conversion `g` uses signed SXTH exponent comparisons against -4 and precision before incrementing; flag bit 3 controls whether retained count clamps signed precision. The remaining path subtracts the sign-extended exponent from R8 and uses the MI condition to clamp negative results to zero. Other conversions branch to an unresolved path.
