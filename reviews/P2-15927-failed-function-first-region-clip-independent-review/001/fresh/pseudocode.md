# First region clip continuation, 0x540264..0x5402C8

Partial; accepted:false.100bytes continuation, frame224active. Ordered wrapped expressions and childcalls:

word[SP+20]=word[SP+52]
R0=freshword[SP+52];R0=u32(R0-R9);R0=u32(R0+1);word[SP+12]=R0
word[SP+16]=word[SP+48]
R0=freshword[SP+48];R0=u32(R9+R0);R0=u32(R0-1);word[SP+24]=R0
R1=SP+12;R0=SP+60;call540024()
R0=word[SP+12]
if s32(R10)<s32(R0):R0=freshword[SP+12]
else:R0=R10
word[SP+60]=R0
R0=word[SP+24]
if s32(R0)<s32(R11):R0=freshword[SP+24]
else:R0=R11
word[SP+72]=R0
R2=u32(R4+56);R1=SP+60;R0=SP+28;call450BCC()
if R0==0:branch540308
R2=R8;R1=SP+92;R0=SP+28;call450F28()
if R0!=0:branch540308
R0=SP+112;call561810()
continue5402C8

Max/min comparisons signed; repeatedloadsaftercompare retained, not collapsed into immutableminmax. Copy/clipping/geometry initialization names inference only; opaque childmemoryeffects and exactcontracts unresolved. Both skipbranches joinoutsidepacket at540308. No fullfunction return/ABI or physicaldrawing/alias/fault/concurrency qualification, no C/gates.
