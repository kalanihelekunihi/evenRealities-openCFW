# Error mask read-clear leaf, 0x4B128A..0x4B1298,14 bytes
R0=word[0x4B178C]; R1=word[R0]; R2=0
R0=word[R1+32]; word[R1+32]=R2; returnviaLR
No stack/calls. Returnsoldmask/R1context/R2zero. MOVS0setsN0Z1retainsC/V; subsequentloads/storedo notchangeflags. Loadclearisnotatomicandcanloseconcurrentupdates. Literalpointeroutsidecode.

Partial; accepted:false. Opaquechildren, architecturefaults, concurrentglobal/lifetime effects conditional; arithmeticwrap32 and orderedfreshloads retained. No C, admission, freeze, gates or physicalqualification.
