# Touch configuration register command A148

ExactA148..A180 instructions accept `(R0==1 && unsignedR1<=1) || (((R0-2) modulo256)<=1 && R1==0)`. The second test truncates to eight bits, so supplied inputs258/259 withR1zero are accepted as well as2/3. Accepted inputs write one word to40010000: `40000000 | ((R0<<6)&255) | (R1&63)` and returnzero. Rejected inputs return literal004A0001 without a register write. No stack frame or helper calls occur; volatile command semantics beyond the word write remain unresolved.

Fifty-four original-instruction fixtures exercise canonical values, large aliases, mode boundaries andFFFF_FFFF. Independent predicate/postconditions check exactwriteaddress,width,value,unchangedMMIOonrejection,rawreturnandSP. SyntheticMMIOdoesnotprovephysicalcommandinterpretation. No canonicaladmission orCimplementation.
