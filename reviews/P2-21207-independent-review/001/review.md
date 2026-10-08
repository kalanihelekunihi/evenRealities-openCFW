# P2-21207 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481B08..0x481BB8 (176 bytes); instruction and literal-reference outputs match. The second body pointer is formed by adding SP20 and SP32; SP36 is the full loop count. Body callbacks post-increment the byte pointer, preserve their full result in SP16, update SP52, and reload/store callback state at the recorded point. Trailing padding stores byte 48 unconditionally and only calls 482684 for positive signed counts. The later bit-2 flag path similarly writes a space, then conditionally repeats callbacks using signed R5. The null-string arm uses ADR 0x4826E4. For nonnull strings, negative precision calls 44A43C while nonnegative precision calls 4D40E0; the code stores either the full helper result minus the original pointer or the precision value, depending on that helper's result. Helper semantics remain unresolved.
