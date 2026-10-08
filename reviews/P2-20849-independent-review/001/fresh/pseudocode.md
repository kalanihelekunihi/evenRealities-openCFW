# Division zero handler immediate live register return

Partial/unaccepted;two instruction bytes. Locked instruction at4D2B98 is BXLR. No memoryaccess,stackallocation,flagwrite,call,trap or resultnormalization occurs. ReturnsliveR0..R3 andotherregisters unchanged.
MappeddivisionCCC4 tailbranches here forR2zero,R3zero;thus thatunsignedentry returns originalR1:R0 numerator andzeroR3:R2 divisor unchanged. AtentryCC60 no frame allocated onthatpath. Signedwrapper behavior stillincludesitsmappednormalizationafterthisreturn whereframed; do not inferlanguageexceptionsemantics. Bytes4D2B9A onward outside map. No C/freeze/completenessclaim.
