# Touch activation reset helpers

58F8..591C is36 instructionbytes, followed bymaskliteral. Freshlyload descriptor+4pointer/word8,ANDmask/store. Call5868(index,descriptor) forindices2,1,0 inthatorder, ignoringearlierreturns andreturninglastcall's rawR0. Restorefour-wordframe. 7E04..7E14 is16instructionbytes: freshlyload descriptor+4pointer,clearhalfwords2/16 andbytes6/1C inthatorder,return throughLR preservingincomingR0. No frame orhelpercalls occur there.

Twelve originalinstruction fixtures coverbothentries, threeoldpatterns andtwo controlled5868statuses. Exactcalls,writes,returns andSP matchindependentmodel. Pointervalidity,real5868behavior andconcurrency remainunresolved. No canonicaladmission orCimplementation.
