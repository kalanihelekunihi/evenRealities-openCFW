# Buffer handle retirement candidate, 0x514D00..0x514D2C,44 bytes
PUSH R4,LR8; R4=entryR0
if R4==0:
 R0=8192; call4B127C(); R0=FFFFFFFF; restoreR4,PC; SP+=8; return
R0=word[R4+28]
if R0 signbit==1: goto514D22
call514026()
if R0 signbit==1: goto514D28
514D22: R0=FFFFFFFF; word[R4+28]=R0
514D28: R0=0; restoreR4,PC; SP+=8; return

Normalnonnullreturns0 evenifchildnegative; negativechildleaveshandlewordunchanged. Existingnegativehandle is rewrittenFFFFFFFF, anynonnegativechildresultretirestoFFFFFFFF. Retirementnameinferred, no childcompletion/resourcefreequalification. Childmayalterwordbeforelaterstore, originalregisterhandleinputpassedwithoutR4substitution.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
