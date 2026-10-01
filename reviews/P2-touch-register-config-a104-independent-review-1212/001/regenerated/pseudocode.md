# Touch configuration register command A104

Exact A104..A13C instructions accept `(R0==1 && unsignedR1<=1) || (((R0-2) modulo256)<=1 && R1==0)`. The second test truncates to eight bits, so supplied inputs258/259 withR1zero are accepted as well as2/3. Accepted inputs write one word to40010000: `8000FF00 | ((R0<<6)&255) | (R1&63)` then perform one fresh word read from that same address and return zero. The read value does not affect the return. Rejected inputs return literal004A0001 without a register write. No stack frame or helper calls occur; volatile command semantics beyond the word write remain unresolved.

Fifty-four original-instruction fixtures exercise canonical values, large aliases, mode boundaries andFFFF_FFFF. Independent predicate/postconditions check exactwriteaddress,width,value,unchangedMMIOonrejection,rawreturnandSP. SyntheticMMIOdoesnotprovephysicalcommandinterpretation. No canonicaladmission orCimplementation.
