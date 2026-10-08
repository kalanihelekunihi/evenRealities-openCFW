# Independent review — P2-21467

Status: partial; accepted: false.

Fresh replay passed for the exact 148-byte span, and regenerated instruction/reference records match the candidate. The first fresh bit-0 test selects 48834C(18,2) or 488290(18 with R1 live from the preceding helper); result is then passed as R1 to 4D48AA(object+76, result), followed by the 32767/4D4A6E call.

For each dimension path the code freshly loads object+44, performs 32-bit MULS by 7 or 5, adds 80 with 32-bit wrap, and executes SDIV by 160. It uses signed q<2 to choose one; otherwise it repeats the load/multiply/add/divide into R1 before the object helper call. The wrapper at 0x484A26 returns saved entry R3 in R0 and its result is ignored. The final 4D48C4 call uses object+76 and 102. Frame remains open at the slice boundary.

External helper contracts and the following continuation are unresolved. Review remains partial/unaccepted.
