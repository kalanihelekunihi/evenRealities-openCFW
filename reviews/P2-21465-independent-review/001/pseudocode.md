# Fourth three-byte field and paired object setup

Partial/unaccepted. Exact 142 instruction bytes 484B16..484BA4, continuing the 32-byte frame at 484A98, with object in R4. Fresh byte[object+36] bit0 selects field+57 value: set calls 44104C(word at literal485484,live other registers); clear calls 4882D2(18,2,live R2/R3). Store result at SP0 then call 439BE4(object+57,SP,3). This overwrites saved entry R1.

Call 488198(object+388) then 488198(object+400), other registers live. Load R5 from literal485488 and R6 from literal48548C. Set SP4=0 and SP0=70, R3=80,R2=R6,R1=R5,R0=object+868; call 482950. Then SP4=0,SP0=0 and call 482950(object+888,R5,R6,80). Both stack words overwrite saved entry R1/R2; retain exact stack arguments without inferring their semantics.

Call 4D4ABC(object+388,object+868,live R2/R3), then 4D4ABC(object+400,object+888,live R2/R3). Finally call 488198(object+76,live other registers). Prefix ends with frame open; next flag selection and eventual return are separate. Literal bytes are in references.json; helper contracts unresolved. No C, freeze, whole coverage or equality claim.
