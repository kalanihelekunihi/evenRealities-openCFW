# Independent review 2909

**PASS_SCOPED**; `accepted` remains false.

The authenticated image hash, body [42AEF0,42B010) digest, and candidate artifact hashes match. Isolated Capstone decode replay into a fresh directory passed, accounting for all 107 instructions in the 288-byte body. PC-relative literals resolve to the recorded MMIO, entry-array, selection-mask, and output-flag addresses. The instruction flow supports the stated early guards, query call and two separate low-nibble reads; the row loop checks entry active bit and selected mask, then performs fresh UBFX kind reads for its threshold tests. UBFX zero-extends the 9-bit kind, so the subsequent signed-negative branch is unreachable for that value. The stated compact kind intervals (0–5, 19–24, 256–479) describe stable values, not a substitute for the distinct volatile reads. This is static pseudocode only; no dynamic read/alias/concurrency or physical-hardware claim. accepted:false.

Candidate receipt SHA-256: `d89f98901c50e3ed306b2ef351e65937d38fdfcd7f655534a2847df1999f759a`.
