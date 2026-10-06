# Active buffer getter, 0x5144FA..0x514504,10 bytes
R0=word[0x514B78]; R1=word[R0]; R0=word[R1+4]; returnviaLR
No stack/calls/flagchanges. Literalpointerdata outsidecode, noNULLvalidation; R1 clobberedcontextpointer, otherintegerregisters unchangedlocally. Objectlifetime/fault/concurrencyconditionsnotqualified.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
