# Independent review P2-18485

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 114-byte function at `0x460450..0x4604C2`; instruction/reference manifests match. It allocates a 32-byte frame and reads the caller's fifth argument at SP+32 before output stores. Search uses eight entries with 52-byte stride and compares full word at entry+48 against the incoming key. Record base is reloaded on each search iteration. No child calls occur before a match.

On a match, it loads the output byte pointer from caller SP+32, writes entry word 0 through incoming R1, then calls `0x44A43C` with the entry+4 pointer and live R1-R3. It next calls `0x439BE4` with R0=retained incoming R2, R1=entry+4, R2=the previous child’s full R0, and live R3; that child result is discarded. It freshly loads entry+36 and stores through retained incoming R3. R6 is then replaced by `low32(52*R6)` and used to read byte entry+40, which is stored at the caller-provided byte pointer. The function returns zero on the matched path and `0xFFFFFFFF` when no entry matches.

The LDM return list is asymmetric: it restores saved R3 into R1, restores R4-R9 and PC, and does not restore R0/R2/R3. The result remains in R0, while R1 reflects the saved incoming R3. No string or copy contract is inferred for either child. Fresh record-base reloads, post-child field reads, and argument order were checked.

No source or gate changes; partial/unaccepted only.
