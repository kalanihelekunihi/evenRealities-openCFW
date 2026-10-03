# Independent review 2271

**Result:** PASS_SCOPED.

Isolated replay regenerated all 514 fixtures. Source, body [0x9178,0x91F0), literal [0x91F0,0x9218), and listed artifact hashes match. Decoding confirms exact full-width comparisons against 5 and 11; the generic path and special paths write the listed words in order. Mode 5 zeroes 0x3020 then copies source words 0–4; mode 11 copies 0–5 to the first six locations then 6–10 to the tail; other tested modes use the generic mapping. R0/R4/R5/SP checks pass.

**Limits:** Fixture modes cover all low-byte values plus 0xFFFFFFFF and two source patterns, but do not exhaust high-word aliases. Independent nonaliasing buffers only; memory faults, physical register effects, and out-of-range pointers remain untested. No canonical admission.
