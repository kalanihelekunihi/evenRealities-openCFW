# Next native dispatch 330ce0

Direct authenticated ARC little endian DSP listing identifies complete 330ce0..330e10. Existing selected address-copy304604, forward memcpy332fc4, event allocate32e454 and send30ae90 cover all children.

Type4 allocates event14,length4, bytes[1]=12,[0]=1,[2]=32,[3]=input3; send event-2 return1, allocnull0.

Type2 captures input18 then maskword8056f8. If input18!=255, requires mask bit10, featurebyte8056ef bit5 and count805718 below config805cacbyte14. These rejection/alloc-failure paths return1 despite no event (native R17 delayed initialization), distinct from legacy path. Allocate62,18; bytes0=11,1=1,2=input10,3=input11; copy6 addressinput12 toevent4, byte10=input18, copy6 input19 toevent11,byte17=input9; increment fresh count805718, send event-2 return1.

Legacy input18==255 requires maskbit1, featurebit5, countbelow configbyte14; rejection0. Allocate62, low8(input8+12), null0. bytes0=2,1=1,2=input10,3=input11; copyinput12address toevent4; event10=freshinput8, memcpy(event11,inputword4,freshinput8); freshinput8 determines tail event11+length=input9; fresh countincrement; send return1. Unsupported type returns0.

This note is a next-source contract, not compiled implementation or runtime proof.
