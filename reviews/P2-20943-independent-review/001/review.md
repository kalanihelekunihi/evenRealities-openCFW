# P2-20943 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 148 bytes at 0x47DFEC..0x47E080. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The first entry uses an 88-byte frame, reads the flag byte, and bypasses aggregation with zero if already set. Otherwise it invokes 474A76 and DF8A, increments the global counter word with 32-bit wrap, then calls DEB4; any nonzero full result exits directly. SP0 uses a signed `<1` test. On the nonnegative path, a fresh global load is compared unsigned with `SP8+1`; the global increments only when its observed value is below that threshold, with an independent SP8 reload for the store. DE0A formats from SP+12 with arguments 64 and SP8; DE7A then returns its full value. Subtracting 32 and unsigned-comparing against 32736 accepts the interval 32..32767; only then are SP8 and the full result written to globals.

The common DF28 cleanup result is retained unless it is zero, in which case the flag byte is set and R0 explicitly becomes zero. The second entry independently loads the handle word for its zero test and, when nonzero, reloads it for 4745F4 before clearing the word; the helper result is discarded and the leaf returns zero.

Frame teardown adds 80 bytes then restores R4/PC. Local initialization and helper contracts remain unresolved. Candidate stays partial/unaccepted; no source or gate files changed.
