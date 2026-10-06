# Two-child adapter and lazy initializer46015A..46018E
Partial;unaccepted.52 instructionbytes,two completefunctions.
46015A PUSH{R4,R5,R6,LR},frame16. R4=incomingR0,R5=incomingR1,R6=incomingR2. ResetR2=R6,R1=R5,R0=R4 inthatorder;4411F2 liveR3. ResetR2=R6,R1=R5,R0=R4 again;441200 livepreviouschildR3. FirstchildR0discarded;460176POP{R4,R5,R6,PC}restoresoriginals/LR,returnsfullsecondchildR0. No guardsorlocalmemoryaccess beyondstack;childcontracts unresolved.
460178 PUSH{R4,LR},frame8;R4=wordliteral46061C globaladdress;R0=freshword[R4];fullnonnull→46018CPOP preservingloadedR0. Fullzero:R0=0;44971C with liveincomingR1/R2/R3;word[retainedR4]=fullchildR0,withoutreloadorvalidation;46018CPOP{R4,PC}restoreoriginalR4/LR,returnchildR0. Thisinitialization repeats on futurecalls ifchildreturnszero. No lock/synchronization inspan;donotassume allocationcontract. Next46018Eexcluded.
No C,gate/source admission,whole coverage or simulator/hardware proof.
