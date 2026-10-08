# Remaining records and return 0x469F16..0x469FA2

Partial/unaccepted;140instructionbytes. Inherit56frame andFULLoriginalselectorR0. FULL10: orderedbytewrites0,10,0,0,0,0 atSP16..21;call464BB2(34,SP16,6,0) ->469F9E. FULLnot10thencompare72: equalorderedbytes0,72,0,0,0,0 atSP8..13;call464BB2(34,SP8,6,0) ->469F9E. Not72compare73: equalorderedbytes0,73,0,0,0,0 atSP0..5;call464BB2(34,SP,6,0),fallthroughreturn. Unequal73branchesreturnwithR0FULLoriginalselectorunchanged (afterguardR2overwrite); no blanketzero/defaultbool.

Shared469F9E ADDSP52 skips48localsandsavedR7word;POPPC4 restores56frame. R0live: guardnonzeroarm0, recognizedselectorschildFULLresult, defaultoriginalselector. R7nevermodifieddirectlyandnotrestoredviaPOP. R1/R2/R3childclobbersremainlive. NextPUSH469FA2excluded. Preserveorderedfullselectorchecksanddistinctcasebuffers. No C,freezeorchildcontractclaim.
