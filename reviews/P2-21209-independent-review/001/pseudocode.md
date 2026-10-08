# Pointer zero extension and count-store policy/modifier dispatch

Partial/unaccepted;144 instruction bytes481BB8..481C48. Continues481836232frame. Pointerconversion:loadargcursor[R9]→R1,loadwordpostincrement4→R0,storeadvancedcursor;R4=R0(BIC0),R1=0,R5=0(BICFFFFFFFF);STRD R4,R5→SP8/SP12 zeroextended64bitvalue. R3=SP72→SP20;R1='x'(120);branch482476 unresolvedintegerconversion.

Countconversion481BDC:loadpointerSP172 thenbyte[pointer+1]policy;nonzero→R4FFFFFFFF,ADR R0=4826B4,branch481A4E existingdiagnostichelperpath. Zero:reloadmodifierbyteSP66,dispatchb98→481CB6,h104→481C28,j106→481C7C,l108→481C0E,q113→481C94,t116→481C62,z122→481C48,other→481CD4. Otherdestinationsunresolvedhere.

Modifierl:loadargcursor,freshpointerwordpostincrement4,storecursor;nonnull→481CEC unresolvedwordstore;null→R4FFFFFFFF,ADR R0=4826CC,branch481A4E. Modifierh:samepointerfetch/cursorupdate;null→sameADR4826CC diagnosticpath;nonnull→freshwordSP52counter,STRHlow16counter[targetpointer],branch4824AC. Policyrejectpathconsumesnoargument;nullargumentpathsadvancecursorbeforediagnostic. No inferredstandardprintfsemantics, C/freeze/fullcoverage/equality claim.
