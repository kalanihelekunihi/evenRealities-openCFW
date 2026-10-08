# Integer flags and signed wide argument magnitude prefix

Partial/unaccepted;130 instructionbytes483BDE..483C60,continuation88-byteframe483960. UppercaseentryR8|=32. Freshcursorbyte i thenfreshbyte d; neither clearsflags12plus/space. IfR8bit10set,logicalshiftR8right1thenleft1 clearsbit0. Freshcursorbyte i or freshbyte d→483C16;others→483D1A unresolved. Signedentrybit9clear→483C7C;set roundsargpointerR9up8using(R9+7)&~7wrapping,loadsR2low/R3high,nextR9=aligned+8. Signedhighnegative setsR12=1else0.

Compare signed64pair against positive1: R0=1,R1=0; highsigned<0→negate,>0→keep,high0andunsignedlow<1→negate,elsekeep. Negate lowR2 viaNEGS thenR3=R3-(R3<<1)-(1-carry) viaSBCS, yields two-word modular negation (zero also negated). Orderedstack flagsR8SP32,widthR7SP28,precisionR4SP24,radixpairR10/0SP16/20. Fallthrough483C60 remainingargsunresolved. Preserve original sign separately,8alignment, lowcarry and flags adjustment; no C,freeze,wholecoverage or equalityclaim.
