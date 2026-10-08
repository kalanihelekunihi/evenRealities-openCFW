# Fresh status guards and buffer preparation 0x46A3D8..0x46A450

Partial/unaccepted; 120 instruction bytes. PUSH R4/LR then allocate 24 bytes, total frame 32. Call 43D0CE with live entry arguments. Test result bit 1 by LSLS 30 / BPL; if set, write literal word at 46AE78 to SP4 and 374 to SP0, call 43D574(4, literal46A834, literal46A830, literal46AE7C), with those extra stack arguments. Child contract unresolved.

Call 43D0CE again with live arguments. Test bit 0 by LSLS31/BMI; if clear, call 43D0CE a THIRD time and test this fresh result bit 2 by LSLS29/BPL. If second result bit0 or third result bit2 is set, load literal46AE80 into R1 and R2, then call 43CE9E(0x10000000,R1,R1,liveR3). Do not collapse the distinct status calls into one cached value.

At 46A420 store zero byte through address literal46B004. Call 469C98 with R0 zero and live R1/R2/R3. FULL child result nonzero branches to 46A4DE outside this component. If zero, R4=SP12, call 43C0E4(SP12,10,0,liveR3); repeat the entire argument setup and same call a SECOND time with fresh liveR3. Then call 469CAC(SP12,5,liveR2,liveR3); result/control flow continues at 46A450. Local buffer occupies SP12..21 within the allocated frame; initialization semantics remain a child contract rather than assumed memset. No C, freeze, or corpus completeness claim.
