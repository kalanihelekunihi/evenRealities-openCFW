# Independent review 1775: scoped pass

The three pinned bodies are 7F6C..7F78 (12 bytes/5 instructions), 7F78..7F7C (4/2), and 7F7C..7F9C (32/14); the following 7F9C literal is excluded. Independent replay reproduces all 80 equality/mismatch cases, including width wrap, full-word comparisons, SP restoration and return values. The instruction flow confirms 7F78 loads the word at R0; 7F6C passes R0+1 and (R1−4) modulo 2^32 to 7E68 and returns its result; 7F7C compares full 32-bit stored and computed values.

The actual checksum helper remains controlled, so checksum semantics are not established. No canonical acceptance or coverage change is made.
