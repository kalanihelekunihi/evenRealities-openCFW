# Floating output frame release and return

Partial/unaccepted; six instruction bytes 48360C..483612, continuation of the 80-byte frame entered at 483350. After output helper 48306C returns, add SP by 48, then load R4,R5,R6,R7,R8,R9,R10 and PC from eight consecutive words, postincrementing SP by 32. Total frame release 80 bytes. Preserve helper result R0 and its R1/R2/R3 effects; no extra result assignment. Saved PC controls return. The halfword 483612..483614 is excluded as adjacent padding pending data accounting. No C, freeze, whole coverage or equality claim.
