# Record owner list insertion tail and lazy resource creation prefix

Partial/unaccepted;74 instructionbytes484828..484872. Continuing4847C424Bframe: pendingnextwordcomparisonNE→484822advance;EQword[tailR1+76]=recordR4;branch484832. Emptyownerheadpathword[ownerR8+684]=recordR4. POP R4/R5/R6/R7/R8/PC24B retainsR0lastnextword0onappendorheadcheck0, notrecord explicitly.

New484836PUSHentryR3/R4/R5/R6/R7/LR24B;R4=entry0record;freshword[record]R0nonnull→independentword[record]reload thenword[resource+16]R0,branch4848B0unresolved. NullR0=record+4;451598→R6;R0=record+4;4515A4→R7. R1=byte[record+20],R0=R6;48AAD8→R5;R5*=R7mod32. R3=0,R2=freshbyte[record+20],R1=R7,R0=R6;48AFFA;storeR0word[record]. Fallthrough484872unresolved. Exactrepeatedpointer/byte loadsandmultiplicationretained; dimensional/helpertypesunknown. No C,freeze,wholecoverage or equalityclaim.
