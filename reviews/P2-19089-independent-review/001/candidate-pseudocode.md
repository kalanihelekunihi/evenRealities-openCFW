# Predicate action paths 0x46928C..0x46931C

Partial/unaccepted;144 instruction bytes. Inherit32-byte frame and R5 saved context bool. Fresh0x43D0CE bit1 diagnostic: SP4=literal469B58, SP0=99, R3=literal469B4C, R2=literal469B38, R1=literal469B3C, R0=3 ->43D574. Independent freshbit0 or conditional third freshbit2: R2=literal469B5C, R1=R2, R0=0x0C000000, liveR3 ->43CE9E.

At4692CE call45A568 withliveargs; FULL result!=1 branches46931C. FULL1 setsR4=0 then calls44349C withliveargs. FULLresult1 setsR4=1 and calls464C36(0,0,0,0); otherwise skips first action. Bothpaths call4434B4 withrespective liveargs. FULLresult!=1 branches46931C. FULL1 andR4==0 calls464C36(0,0,0,0) then branches46931C. FULL1 andR4!=0 setsR0=500 andcalls454B4C withliveR1/R2/R3, then464C36(0,0,0,0). Fallthrough46931C.

Thus two full-one predicates can produce two ordered action calls, with child454B4C between them on the R4=1 path. No delay contract presumed fromconstant500; retain raw call. R4flag/R5bool and unchanged savedinputSP16 remain live for nextchunk. Freshread/call order preserved; no C, gate or runtimeclaim.
