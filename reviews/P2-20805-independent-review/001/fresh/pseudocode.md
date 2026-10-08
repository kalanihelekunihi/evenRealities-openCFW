# Counter reset diagnostic and table loop initialization

Partial/unaccepted;86 instruction bytes. At47C164 PUSH R0..R6,LR creates32-byte frame. Query43D0CE with live arguments; bit1zero skipsC18C. Otherwise SP4=literal47CAE8,SP0=2091;43D574(4,literal47C548,literal47C544,literal47CAEC,2091,literal47CAE8).
C18C query status afresh:bit0one→C19C;otherwisequeryagain,bit2zero→C1AA. C19C:43CE9E(0x10000000,literal47CAF0,same,liveR3). No explicit R3 assignment in mask setup.
C1AA:R4=literal47C558;store word[R4]=0. ThenR5=literal47CAF4,R6=0;branch pending47C230. Reset precedes table loop, including zero eligible records. SP0/SP4 logger writes overwrite saved entryR0/R1. No return inferred in this prefix. No C/freeze/completeness claim.
