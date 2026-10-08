# Decimal leading-zero trim, retained digit and carry scan

Partial/unaccepted;124 instruction bytes482040..4820BC. Continues481836232frame,R6cursor,R8lowercaseconversion. R6=cursor-SP133mod2^32,R4=SP133. Whilefreshbyte[R4]==48:reloadSP0exponentdecrement1store;R6--;R4++;repeat. No encodedlength/boundcheckinleadingzero scan. Retainedcountbase: R8f102→wordSP0+1;elseR8e101→1;other→0. AddprecisionwordSP56mod2^32→R0. IfsignedR6<R0,R0=R6-1;negativeR0→4820BC. Note strictLTclamp differsfromordinarymin.

IfsignedR0<R6,freshbyte[R4+R0]>52signed(ASCII'4')→R1=57('9');elseR1=48('0'). R0>=R6→R1=48. R2=R0,R3=R4-1,R5=R3+R2. Backwardscan:freshbyte[R5]postdecrement→R6;R2--;ifbyte==R1 R0--repeat. R1==57→freshbyte[R4+R2]increment1storelow8. IfsignedR2negative:reloadSP0exponent+1store,R4=R3(previousbase-1),R0++;elseunchanged. Joins4820BC. Preservetrim/scanunboundedencodedreads,sentineldependency,overflowandorderedwrites;no ties-to-even substitution,C/freeze/fullcoverage/equality claim.
