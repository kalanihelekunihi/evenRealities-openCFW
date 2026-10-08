# Unsigned handoff and fixed/general floating handlers

Partial/unaccepted;184 instructionbytes483DE0..483E98 continuing88-byteframe483960. SharedunsignedvalueR0: orderedflagsR8SP20,widthR7SP16,precisionR4SP12,radixR10SP8,sign0SP4,valueR0SP0;reloadR3SP44,R2R6,R1SP40,R0R5;call48320A,R6=result. Common483E00 freshcursorSP48incrementstore,branch48398E.

Fixedentry483E08 freshcursorbyteF70→R8|=32,otherwiseunchanged. AlignedvarargaddressR0=(R9+7)&~7wrap,full8Bload d0[R0],R9=R0+8. OrderedflagsR8SP8,widthR7SP4,precisionR4SP0;reloadR3SP44,R2R6,R1SP40,R0R5;call483350,R6=result;freshcursorincrementstore,branch48398E.

General/scientificentry483E42 freshcursorbyteg103 or independentlyfreshG71→R8|=2048. FreshbyteE69 or independentlyfreshG71→R8|=32. Samealigned8Bvarargload/advance andstackflags,width,precision;reloadcallbackargs,call48364C;R6=result;freshcursorincrementstore,branch48398E. Exact rereads,stackorder andhelperselection retained. No C,freeze,wholecoverage or equalityclaim.
