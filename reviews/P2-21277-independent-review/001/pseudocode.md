# Zero-count predicate and byte table mapping

Partial/unaccepted;88 instructionbytes482A5A..482AB2. Frameless482A5A freshbyte[entryR0+8];returnUXTB(1ifzeroelse0),BXLR. Separate482A6A usesUXTB(entryR0) comparisonwithoutinitiallytruncatingfullR0:255→R0=63;0→R0=0;otherwiseUXTB(R0)<138 (signedcomparison equivalentforbyte) freshlyloadliteral482AFC pointerR1,truncateR0=UXTB(R0),freshbyte[R1+R0]→R0,return.

Byte>=138: fullR0+=118mod2^32;freshliteral482AB8→R2 contextpointer;freshword[R2+48]→R1;zero→return0. OtherwiseR1=UXTB(currentR0),freshword[R2+40]→R3;unsignedR1>=R3→return0. Validindex independentlyreloadword[R2+48]→R1,thenR0=UXTB(R0),freshbyte[R1+R0]→R0,returnBXLR. Preservepointersecondread(no secondnullguard),freshfullwordbound,118additionbeforebytewrap and explicit255sentinel. No stackchanges,missingtableextent/meaningremainunresolved. Following482AB2..B4zeroexcluded. No C,freeze,wholecoverage or equalityclaim.
