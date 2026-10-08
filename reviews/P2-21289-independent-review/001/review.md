# P2-21289 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482C9A..0x482D02 (104 bytes); instruction/reference outputs match. The traversal saves the next pointer before callback or unlink/release work and then uses that saved value for the current iteration. The end POP returns saved entry R3, not the loop state or last helper result. Descriptor endpoint accessors perform their observed null guards; computed-link accessors do not and derive offsets from the loaded descriptor word plus the supplied node index. No cycle/membership or fixed-field-offset assumption is made.
