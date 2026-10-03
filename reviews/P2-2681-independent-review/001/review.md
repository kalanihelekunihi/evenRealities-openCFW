# Independent review 2681: complete original service chain

**Result: PASS_SCOPED.** `accepted` remains false.

All 384 isolated fixtures pass and match the candidate replay output byte-for-byte. The flag-2/flag-7 services, common service body, operation-4 dispatcher/query, delay conversion, and ITCM loop all run original instructions. The combined ordered writes, PRIMASK mask during writes, callback order, delay counts, and return frame match the assertions. The operation-4 table is zeroed, so the composition exercises only its inactive state path.

Inputs are stable synthetic RAM/MMIO and clock fixtures; no physical timing or hardware effect is claimed. Active operation-4 state behavior remains separate evidence. No canonical admission.
