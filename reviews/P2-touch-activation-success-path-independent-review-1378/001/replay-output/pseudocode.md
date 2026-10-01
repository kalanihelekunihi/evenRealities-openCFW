# Touch activation success path 4AF4

On zero4ABE status, call5CA2,7BB8,5C7A withdescriptor, OR their rawresults into accumulatedstatus. ActualA6C0 divides descriptorword0's firstword by1000000. Call5FA4(1000000,quotient,5), retaining its return as retrycounter. Repeatedly call5C8E(descriptor): zero ends polling; nonzero with counterzero sets accumulatedstatus4 andends; otherwise decrementcounter andretry. Thus atmostcounter+1 polls occur, and zero on the last permitted poll succeeds.

Set contextbyte76one; call6AC0(1,descriptor),ignore result. Call5C02(index,descriptor) forindices0,1,2,ignore eachreturn. Continue common cleanup4F54/4E1C and freshperipheralbit15clear, then returnaccumulatedstatus. Six-word frame restored. Full localbody4AF4..4BA0 is172instructionbytes, followed byliterals.

Eighteen originalinstruction fixtures vary three retrybudgets, three failureprefixlengths andtworegisterpatterns. All deeperhelpers arecontrolled; unsigneddivision executesdirectly. Exactcallsequence,budgetarguments,cleanupwrites,flag,result andSP arechecked. Physicalpolltiming,helperbehavior andconcurrentmutation remainunresolved. No canonicaladmission orCimplementation.
