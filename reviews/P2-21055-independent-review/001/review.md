# P2-21055 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F7AE..0x47F85E (176-byte prefix); instruction/reference outputs match candidate. The index-29 path uses separate fresh word observations, unsigned less-than-34 guard, bit-21 check, and a literal helper call with fifth argument 1. The index-28 route performs ordered, distinct word clears (bit24, bit0, then bits1..3). The remaining path uses a fresh protected pointer/mask read and independently reloads the pointer for store, restores PRIMASK from SP20, and ends with the 40-byte frame active at F85E. No unwind or external address/helper contract is claimed.
