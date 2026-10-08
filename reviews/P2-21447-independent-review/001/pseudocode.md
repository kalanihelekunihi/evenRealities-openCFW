# Record reset, three copies, owner callback and list append prefix

Partial/unaccepted;100 instructionbytes4847C4..484828. PUSH R4/R5/R6/R7/R8/LR24B;R4=entry0record,R5=entry1parent,R6=entry2,R7=entry3source. 4846DE(R0=record);453604withrestoredentryR1/R2/R3fromresetwrapperandR0record→R8owner. Storeparentword[record+72];threeordered439C04copies16BfromsameR7sourceinto record+24,record+4,record+40. StorelowbyteR6atrecord+20.

Freshword[ownerR8+688]nonnull→R1=record,R0=owner,R2=freshword[owner+688],BLXR2(liveR3copyhelper-effects);nullskip. Freshword[owner+684]zero→48482Eunresolved;nonnullfreshreloadword[owner+684]R1,loopfreshword[node+76]R0compare0at484826;nextbranchpending484828. R1advanceentry484822reloadsword[node+76]. Preservecallbackbeforeheadrereadandthreecopyorder;owner/helpercontractsnotinferred. No C,freeze,wholecoverage or equalityclaim.
