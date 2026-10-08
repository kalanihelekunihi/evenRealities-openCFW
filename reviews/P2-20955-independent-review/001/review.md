# P2-20955 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 134 bytes at 0x47E1EC..0x47E272. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The first entry returns -2 when its fresh flag byte is zero. Otherwise it reads the first global word; zero returns 0. A nonzero first word leads to an independent second global read and unsigned comparison against 33. At or above 33, the E06A cleanup call precedes clears of both global words; all normal paths return zero, with the epilogue placing the saved entry R3 into R1. The second wrapper freshly tests its handle word, reloads it for 474910 only when nonzero, discards that call result, and returns saved entry R7 in R0.

The initializer entry tests its global word. Zero triggers two local stack-slot writes that overwrite saved entry R3/R2, followed by the 47E712 call with 2000 and zero arguments. Its full result is stored globally and freshly reloaded. If zero, the code calls 5FA0A4, prepares `(R0=0,R1=FFFFFFFF)`, performs the literal store to address FFFFFFFF, and branches to itself if that store completes. This preserves the observed instruction path without assuming fault behavior. Nonzero instead calls 48EAC8 and 47DD92 before POP returns SP0/SP4 into R0/R1. The initial-nonzero bypass returns the saved entry slots.

External helper and memory-fault semantics remain unresolved. Status remains partial/unaccepted; no source or gate files changed.
