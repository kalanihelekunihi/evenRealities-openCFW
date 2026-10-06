# Independent review 15969

Partial, accepted:false. Fresh replay passed for 352 bytes at 0x5226e8..0x522848. VCMP/VMRS tests m[6]/m[7] against +/-1e-7 with APSR predicates; path at 0x522740 divides matrix offsets 0..20 by a freshly loaded m[8]. Allocation 6/9 occurs after possible input mutation. Short/long records then store command words in exact order; R0 advances by four before final indexed store, then restores R4/PC. The bottom-left-minus-one operation is literal.

Allocator/external-child behavior remains unresolved; no admission or gate change.
