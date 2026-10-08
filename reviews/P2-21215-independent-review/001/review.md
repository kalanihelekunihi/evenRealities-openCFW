# P2-21215 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481D7A..0x481DE8 (110 bytes); instruction and literal-reference outputs match. The raw low/high word reloads feed the exact shifted combined value and ASR tests. The first special predicate checks both derived components and branches to separate ADR source addresses based on the unsigned conversion range. The other path independently reloads both words, but its second predicate checks the derived high fraction only; the low-word fraction is not part of that test. Both special branches prepare a three-byte copy call to 0x439BE4 with destination R12, source literal, and length 3; its full return is ignored. No IEEE special-value contract or helper copy semantics are inferred.
