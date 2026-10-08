# Stride256 four fresh guards and fourteen-argument diagnostics

Partial/unaccepted;202 instruction bytes; inherited64-byte frame. R4 base,R5 eligiblecount,R6 visitcount,R7 fullindex.
C316:R8=R4+(R7<<8)mod32. Freshbyte47zero→C3D8;elsefreshbyte48zero→C3D8;elsefreshword0==FFFFFFFF→C3D8;elseindependentlyreloadword0==0→C3D8. Only after allfourguards R5++mod32. Preserve both word reads, do not infer one cached value.
C340 query43D0CE bit1zero→C38E. Otherwise fresh unsignedbytes0..5 read ascending intoSP36,32,28,24,20,16;thenfreshbyte46→SP12,fullR7→SP8,literal47CB18→SP4,2139→SP0;43D574(4,literal47C548,literal47C544,literal47CB0C,2139,literal47CB18,fullR7,freshByte46,freshByte5,freshByte4,freshByte3,freshByte2,freshByte1,freshByte0). Fourteen arguments, allslots within40locals.
C38E freshquerybit0one→C39E;elseanotherquerybit2zero→C3D8. C39E independentlyreadbytes0..5ascending intoSP24,20,16,12,8,4;thenfreshbyte46→SP0;43CE9E(0x12000000,literal47CB1C,same,fullR7,freshByte46,freshByte5,freshByte4,freshByte3,freshByte2,freshByte1,freshByte0).
C3D8 incrementR6mod32 andR7mod32 unconditionally, including rejected records. C3DC signedfullR7<10→C316;elsependingC3E0. R6countsvisits,R5onlyeligible. No narrowing/cachedreads/C/freeze/completenessclaim.
