# Touch 98F4 configuration programming

Body98F4..9AAA has438 instruction bytes, excluding NOP/literals. Guard behavior is separately recorded in1343. Valid paths derive control from boolean config bytes5/8 at bits16/8, store base+0, then derive base+60 from low four bits(width16-1), bit11 iff byte6zero, low byte((width12-1)<<4), and mode<<30. Freshly read control and maskFFFF3FFF. Store byte7 boolean atbit31 tobase+80.

If mode differs from1 and byte9nonzero, store307 atbase+300 and2A0003 at+70; otherwise107 and2A1013. Store15 iff byte1nonzero at+304; store lowbyte(byte3<<1) OR byte4<<16 at+310. Store107 at+200 and8 iff byte2nonzero otherwise1 at+204. Clear+EC8,+E88,+FC8,+F88,+F08. At+F48 store0 for mode2 otherwise1D1, freshly read it and OR03000000 iff byte7nonzero and mode differs from2, then store again.

Context receives byte1 at0, byte2 at1, halfword config+20 at+50, boolean(mode!=2 && byte7!=0) at2 and10000000 at4. Clear context word offsets8,18,20,40,3C,30,2C,44,48,4C. Returnzero and restoreframe. Null/error and guard paths are described in1343; continuation afterBKPT remains unresolved.

Receipt-derived original-instruction fixtures vary all seven boolean fields, all three modes and widths0/1/16, excluding the explicitly invalid simultaneous byte1/5 combination. Exact ordered peripheral/context writes match the independent model with no helper substitutions. Other signed-byte values and distinct width pairs are not fixture-covered. Physical peripheral behavior, concurrency and global ownership remain unresolved. No canonical admission or C implementation.
