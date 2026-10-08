# Seven record setter getter helper entries

Partial/unaccepted;178instructionbytes,sevendistinctentries.
0x47B3AE:16-bytePUSH R3,R4,R5,LR;R4entryR0,R5=R4+135mod32;call439BE4(R5,entryR1,16,entryR3);then479B74(R4,liveargs),then47B730(R4,liveargsafterfirst),noguards. POP R0,R4,R5,PCreturnsfullsavedentryR3,nothelperresult.
0x47B3CC:8-bytePUSH R4,LR;R4entryR0,storeLOW8entryR1atR4+134;call479B74(R4,liveargs),then47B730(R4,liveargsafterfirst);POP R4,PCreturnslivesecondresult.
0x47B3E2:8-bytePUSH R4,LR;R4entryR0,narrowR1LOW16;R0=R4+(R1<<1)mod32;storeLOW16entryR2halfword[R0+108]. Call4BB05Awithliveargs,narrowresultR0LOW8,call4BAD26withliveargs. Fullresultzero skips0x47B40Areturnszero. Nonzero calls479B74(R4,liveargs),then47B730(R4,liveargsafterfirst);POP R4,PCreturnslivesecondresult. No indexboundcheck.
0x47B40C:frameless;freshbyte[entryR0+132]R3,storebyte[entryR1],thenR0+=133mod32,storefullR0word[entryR2],BX LRreturnsadjustedpointer. Preserveorderedwritesunderaliasing,nopointerguards.
0x47B418:8-bytePUSH R4,LR;R3fullentryR2. R3zero skips0x47B436withR0entryR0. OtherwiseentryR0zero skipswithzero. BothnonnullstoreLOW8entryR1byte[R0+132],R2one,R4=R0+133mod32,R1=R3,R0=R4;call439BE4(R4,entryR2,1,entryR2fullalsoinR3). POP R4,PCreturnslivehelperresult,orskipentryR0. No otherguards.
0x47B438:frameless;fullentryR0nonzero storesLOW8entryR1byte[R0+132]andreturnsunchangedfullR0. EntryR0zero loadsR0literal47BC10,R2=10;whileLOW8R2nonzero storeLOW8R1byte[R0+132],decrementR2,advanceR0by200mod32. ReturnfinalR0=literalbase+2000mod32aftertenstores. No47/48guards.
0x47B45A:framelessloadR0literal47BC14thenBX LR,noothermemoryread. Preservehelperlivearguments,separateentries,andframe/returndifferences. No C,freezeorwholecoverageclaim.
