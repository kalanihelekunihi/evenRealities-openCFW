# Wide integer handoff and signed long/byte/halfword paths

Partial/unaccepted;128 instructionbytes483C60..483CE0,continuation88-byteframe483960. WidepathUXTB R12sign→SP8;R2/R3magnitude→SP0/4;SP12 gap unwritten in this path. ReloadR3SP44entry2,R2R6position,R1SP40entry1,R0R5callback;48329C;R6=result,branch483E00unresolved. Previous flags/width/precision/radixpairSP32/28/24/16/20 retained.

483C7Cflagsbit8clear→483CBC. Set loadword[R9]R0,R9+=4;signR1=1ifsignedR0negativeelse0; signedR0<1negateswrapping,elsekeeps. Ordered flagsSP20,widthSP16,precisionSP12,radixR10SP8,UXTBsignSP4,magnitudeSP0. ReloadcallbackargsR3SP44,R2R6,R1SP40,R0R5;call48320A,R6=result,branch483E00.

483CBCbit6set loadfullwordvararg,nextR9+=4,UXTB R0 (unsigned byte even within signed conversion),branch483CE8 unresolved. Elsebit7set loadfullword,nextR9+=4,SXTH R0,branch483CE8. Bit7clear→483CE0unresolved. Preserve precedencebit6beforebit7 and byte zero extension exactly. No C,freeze,wholecoverage or equalityclaim.
