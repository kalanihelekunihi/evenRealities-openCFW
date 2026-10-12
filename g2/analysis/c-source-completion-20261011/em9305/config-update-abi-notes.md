# Native update ABI notes

318670 preserves incoming R1, including on every early return. Complete C update translations must retain their own link pointer; C callers must not assume ABI preservation of a caller-saved argument register. The native caller ignores boolean R0.

311c0000 and331c0000 match pinned ARC MPYWHL register forms. Full update source must use named ISA operation; assembly operand/byte verification remains required.

3185e8 arguments are PHY at link480 and481, length bytes448 and444 respectively. Several native call sites load byte444 in a branch delay slot. st.as offset127/102 are word offsets508/408; ldh.as offset250 is byte500. add3 offset63 is byte504.

326d0c ends at326ed8; prior combined channel listing includes both326b00 and326d0c. Full native extended listing is saved separately.

Basic channel326c6a captures first31855c R0 intoR7, then326c78 passesR7 assecondcallR0. Current authentic native listing yields lowbyte-as-pointer flow; preserve in prepared C and keep admission/proof gate until independent byte/operand audit. No substitute same-link second call is authorized by evidence. MACWHL341d1083 exactly assembled asmacwhl r3,r12,r2; native writesACC0_LO fromprevioussum eachstep before MAC.
