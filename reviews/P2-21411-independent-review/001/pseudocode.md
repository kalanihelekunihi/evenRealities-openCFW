# Multi-object initialization tail and global resource wrappers

Partial/unaccepted;60 instructionbytes484308..484344. Continuation4842E616Bframe,R2retained1024: R1=wordliteral48437C,R0=R5thirdobject;48413C. Call4840C8withprevioushelperregistereffects;byte[R4secondobject+24]=0 thenbyte[R5thirdobject+24]=0. POPR0(savedentryR3),R4/R5/PC16B;returnR0isentryR3,notlasthelperresult.

48431E8BframePUSHR7/LR;R1=entry0,R0=wordliteral48436Cglobalobject;484180;POPR1(savedR7)/PC,helperR0resultretained. 48432A8Bframe:R2=entry1,R1=entry0,R0=sameglobal;484234;POPR1/PCretainshelperR0. 4843388Bframe:R1=entry0,R0=sameglobal;48429E;POPR0(savedR7)/PC overrideshelperresultwithentryR7. ExactPOPaliasesandcallargs retained. No C,freeze,wholecoverage or equalityclaim.
