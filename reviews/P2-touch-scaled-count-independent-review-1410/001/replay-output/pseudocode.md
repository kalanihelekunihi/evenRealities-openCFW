# Scaled count helper at 5D70

Read the context pointer at descriptor + 8, then its word at offset 44. Multiply the input by that word with unsigned 32-bit wraparound and shift right by 14. If the scaled value is zero, return zero. Otherwise subtract one and return the smaller of that result and 65535. There are no stores, calls or stack changes.

The instruction span is [5D70,5D8A), 26 bytes. The halfword at 5D8A is alignment NOP; the word at 5D8C is the 65535 literal. The 121 original-instruction fixtures check wraparound, zero, decrement and saturation against an independent arithmetic model. Pointer validity and physical meaning remain unresolved. This packet provides private pseudocode evidence without canonical admission or C implementation.
