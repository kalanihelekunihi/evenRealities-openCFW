# P2-21223 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481EE6..0x481F6A (132 bytes); instruction and literal-reference outputs match. The signed budget selection is capped by the signed digit length; when the chosen discard count is below length, a fresh digit chooses threshold 15 or 0. The backward scan post-decrements the pointer and count until the byte equals that threshold, with no separate encoded bound guard; the SP132 byte therefore remains a relevant sentinel/helper result. A 15-threshold path reloads and increments the retained digit. Negative R2 adjusts SP0 exponent by four and adjusts count; nonnegative selects SP133 as source. ASCII formatting writes digits backward and uses the original conversion byte R11 for alphabetic adjustment. Negative precision stores R0-1; nonnegative precision follows the other branch. Rounding policy beyond these operations is unresolved.
