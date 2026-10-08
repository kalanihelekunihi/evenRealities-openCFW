# Ordered helper pair and three-byte field initialization prefix

Partial/unaccepted. Exact 152-byte span 484A7E..484B16. Wrapper at 484A7E saves R3,R4,R5,LR (16B), retains entry R0/R1 in R4/R5, calls 4D4892 then 4D489E with R0=R4,R1=R5 before each and live R2/R3; POP R0 returns saved entry R3. Zero halfword 484A96..484A98 is inter-function data/padding.

484A98 opens a 32B frame saving entry R1..R7 and LR; R4 retains object. For each field, freshly read object byte+36 bit0 to select the value helper, store returned R0 at SP0 (overwriting saved entry R1), then call 439BE4(destination,SP,3), copying the low three bytes of the stack word on this little-endian image; copy-helper full contract remains unresolved.

Field +48: bit0 set calls 44104C with R0=word at literal48547C; bit0 clear calls 4882D2(18,4,live R2,R3). Field +51: bit0 set calls 4882D2(18,5,live R2,R3); clear calls 48834C(18,4,live R2,R3). Field +54: bit0 set calls 44104C with R0=word at literal485480; clear calls 441094 with R0 still zero from the preceding flag shift, and other registers live from prior copy. Each copy sets R2=3 and R1=SP. Prefix ends after third copy, frame still open; continuation and final return remain separate. Referenced literal words recorded in references.json. No C, freeze, whole coverage or equality claim.
