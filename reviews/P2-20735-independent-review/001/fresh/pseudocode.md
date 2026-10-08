# Byte194 setter and forty-two helper saved slot

Partial/unaccepted;36instructionbytes,twoentries. Entry0x47B488framelessstoreLOW8entryR1byte[entryR0+194],BX LRreturnsunchangedfullentryR0. No guards.
Entry0x47B48E PUSH R3,R4,R5,LR16-frame;R4fullentryR0,R5=R4+152mod32,R2=42,R0=R5;call439BE4(R5,entryR1,42,entryR3). Then479B74(R4,liveargs),then47B730(R4,liveargsafterfirst),withoutresultguard. POP R0,R4,R5,PCreturnsfullsavedentryR3,nothelperresult. No C,freezeorcompletenessclaim.
