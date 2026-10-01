# Touch descriptor validation 7D92

Body7D92..7DDE is76 instructionbytes; next7DDEentry excluded. Load seven descriptorwords atoffsets0,4,8,C,10,14,1C, in that order, before checking any. Returnzero iff allseven words are nonzero; otherwise returntwo. Checks continue after eachnullvalue; loadedpointervalues are notdereferenced. Restorefive-wordframe. No guard for nullincomingdescriptor exists.

128 originalinstruction fixtures cover everyzero/nonzero fieldcombination. Exactsevenloadsequence,return andSP matchindependentmodel. Nonzerofields useallones to confirm no pointeeaccess. Actualpointervalidity,nonnull semanticcontracts andconcurrency remainunresolved. No canonicaladmission orCimplementation.
