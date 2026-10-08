# P2-21277 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482A5A..0x482AB2 (88 bytes); instruction and reference outputs match. The frameless predicate returns the byte-derived boolean. The mapping path preserves full-input equality checks for 255 and zero, then uses the byte threshold branch; the lower table lookup uses UXTB indexing. The upper branch adds 118 to full R0 before loading the context pointer and bounds word, narrows the index, then independently reloads the dynamic table pointer for the final byte lookup. No second null guard or table extent is inferred.
