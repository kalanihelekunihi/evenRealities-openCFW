# Independent review P2-18527

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 50-byte span `0x460C76..0x460CA8`; instruction/reference manifests match. The entry is the completion branch selected after the signed counter comparison against a fresh halfword count. It performs three ordered global stores: word 1 through `0x46156C`; then freshly reloads source halfword at R5+4 and stores the zero-extended value through `0x461570`; finally writes word 1 through `0x460FB0`. Because the count reload follows the first store, aliasing can alter the value; the test count is not reused.

Next, it reads a word through `0x461574` and calls `0x4495E4` with R1=4 and live R2/R3. It then calls `0x4601EA` with the full previous child R0 and live R1-R3, no argument reset. Finally it sets R1=0, R0=low8(R4), calls `0x4604C2` with live R2/R3, discards the result, and joins external `0x460D54`. The alternate branch at `0x460CA8` is excluded.

Global pointee contracts and child behavior remain unresolved. No guards or broader routine claims are added. Partial/unaccepted only.
