# Independent review 1787: scoped pass

The exact body is 486C..48A4 (56 bytes, 28 instructions); the literal pool starts at 48A4 and is excluded. Independent operand-based literal extraction agrees with the candidate. Original instructions first branch on null R0, otherwise emit 12 word stores in the listed order, zero fields at +32,+36,+0, return zero, and preserve SP. The three fixtures reproduce in isolation, including the null error literal and two aligned destinations.

The pointer targets remain unknown and physical storage effects are outside scope. No canonical acceptance or coverage change is made.
