# Fraction digits, postdecrement zero fill and separator

Partial/unaccepted;96 instructionbytes4834FC..48355C,continues48335080-byteframe. EntryunsignedR8>=32→48353C. OtherwiseR7--mod;R9=10,R10=UDIV(R4,10),R9=R4-10*R10mod,add48;R10=SP16buffer,storelowbyteR9[buffer+R8];R8++;R9=10,R4=UDIV(R4,10);nonzeroR4repeat4834FC,zero→48353C. Digitloopatleastonewriteifspace,evenfractionR4zero;precisionR7decrementswithoutguard.

Zero-filltest48353C unsignedR8>=32→48354A withoutR7decrement. OtherwiseR4=oldR7,R7=R4-1mod;oldR4!=0→48352E:writeASCII48atSP16+R8,R8++andretest. OldR7==0stillsetsR7=FFFFFFFFbutwritesnothing. At48354A count>=32→unresolved48355C;space→R4=46,R7=SP16,storeASCII'.'atbuffer+R8,R8++then48355C. Preservepostdecrementevenzero,bufferbound32onallwrites and precisionversusfractionterminationdistinct;no inventedclamp. No C,freeze,wholecoverage or equalityclaim.
