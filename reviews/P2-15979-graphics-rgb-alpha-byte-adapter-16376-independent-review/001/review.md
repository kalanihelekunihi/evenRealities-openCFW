# Independent review 15979

Partial, accepted:false. Fresh decode replay passed for 24 bytes. Saves entry R0 and LR, loads three stacked bytes into R2/R1/R0 respectively, calls 4B15A6, then pops R1 and PC. Thus R1 is restored entry R0 while R0 is child result.

Child/global/hardware effects remain unqualified; no admission or gate change.
