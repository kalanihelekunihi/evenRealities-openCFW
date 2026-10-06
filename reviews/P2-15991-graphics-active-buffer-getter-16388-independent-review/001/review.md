# Independent review 15991

Partial, accepted:false. Fresh decode replay passed for 10 bytes. Loads global pointer, dereferences its first word, then loads word +4 as return value. R1 holds intermediate pointer; no local frame/flags changes or null check.

Child/global/hardware effects remain unqualified; no admission or gate change.
