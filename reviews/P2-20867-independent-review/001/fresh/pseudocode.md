# Fresh halfword six-way message dispatch

Partial/unaccepted;38instructionbytes;inherited40frame,R6=entryR1bufferpointer,R4inheritedzero. Freshunsignedhalfword[R6]→R0 exactlyonce. Compare1:equal→pendingD08C,unsignedless(0)→pendingD7B6. Compare3:equal→pendingD516,unsignedless(2)→pendingD20E. Compare5:equal→pendingD71C,unsignedless(4)→pendingD5B8. Compare6:equal→pendingD642;otherwiseunconditionalD7B6.
Thussixexplicitselectors1..6;0and7..65535defaultD7B6. No halfwordreload,masking or signedcomparison. No length/pointerguardinthisslice; do notinfercasebehaviororoutcomeuntiltargetsrecovered. No stackwrite/call inthisdispatch. No C/freeze/completenessclaim.
