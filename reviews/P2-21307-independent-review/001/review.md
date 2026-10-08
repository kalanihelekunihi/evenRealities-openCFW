# P2-21307 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482FAA..0x482FF2 (72 bytes); instruction/reference outputs match. The 8-byte wrapper returns a full stack word after either the three-byte helper path or fallback call and store. The later 16-byte wrapper reads and reloads the recursive field, calls recursively before checking/reloading the callback pointer, and invokes the callback with the loaded pointer and live R3. No second callback null guard or recursion guard is present in this slice. The epilogue returns saved entry R3 in R0. Helper/copy semantics remain unresolved.
