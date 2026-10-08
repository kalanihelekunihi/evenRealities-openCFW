# Unsigned wide/long output and byte/halfword extraction

Partial/unaccepted;128 instructionbytes483D60..483DE0 continuing88-byteframe483960. WidepairR0/R1retainedfromalignedvarargload: orderedwidthR7SP28,precisionR4SP24,R11=0,radixpairR10/R11SP16/20,sign0SP8,valuepairR0/R1SP0/4. FlagsSP32alreadywritten;SP12gapnotwritten. ReloadR3SP44,R2R6,R1SP40,R0R5;48329C;R6=result;branch483E00.

483D84flagsbit8clear→483DB4;setloadfullwordR0[R9],R9+=4;orderedflagsR8SP20,widthR7SP16,precisionR4SP12,radixR10SP8,sign0SP4,valueR0SP0. ReloadcallbackargsR3SP44/R2R6/R1SP40/R0R5;48320A;R6=result;branch483E00. 483DB4flagsbit6setloadword,nextR9+=4,UXTBvalue,branch483DE0. Elsebit7setloadword,nextR9+=4,UXTHvalue,branch483DE0. Elsefullwordload,nextR9+=4,fallthrough483DE0 unresolved. Allnarrowloadsconsume4B,bit6precedence;no sign extension. No C,freeze,wholecoverage or equalityclaim.
