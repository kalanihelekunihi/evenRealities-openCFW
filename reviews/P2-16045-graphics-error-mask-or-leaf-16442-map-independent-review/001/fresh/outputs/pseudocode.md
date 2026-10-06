# Error mask OR leaf, 0x4B127C..0x4B128A,14 bytes
R1=word[0x4B178C]; R1=word[R1]; R2=word[R1+32]
R0=entryR0|R2; word[R1+32]=R0; returnviaLR
No stack/calls; R0newmask,R1contextpointer,R2oldmask. ORRSsetsN/ZretainsC/V. This helper records bits and normally RETURNS; nottrap/logcall. Unmappedcontext/fault conditions remain. Literalpointerdataoutsidecode. UpdateisloadORstore, notatomicRMW.

Partial; accepted:false. Opaquechildren, architecturefaults, concurrentglobal/lifetime effects conditional; arithmeticwrap32 and orderedfreshloads retained. No C, admission, freeze, gates or physicalqualification.
