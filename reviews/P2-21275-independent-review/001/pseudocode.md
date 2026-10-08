# Byte dispatch stack-copy and global-load return paths

Partial/unaccepted;72 instructionbytes482A12..482A5A;continues48297C24-byteframe. Entry482A12 setsR0=SP4,R1=SP8,R2=3,call439BE4 liveR3;freshwordSP4→R0,branch482A56. Separate482A20 usesR0=SP4,R1=SP,R2=3,samehelper/liveR3,thenfreshwordSP4→R0 andbranch482A56. No copy semantics or upperbyteinitialization inferred; wordread includesallfourbytes followinghelpercall.

Entries482A2E/34/3A/40/46/4C/52 freshliteralpointer from482AE0/AE4/AE8/AEC/AF0/AF4/AF8 respectively intoR0,thenfreshword[pointer]→R0,branch/fallthrough482A56. CommonreturnADDSP16 bypasses savedscratchR0/R1/R2/R3,POP{R4,PC}8bytes,total24;retains currentR0 result. Preserve distinct entrytargets,livehelperR3 and freshwordreads. Next482A5A isseparatepredicateoutsidecandidate. No C,freeze,wholecoverage or equalityclaim.
