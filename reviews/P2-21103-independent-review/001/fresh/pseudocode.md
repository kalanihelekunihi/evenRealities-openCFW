# Frameless inverted bit thirty-one byte output

Partial/unaccepted;16 instruction bytes4800E4..4800F4. R1=literal4801F8pointer;freshword[R1] shiftedright31 thenXOR1→normalized inversebit31. StorebyteatfullentryR0pointer,thenexplicitR0=0,BX LR. No nullguard;R1retainsnormalizedoutput,R2/R3unchanged. Singlewordread;outputaliasdoesnotcauseadditionalread. No stack/helper/PRIMASKoperations. Pointedownership/MMIO/C/freeze/fullcoverage unresolved/notclaimed.
