# P2-19035 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468920–0x4689DE (190 bytes, 68 instructions); candidate and fresh instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

The case-15 and case-16 paths retain their separate diagnostic constants and fresh-mask sequences. Both explicitly narrow R6 in place before the exact-one test. Each enabled route loads a halfword through its own literal pointer and stores it at a different stack offset (SP+4 for case 15, SP+2 for case 16); these stores overlap prior diagnostic stack values as stated. The child receives the shown stack pointer and argument count. Branches to 0x468A28 leave this slice; no child contract is inferred.
