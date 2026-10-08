# Signed word output, recursive V and unsigned wide prefix

Partial/unaccepted;128 instructionbytes483CE0..483D60,continuation88-byteframe483960. OrdinarysignedloadwordR0[R9],R9+=4. Shared483CE8 signednegativeR0setsR1=1else0; signedR0<1negateswrapelsekeeps. OrderedstackflagsR8SP20,widthR7SP16,precisionR4SP12,radixR10SP8,UXTBsignR1SP4,magnitudeR0SP0. ReloadR3SP44,R2R6,R1SP40,R0R5;48320A;R6=result,branch483E00.

Unsignedentry483D1A freshSP48cursorbytecompare86V;NE483D46. VloadpointerR0[R9],R9+=4;R1=word[R0+4],thenword[R1]→SP0recursivefirststackarg;R3=word[R0];R2=freshSP44-R6wrap;R0=freshSP40,R1=R0+R6wrap;R0=R5callback;call483960recursively;R6+=resultwrap;branch483E00. Exactpointerindirections and changedcontext/thirdarg retained without assuming printf ABI abstractions.

483D46flagsbit9clear→483D84;setR2=(R9+7)&~7wrap,loadpairR0/R1[R2],nextR9=R2+8;storeflagsR8SP32. Fallthrough483D60remainingargsunresolved. No C,freeze,wholecoverage or equalityclaim.
