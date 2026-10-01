# Touch secondary interrupt initialization 38E0

Body38E0..3936 is86 instruction bytes, excluding NOP/pool. Copy original eight-byte descriptorB0F0 to local stack: signed halfword index8 and priorityword3. Call4C7C(200004EC); nonzero returns that status and restoresframe. Onzero call actualA2A8(stackdescriptor,3949), executing actualA214 and conditionallyA274. For nonnegative descriptor index, write1<<(index&31) toE000E280 andE000E100. Then call4AF4(200004EC), restoreframe and return its raw result. Signed-negative localbranches are present but original copieddescriptor hasindex8.

Six originalinstruction fixtures cover three controlled firststatuses and bothVTORstates. Two deeperhelpers are controlled; interruptregistrationhelpers executeactualinstructions. Exactpriority/vector/enablewrites, reachedcalls/rawreturn andSP are checked. Copieddescriptor mutation, physicalinterruptdispatch and deeperhelperbehavior remainunresolved. No canonicaladmission orCimplementation.
